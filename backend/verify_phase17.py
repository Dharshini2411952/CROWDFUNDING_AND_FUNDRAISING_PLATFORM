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
    print("=" * 70)
    print("RUNNING PHASE 17 ENGAGEMENT & INTERACTIVITY VERIFICATION")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Create test users
        donor_email = f"p17_donor_{uuid.uuid4().hex[:6]}@test.com"
        donor = User(
            email=donor_email,
            name="Phase17 Donor",
            password="hashedpassword123",
            role="DONOR",
        )
        donor2_email = f"p17_donor2_{uuid.uuid4().hex[:6]}@test.com"
        donor2 = User(
            email=donor2_email,
            name="Phase17 Donor2",
            password="hashedpassword123",
            role="DONOR",
        )
        campaigner_email = f"p17_camp_{uuid.uuid4().hex[:6]}@test.com"
        campaigner = User(
            email=campaigner_email,
            name="Phase17 Campaigner",
            password="hashedpassword123",
            role="CAMPAIGNER",
        )
        admin_email = f"p17_admin_{uuid.uuid4().hex[:6]}@test.com"
        admin = User(
            email=admin_email,
            name="Phase17 Admin",
            password="hashedpassword123",
            role="ADMIN",
        )
        db.add_all([donor, donor2, campaigner, admin])
        db.commit()
        for u in [donor, donor2, campaigner, admin]:
            db.refresh(u)

        donor_token = create_access_token(donor.user_id, donor.role)
        donor2_token = create_access_token(donor2.user_id, donor2.role)
        campaigner_token = create_access_token(campaigner.user_id, campaigner.role)
        admin_token = create_access_token(admin.user_id, admin.role)

        headers_donor = {"Authorization": f"Bearer {donor_token}"}
        headers_donor2 = {"Authorization": f"Bearer {donor2_token}"}
        headers_camp = {"Authorization": f"Bearer {campaigner_token}"}
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        # Create a test campaign
        campaign = Campaign(
            title="Phase 17 Test Campaign",
            description="Testing saved campaigns, comments, notifications",
            goal_amount=1000.0,
            collected_amount=0.0,
            category="Education",
            status="APPROVED",
            creator_id=campaigner.user_id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30),
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        cid = campaign.campaign_id

        # -------------------------------------------------------------
        # Test 1: Save Campaign
        # -------------------------------------------------------------
        print("\n--- Test 1: Save Campaign ---")
        res = requests.post(f"{BASE_URL}/saved-campaigns/{cid}", headers=headers_donor)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        print("PASSED: Campaign saved successfully (201).")

        # -------------------------------------------------------------
        # Test 2: Duplicate Save Returns 409
        # -------------------------------------------------------------
        print("\n--- Test 2: Duplicate Save (409) ---")
        res = requests.post(f"{BASE_URL}/saved-campaigns/{cid}", headers=headers_donor)
        assert res.status_code == 409, f"Expected 409, got {res.status_code}: {res.text}"
        print("PASSED: Duplicate save correctly returned 409 Conflict.")

        # -------------------------------------------------------------
        # Test 3: Get Saved Campaigns (Persistence Check)
        # -------------------------------------------------------------
        print("\n--- Test 3: Get Saved Campaigns ---")
        res = requests.get(f"{BASE_URL}/saved-campaigns/", headers=headers_donor)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        saved_items = res.json().get("data", [])
        assert any(item["campaign"]["campaign_id"] == cid for item in saved_items), "Saved campaign not found in GET response"
        print("PASSED: Saved campaign retrieved cleanly.")

        # -------------------------------------------------------------
        # Test 4: Unsave Campaign
        # -------------------------------------------------------------
        print("\n--- Test 4: Unsave Campaign ---")
        res = requests.delete(f"{BASE_URL}/saved-campaigns/{cid}", headers=headers_donor)
        assert res.status_code in [200, 204], f"Expected 204, got {res.status_code}: {res.text}"
        res = requests.get(f"{BASE_URL}/saved-campaigns/", headers=headers_donor)
        saved_items = res.json().get("data", [])
        assert not any(item["campaign"]["campaign_id"] == cid for item in saved_items), "Campaign still found after unsaving"
        print("PASSED: Campaign unsaved successfully.")

        # -------------------------------------------------------------
        # Test 5: Comment Creation
        # -------------------------------------------------------------
        print("\n--- Test 5: Comment Create ---")
        comment_payload = {"campaign_id": cid, "comment_text": "Great cause! Happy to support."}
        res = requests.post(f"{BASE_URL}/comments/", json=comment_payload, headers=headers_donor)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        comment_data = res.json()
        comment_id = comment_data["comment_id"]
        assert comment_data["comment_text"] == "Great cause! Happy to support."
        print(f"PASSED: Comment created (ID={comment_id}).")

        # -------------------------------------------------------------
        # Test 6: Comment Edit (Owner allowed)
        # -------------------------------------------------------------
        print("\n--- Test 6: Comment Edit (Owner) ---")
        update_payload = {"comment_text": "Updated comment: Truly inspiring campaign!"}
        res = requests.put(f"{BASE_URL}/comments/{comment_id}", json=update_payload, headers=headers_donor)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        assert res.json()["comment_text"] == "Updated comment: Truly inspiring campaign!"
        print("PASSED: Owner updated comment successfully.")

        # -------------------------------------------------------------
        # Test 7: Comment Edit / Delete Unauthorized (Donor 2 -> 403)
        # -------------------------------------------------------------
        print("\n--- Test 7: Comment Edit/Delete Unauthorized (403) ---")
        res = requests.put(f"{BASE_URL}/comments/{comment_id}", json={"comment_text": "Hacked text"}, headers=headers_donor2)
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        res = requests.delete(f"{BASE_URL}/comments/{comment_id}", headers=headers_donor2)
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        print("PASSED: Unauthorized edit/delete rejected with 403 Forbidden.")

        # -------------------------------------------------------------
        # Test 8: Comment Delete (Owner)
        # -------------------------------------------------------------
        print("\n--- Test 8: Comment Delete (Owner) ---")
        res = requests.delete(f"{BASE_URL}/comments/{comment_id}", headers=headers_donor)
        assert res.status_code in [200, 204], f"Expected 200/204, got {res.status_code}: {res.text}"
        print("PASSED: Owner deleted comment successfully.")

        # -------------------------------------------------------------
        # Test 9: Notifications (Creation & Retrieval)
        # -------------------------------------------------------------
        print("\n--- Test 9: Notifications Retrieval & Unread Count ---")
        # Create a test notification directly or via API action
        test_notif = Notification(
            user_id=donor.user_id,
            title="Welcome to Phase 17",
            message="Your account is ready.",
            notification_type="SYSTEM",
            is_read=False
        )
        db.add(test_notif)
        db.commit()
        db.refresh(test_notif)
        nid = test_notif.notification_id

        res = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers_donor)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        unread_count = res.json().get("unread_count", 0)
        assert unread_count >= 1, f"Expected unread_count >= 1, got {unread_count}"
        print(f"PASSED: Unread notification count = {unread_count}.")

        # -------------------------------------------------------------
        # Test 10: Mark Notification as Read
        # -------------------------------------------------------------
        print("\n--- Test 10: Mark Notification Read ---")
        res = requests.patch(f"{BASE_URL}/notifications/{nid}/read", headers=headers_donor)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert res.json()["is_read"] == True
        print("PASSED: Marked notification as read.")

        # -------------------------------------------------------------
        # Test 11: Mark All Notifications Read
        # -------------------------------------------------------------
        print("\n--- Test 11: Mark All Notifications Read ---")
        res = requests.patch(f"{BASE_URL}/notifications/read-all", headers=headers_donor)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        res = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers_donor)
        assert res.json().get("unread_count") == 0
        print("PASSED: Mark all notifications read verified.")

        # -------------------------------------------------------------
        # Test 12: Campaign Approval Notification
        # -------------------------------------------------------------
        print("\n--- Test 12: Campaign Approval Notification ---")
        pending_campaign = Campaign(
            title="Pending Approval Campaign",
            description="Testing approval notification",
            goal_amount=500.0,
            collected_amount=0.0,
            category="Health",
            status="PENDING",
            creator_id=campaigner.user_id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=15),
        )
        db.add(pending_campaign)
        db.commit()
        db.refresh(pending_campaign)

        res = requests.patch(f"{BASE_URL}/admin/campaigns/{pending_campaign.campaign_id}/approve", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        # Check campaigner notifications
        res_notif = requests.get(f"{BASE_URL}/notifications/", headers=headers_camp)
        assert any("Approved" in n["title"] or "APPROVED" in n["message"] for n in res_notif.json()), "Approval notification not found"
        print("PASSED: Campaign approval notification generated and verified.")

        # -------------------------------------------------------------
        # Test 13: Donation & Goal Completion Notification
        # -------------------------------------------------------------
        print("\n--- Test 13: Donation & Goal Completion Notification ---")
        pay_res = requests.post(f"{BASE_URL}/payments/create", json={"campaign_id": pending_campaign.campaign_id, "amount": 500.0}, headers=headers_donor)
        assert pay_res.status_code == 200, f"Expected 200 for payment create, got {pay_res.status_code}: {pay_res.text}"
        ref = pay_res.json()["data"]["payment_reference"]

        verify_res = requests.post(f"{BASE_URL}/payments/verify", json={"payment_reference": ref, "campaign_id": pending_campaign.campaign_id, "amount": 500.0}, headers=headers_donor)
        assert verify_res.status_code == 200, f"Expected 200 for payment verify, got {verify_res.status_code}: {verify_res.text}"

        res_donor_notif = requests.get(f"{BASE_URL}/notifications/", headers=headers_donor)
        donor_notifs = res_donor_notif.json()
        assert any("Donation" in n["title"] or "Goal" in n["title"] for n in donor_notifs), f"Donation notification for donor not found"

        res_camp_notif = requests.get(f"{BASE_URL}/notifications/", headers=headers_camp)
        assert any("Goal Reached" in n["title"] or "Donation Received" in n["title"] for n in res_camp_notif.json()), "Goal completion notification for campaigner not found"
        print("PASSED: Donation and Goal Completion notifications verified.")

        print("\n" + "=" * 70)
        print("ALL PHASE 17 VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
