import sys
import os
import uuid
import datetime
import requests

BASE_URL = "http://127.0.0.1:8000"

from app.core.database import SessionLocal
from app.models.user import User
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.models.transaction import Transaction
from app.models.notification import Notification
from app.core.security import create_access_token

def run_tests():
    print("=" * 60)
    print("RUNNING PHASE 16 PAYMENT SAFETY & GOAL COMPLETION VERIFICATION")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Create test donor user
        donor_email = f"phase16_donor_{uuid.uuid4().hex[:6]}@test.com"
        donor = User(
            email=donor_email,
            name="Phase 16 Donor",
            password="hashedpassword123",
            role="DONOR",
        )
        # Create test campaigner user
        campaigner_email = f"phase16_camp_{uuid.uuid4().hex[:6]}@test.com"
        campaigner = User(
            email=campaigner_email,
            name="Phase 16 Campaigner",
            password="hashedpassword123",
            role="CAMPAIGNER",
        )
        db.add(donor)
        db.add(campaigner)
        db.commit()
        db.refresh(donor)
        db.refresh(campaigner)

        donor_id = donor.user_id
        campaigner_id = campaigner.user_id

        donor_token = create_access_token(donor_id, donor.role)
        headers = {"Authorization": f"Bearer {donor_token}"}

        # -------------------------------------------------------------
        # Test 1: Invalid amount validation (amount <= 0)
        # -------------------------------------------------------------
        print("\n--- Test 1: Invalid Amount (<= 0) ---")
        res = requests.post(f"{BASE_URL}/payments/create", json={"campaign_id": 9999, "amount": 0}, headers=headers)
        assert res.status_code == 400, f"Expected 400 for amount=0, got {res.status_code}: {res.text}"
        res = requests.post(f"{BASE_URL}/payments/verify", json={"payment_reference": "REF-123", "campaign_id": 9999, "amount": -50}, headers=headers)
        assert res.status_code == 400, f"Expected 400 for negative amount, got {res.status_code}: {res.text}"
        print("PASSED: Invalid amount correctly rejected with 400.")

        # -------------------------------------------------------------
        # Test 2: Non-existent campaign validation
        # -------------------------------------------------------------
        print("\n--- Test 2: Non-Existent Campaign ---")
        res = requests.post(f"{BASE_URL}/payments/create", json={"campaign_id": 999999, "amount": 100}, headers=headers)
        assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"
        print("PASSED: Non-existent campaign returned 404.")

        # -------------------------------------------------------------
        # Test 3: Active Campaign Creation for tests
        # -------------------------------------------------------------
        active_campaign = Campaign(
            title="Active Test Campaign",
            description="Testing payment safety",
            goal_amount=1000.0,
            collected_amount=0.0,
            category="Medical",
            status="ACTIVE",
            creator_id=campaigner.user_id
        )
        db.add(active_campaign)
        db.commit()
        db.refresh(active_campaign)
        camp_id = active_campaign.campaign_id

        # -------------------------------------------------------------
        # Test 4: Successful Payment & Donation Consistency
        # -------------------------------------------------------------
        print("\n--- Test 4: Successful Payment Verification ---")
        create_res = requests.post(f"{BASE_URL}/payments/create", json={"campaign_id": camp_id, "amount": 300.0}, headers=headers)
        assert create_res.status_code == 200, f"Create payment failed: {create_res.text}"
        pref1 = create_res.json()["data"]["payment_reference"]

        verify_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref1,
            "campaign_id": camp_id,
            "amount": 300.0,
            "status": "SUCCESS"
        }, headers=headers)
        assert verify_res.status_code == 200, f"Verify payment failed: {verify_res.text}"
        data = verify_res.json()["data"]
        assert data["collected_amount"] == 300.0, f"Expected collected 300.0, got {data['collected_amount']}"
        assert data["campaign_status"] == "ACTIVE", f"Expected ACTIVE, got {data['campaign_status']}"

        # Verify DB records
        db.close()
        db = SessionLocal()
        don = db.query(Donation).filter(Donation.donation_id == data["donation_id"]).first()
        tx = db.query(Transaction).filter(Transaction.transaction_id == data["transaction_id"]).first()
        assert don is not None and (don.status == "SUCCESS" or don.payment_status == "SUCCESS"), f"Donation record missing or status={getattr(don, 'status', None)}"
        assert tx is not None and tx.payment_reference == pref1, "Transaction record missing or reference mismatch"
        print(f"PASSED: Exactly 1 donation (ID {don.donation_id}) & 1 transaction (ID {tx.transaction_id}) created. Collected: {data['collected_amount']}")

        # -------------------------------------------------------------
        # Test 5: Duplicate Payment Attempt (Idempotency)
        # -------------------------------------------------------------
        print("\n--- Test 5: Duplicate Payment Reference (Idempotency) ---")
        dup_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref1,
            "campaign_id": camp_id,
            "amount": 300.0,
            "status": "SUCCESS"
        }, headers=headers)
        assert dup_res.status_code == 409, f"Expected 409 Conflict for duplicate payment reference, got {dup_res.status_code}: {dup_res.text}"
        print("PASSED: Duplicate payment reference rejected with 409 Conflict.")

        # -------------------------------------------------------------
        # Test 6: Failed Payment Handling
        # -------------------------------------------------------------
        print("\n--- Test 6: Failed Payment Handling ---")
        pref_fail = f"PAY-FAIL-{uuid.uuid4().hex[:8]}"
        fail_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref_fail,
            "campaign_id": camp_id,
            "amount": 200.0,
            "status": "FAILED"
        }, headers=headers)
        assert fail_res.status_code == 400, f"Expected 400 for failed payment, got {fail_res.status_code}: {fail_res.text}"

        # Confirm campaign total did NOT increase
        db.close()
        db = SessionLocal()
        cur_camp = db.query(Campaign).filter(Campaign.campaign_id == camp_id).first()
        assert cur_camp.collected_amount == 300.0, f"Campaign collected amount changed after failed payment! Got {cur_camp.collected_amount}"

        # Confirm failed transaction recorded
        failed_tx = db.query(Transaction).filter(Transaction.payment_reference == pref_fail).first()
        assert failed_tx is not None and failed_tx.status == "FAILED", "Failed transaction not recorded properly"

        # Confirm PAYMENT_FAILED notification dispatched
        fail_notif = db.query(Notification).filter(
            Notification.user_id == donor_id,
            Notification.notification_type == "PAYMENT_FAILED"
        ).first()
        assert fail_notif is not None, "PAYMENT_FAILED notification missing for donor"
        print("PASSED: Failed payment recorded as FAILED without altering campaign total. Notification dispatched.")

        # -------------------------------------------------------------
        # Test 7: Goal Exactly Reached Logic
        # -------------------------------------------------------------
        print("\n--- Test 7: Goal Exactly Reached (INR 300 + INR 700 = INR 1,000) ---")
        pref_goal = f"PAY-GOAL-{uuid.uuid4().hex[:8]}"
        goal_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref_goal,
            "campaign_id": camp_id,
            "amount": 700.0,
            "status": "SUCCESS"
        }, headers=headers)
        assert goal_res.status_code == 200, f"Verify payment failed: {goal_res.text}"
        gdata = goal_res.json()["data"]
        assert gdata["collected_amount"] == 1000.0, f"Expected 1000.0, got {gdata['collected_amount']}"
        assert gdata["campaign_status"] == "COMPLETED", f"Expected COMPLETED, got {gdata['campaign_status']}"

        # Confirm GOAL_REACHED notification dispatched for both campaigner and donor
        db.close()
        db = SessionLocal()
        goal_notif_camp = db.query(Notification).filter(
            Notification.user_id == campaigner_id,
            Notification.notification_type == "GOAL_REACHED"
        ).first()
        goal_notif_donor = db.query(Notification).filter(
            Notification.user_id == donor_id,
            Notification.notification_type == "GOAL_REACHED"
        ).first()
        assert goal_notif_camp is not None, "GOAL_REACHED notification missing for campaigner"
        assert goal_notif_donor is not None, "GOAL_REACHED notification missing for donor"
        print("PASSED: Goal reached! Campaign status updated to COMPLETED and notifications dispatched.")

        # -------------------------------------------------------------
        # Test 8: Attempt Donation to COMPLETED Campaign
        # -------------------------------------------------------------
        print("\n--- Test 8: Prevent Donation to COMPLETED Campaign ---")
        pref_comp = f"PAY-COMP-{uuid.uuid4().hex[:8]}"
        comp_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref_comp,
            "campaign_id": camp_id,
            "amount": 100.0,
            "status": "SUCCESS"
        }, headers=headers)
        assert comp_res.status_code == 400, f"Expected 400 for COMPLETED campaign, got {comp_res.status_code}: {comp_res.text}"
        print("PASSED: Donation to COMPLETED campaign correctly rejected with 400.")

        # -------------------------------------------------------------
        # Test 9: Expired Campaign Handling
        # -------------------------------------------------------------
        print("\n--- Test 9: Expired Campaign Handling ---")
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        expired_campaign = Campaign(
            title="Expired Test Campaign",
            description="Testing expiration logic",
            goal_amount=5000.0,
            collected_amount=0.0,
            category="Education",
            status="ACTIVE",
            creator_id=campaigner_id,
            end_date=yesterday
        )
        db.add(expired_campaign)
        db.commit()
        db.refresh(expired_campaign)
        exp_id = expired_campaign.campaign_id

        pref_exp = f"PAY-EXP-{uuid.uuid4().hex[:8]}"
        exp_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref_exp,
            "campaign_id": exp_id,
            "amount": 500.0,
            "status": "SUCCESS"
        }, headers=headers)
        assert exp_res.status_code == 400, f"Expected 400 for EXPIRED campaign, got {exp_res.status_code}: {exp_res.text}"

        db.close()
        db = SessionLocal()
        exp_camp = db.query(Campaign).filter(Campaign.campaign_id == exp_id).first()
        assert exp_camp.status == "EXPIRED", f"Expected status EXPIRED, got {exp_camp.status}"
        print("PASSED: Expired campaign marked EXPIRED and donation rejected with 400.")

        # -------------------------------------------------------------
        # Test 10: Goal Exceeded Scenario
        # -------------------------------------------------------------
        print("\n--- Test 10: Goal Exceeded Scenario ---")
        exceed_campaign = Campaign(
            title="Exceed Test Campaign",
            description="Testing goal exceeded logic",
            goal_amount=500.0,
            collected_amount=0.0,
            category="Emergency",
            status="ACTIVE",
            creator_id=campaigner_id
        )
        db.add(exceed_campaign)
        db.commit()
        db.refresh(exceed_campaign)
        exc_id = exceed_campaign.campaign_id

        pref_exc = f"PAY-EXC-{uuid.uuid4().hex[:8]}"
        exc_res = requests.post(f"{BASE_URL}/payments/verify", json={
            "payment_reference": pref_exc,
            "campaign_id": exc_id,
            "amount": 1200.0,  # Goal was 500
            "status": "SUCCESS"
        }, headers=headers)
        assert exc_res.status_code == 200, f"Verify payment failed: {exc_res.text}"
        exc_data = exc_res.json()["data"]
        assert exc_data["collected_amount"] == 1200.0, f"Expected 1200.0, got {exc_data['collected_amount']}"
        assert exc_data["campaign_status"] == "COMPLETED", f"Expected COMPLETED, got {exc_data['campaign_status']}"
        print("PASSED: Goal exceeded handled cleanly! Total collected=1200, status=COMPLETED.")

        print("\n" + "=" * 60)
        print("ALL 10 PHASE 16 PAYMENT SAFETY & GOAL LOGIC TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
