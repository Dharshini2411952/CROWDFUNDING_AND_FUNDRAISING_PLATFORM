"""
verify_phase19.py
Phase 19 - Final Integration + Security Hardening Verification
"""
import sys
import os
import uuid
import datetime
import requests

BASE_URL = "http://127.0.0.1:8000"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.models.saved_campaign import SavedCampaign
from app.models.comment import Comment
from app.core.security import create_access_token, hash_password

PASS = "PASSED"
FAIL = "FAILED"
failures = []

def assert_eq(label, actual, expected):
    if actual != expected:
        print(f"  {FAIL}: {label} -- expected {expected}, got {actual}")
        failures.append(label)
        return False
    print(f"  {PASS}: {label}")
    return True

def assert_true(label, condition, detail=""):
    if not condition:
        print(f"  {FAIL}: {label}" + (f" -- {detail}" if detail else ""))
        failures.append(label)
        return False
    print(f"  {PASS}: {label}")
    return True

def h(token):
    return {"Authorization": f"Bearer {token}"}

def setup_users(db):
    uid = uuid.uuid4().hex[:6]
    hashed = hash_password("TestPass@123")
    donor = User(email=f"p19_donor_{uid}@test.com", name=f"P19 Donor {uid}", password=hashed, role="DONOR", is_active=True)
    donor2 = User(email=f"p19_donor2_{uid}@test.com", name=f"P19 Donor2 {uid}", password=hashed, role="DONOR", is_active=True)
    campaigner = User(email=f"p19_camp_{uid}@test.com", name=f"P19 Campaigner {uid}", password=hashed, role="CAMPAIGNER", is_active=True)
    campaigner2 = User(email=f"p19_camp2_{uid}@test.com", name=f"P19 Campaigner2 {uid}", password=hashed, role="CAMPAIGNER", is_active=True)
    admin = User(email=f"p19_admin_{uid}@test.com", name=f"P19 Admin {uid}", password=hashed, role="ADMIN", is_active=True)
    db.add_all([donor, donor2, campaigner, campaigner2, admin])
    db.commit()
    for u in [donor, donor2, campaigner, campaigner2, admin]:
        db.refresh(u)
    return donor, donor2, campaigner, campaigner2, admin

def make_active_campaign(db, creator_id, title="P19 Active"):
    camp = Campaign(title=title, description="P19 test", goal_amount=5000.0, collected_amount=0.0,
                    category="Education", status="ACTIVE", creator_id=creator_id,
                    start_date=datetime.date.today(), end_date=datetime.date.today() + datetime.timedelta(days=30))
    db.add(camp); db.commit(); db.refresh(camp)
    return camp

def make_pending_campaign(db, creator_id, title="P19 Pending"):
    camp = Campaign(title=title, description="P19 pending test", goal_amount=1000.0, collected_amount=0.0,
                    category="Health", status="PENDING", creator_id=creator_id,
                    start_date=datetime.date.today(), end_date=datetime.date.today() + datetime.timedelta(days=14))
    db.add(camp); db.commit(); db.refresh(camp)
    return camp

def run_all():
    print("="*70)
    print("PHASE 19 - FINAL INTEGRATION + SECURITY HARDENING VERIFICATION")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    db = SessionLocal()
    try:
        print("\n[SETUP] Creating test users and campaigns...")
        donor, donor2, campaigner, campaigner2, admin = setup_users(db)
        active_campaign = make_active_campaign(db, campaigner.user_id, "P19 Active Campaign")
        pending_campaign = make_pending_campaign(db, campaigner.user_id, "P19 Pending Campaign")
        camp2 = make_active_campaign(db, campaigner2.user_id, "P19 Camp Owned By Camp2")
        print(f"  donor={donor.email}, campaigner={campaigner.email}, admin={admin.email}")

        donor_token   = create_access_token(donor.user_id, donor.role)
        donor2_token  = create_access_token(donor2.user_id, donor2.role)
        camp_token    = create_access_token(campaigner.user_id, campaigner.role)
        camp2_token   = create_access_token(campaigner2.user_id, campaigner2.role)
        admin_token   = create_access_token(admin.user_id, admin.role)

        # ====================================================
        # SECTION 22 ACCEPTANCE CRITERIA
        # ====================================================
        print("\n" + "="*60)
        print("SECTION 22 -- ACCEPTANCE CRITERIA")
        print("="*60)

        print("\n--- AC-01: Backend Is Running ---")
        r = requests.get(f"{BASE_URL}/")
        assert_eq("AC-01: Backend root returns 200", r.status_code, 200)

        print("\n--- AC-02: Database Tables Exist ---")
        from sqlalchemy import inspect as sa_inspect
        from app.core.database import engine
        insp = sa_inspect(engine)
        existing = insp.get_table_names()
        for t in ["users", "campaigns", "donations", "transactions", "comments", "notifications", "saved_campaigns", "audit_logs"]:
            assert_true(f"AC-02: Table '{t}' exists", t in existing)

        print("\n--- AC-03: GET /campaigns/ Is Public ---")
        r = requests.get(f"{BASE_URL}/campaigns/")
        assert_eq("AC-03: Public campaigns 200", r.status_code, 200)

        print("\n--- AC-04: Auth Endpoints Work ---")
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": "notexist@x.com", "password": "wrong"})
        assert_eq("AC-04: Login with bad creds returns 401", r.status_code, 401)

        print("\n--- AC-06: SECRET_KEY from Environment ---")
        assert_true("AC-06: SECRET_KEY set", bool(os.getenv("SECRET_KEY")))

        # ====================================================
        # SECTION 20A -- DONOR FLOW
        # ====================================================
        print("\n" + "="*60)
        print("SECTION 20A -- DONOR END-TO-END FLOW")
        print("="*60)

        print("\n--- 20A-1: Browse Campaigns ---")
        r = requests.get(f"{BASE_URL}/campaigns/", params={"page": 1, "page_size": 10})
        assert_eq("Browse campaigns 200", r.status_code, 200)
        assert_true("Response has 'items'", "items" in r.json())

        print("\n--- 20A-2: Open Campaign Detail ---")
        r = requests.get(f"{BASE_URL}/campaigns/{active_campaign.campaign_id}")
        assert_eq("Campaign detail 200", r.status_code, 200)
        assert_eq("Campaign ID matches", r.json()["campaign_id"], active_campaign.campaign_id)

        print("\n--- 20A-3: Save Campaign ---")
        r = requests.post(f"{BASE_URL}/saved-campaigns/{active_campaign.campaign_id}", headers=h(donor_token))
        assert_eq("Save campaign 201", r.status_code, 201)

        print("\n--- 20A-4: List Saved Campaigns ---")
        r = requests.get(f"{BASE_URL}/saved-campaigns/", headers=h(donor_token))
        assert_eq("Get saved campaigns 200", r.status_code, 200)
        ids = [s["campaign"]["campaign_id"] for s in r.json().get("data", [])]
        assert_true("Saved campaign in list", active_campaign.campaign_id in ids)

        print("\n--- 20A-5: Post Comment ---")
        r = requests.post(f"{BASE_URL}/comments/",
                          json={"campaign_id": active_campaign.campaign_id, "comment_text": "Great campaign P19!"},
                          headers=h(donor_token))
        assert_eq("Post comment 201", r.status_code, 201)
        comment_id = r.json()["comment_id"]

        print("\n--- 20A-6: Get Comments ---")
        r = requests.get(f"{BASE_URL}/comments/{active_campaign.campaign_id}")
        assert_eq("Get comments 200", r.status_code, 200)
        assert_true("Comment in list", any(c["comment_id"] == comment_id for c in r.json()))

        print("\n--- 20A-7: Donate ---")
        r = requests.post(f"{BASE_URL}/donations/",
                          json={"campaign_id": active_campaign.campaign_id, "amount": 250.0},
                          headers=h(donor_token))
        assert_eq("Donate 200", r.status_code, 200)
        donation_id = r.json()["donation_id"]
        assert_eq("Donation payment_status=SUCCESS", r.json().get("payment_status"), "SUCCESS")

        print("\n--- 20A-8: Donation History ---")
        r = requests.get(f"{BASE_URL}/donations/my", headers=h(donor_token))
        assert_eq("My donations 200", r.status_code, 200)
        assert_true("Donation in history", any(d["donation_id"] == donation_id for d in r.json()))

        print("\n--- 20A-9: Notifications ---")
        r = requests.get(f"{BASE_URL}/notifications/", headers=h(donor_token))
        assert_eq("Notifications 200", r.status_code, 200)
        types = [n.get("notification_type") for n in r.json()]
        assert_true("DONATION_SUCCESS notification", "DONATION_SUCCESS" in types, f"types: {types}")

        print("\n--- 20A-10: Logout (unauthenticated blocked) ---")
        r = requests.get(f"{BASE_URL}/donations/my")
        assert_true("Unauthenticated blocked", r.status_code in [401, 403])

        # ====================================================
        # SECTION 20B -- CAMPAIGNER FLOW
        # ====================================================
        print("\n" + "="*60)
        print("SECTION 20B -- CAMPAIGNER END-TO-END FLOW")
        print("="*60)

        print("\n--- 20B-1: Create Campaign ---")
        r = requests.post(f"{BASE_URL}/campaigns/",
                          json={"title": "P19 Fundraiser", "description": "Testing campaigner flow",
                                "goal_amount": 3000.0, "category": "Technology",
                                "start_date": str(datetime.date.today()),
                                "end_date": str(datetime.date.today() + datetime.timedelta(days=21))},
                          headers=h(camp_token))
        assert_eq("Create campaign 200", r.status_code, 200)
        new_camp_id = r.json()["campaign_id"]

        print("\n--- 20B-2: Verify PENDING Status ---")
        assert_eq("New campaign is PENDING", r.json().get("status"), "PENDING")

        print("\n--- 20B-3: Admin Approves ---")
        r = requests.patch(f"{BASE_URL}/admin/campaigns/{new_camp_id}/approve", headers=h(admin_token))
        assert_eq("Admin approve 200", r.status_code, 200)

        print("\n--- 20B-4: Campaign Now ACTIVE ---")
        r = requests.get(f"{BASE_URL}/campaigns/{new_camp_id}")
        assert_eq("Campaign ACTIVE", r.json().get("status"), "ACTIVE")

        print("\n--- 20B-5: Approval Notification ---")
        r = requests.get(f"{BASE_URL}/notifications/", headers=h(camp_token))
        assert_eq("Notifications 200", r.status_code, 200)
        types = [n.get("notification_type") for n in r.json()]
        assert_true("CAMPAIGN_APPROVED notification", "CAMPAIGN_APPROVED" in types, f"types: {types}")

        print("\n--- 20B-6: View Campaign Activity ---")
        r = requests.get(f"{BASE_URL}/donations/received", headers=h(camp_token))
        assert_eq("Received donations 200", r.status_code, 200)

        # ====================================================
        # SECTION 20C -- ADMIN FLOW
        # ====================================================
        print("\n" + "="*60)
        print("SECTION 20C -- ADMIN END-TO-END FLOW")
        print("="*60)

        print("\n--- 20C-1 & 20C-2: Admin Reports ---")
        r = requests.get(f"{BASE_URL}/admin/reports", headers=h(admin_token))
        assert_eq("Admin reports 200", r.status_code, 200)
        d = r.json()["data"]
        for key in ["total_users", "total_campaigns", "total_donations", "total_amount_raised", "campaigns_by_category"]:
            assert_true(f"Reports has '{key}'", key in d)
        print(f"  Stats: Users={d['total_users']}, Campaigns={d['total_campaigns']}, Donations={d['total_donations']}")

        print("\n--- 20C-3: View Users ---")
        r = requests.get(f"{BASE_URL}/admin/users", headers=h(admin_token))
        assert_eq("Admin users 200", r.status_code, 200)
        assert_true("Donor in user list", any(u["user_id"] == donor.user_id for u in r.json()))

        print("\n--- 20C-4: Deactivate User ---")
        r = requests.patch(f"{BASE_URL}/admin/users/{donor.user_id}/deactivate", headers=h(admin_token))
        assert_eq("Deactivate 200", r.status_code, 200)
        assert_eq("is_active=False", r.json()["is_active"], False)

        print("\n--- 20C-5: Deactivated User Blocked ---")
        r = requests.get(f"{BASE_URL}/donations/my", headers=h(donor_token))
        assert_eq("Deactivated user gets 401", r.status_code, 401)
        assert_true("Error mentions deactivated", "deactivated" in r.json().get("detail","").lower(), r.json().get("detail"))

        print("\n--- 20C-6: Activate User ---")
        r = requests.patch(f"{BASE_URL}/admin/users/{donor.user_id}/activate", headers=h(admin_token))
        assert_eq("Activate 200", r.status_code, 200)
        assert_eq("is_active=True", r.json()["is_active"], True)

        print("\n--- 20C-7: View All Campaigns ---")
        r = requests.get(f"{BASE_URL}/admin/campaigns", headers=h(admin_token))
        assert_eq("Admin campaigns 200", r.status_code, 200)
        assert_true("Pending campaign in list", any(c["campaign_id"] == pending_campaign.campaign_id for c in r.json()))

        print("\n--- 20C-8: Reject Campaign ---")
        r = requests.patch(f"{BASE_URL}/admin/campaigns/{pending_campaign.campaign_id}/reject", headers=h(admin_token))
        assert_eq("Reject 200", r.status_code, 200)

        print("\n--- 20C-9: View Donations ---")
        r = requests.get(f"{BASE_URL}/admin/donations", headers=h(admin_token))
        assert_eq("Admin donations 200", r.status_code, 200)

        print("\n--- 20C-10: View Transactions ---")
        r = requests.get(f"{BASE_URL}/admin/transactions", headers=h(admin_token))
        assert_eq("Admin transactions 200", r.status_code, 200)

        print("\n--- 20C-11: View Audit Logs ---")
        r = requests.get(f"{BASE_URL}/admin/audit-logs", headers=h(admin_token))
        assert_eq("Audit logs 200", r.status_code, 200)
        actions = [l["action"] for l in r.json()]
        assert_true("CAMPAIGN_REJECTED in audit logs", "CAMPAIGN_REJECTED" in actions, f"actions: {set(actions)}")

        print("\n--- 20C-12: Admin Notifications ---")
        r = requests.get(f"{BASE_URL}/notifications/", headers=h(admin_token))
        assert_eq("Admin notifications 200", r.status_code, 200)

        # ====================================================
        # SECTION 21 -- SECURITY NEGATIVE TESTS
        # ====================================================
        print("\n" + "="*60)
        print("SECTION 21 -- SECURITY NEGATIVE TESTS (12 tests)")
        print("="*60)

        print("\n--- SEC-01: Donor -> admin/reports = 403 ---")
        r = requests.get(f"{BASE_URL}/admin/reports", headers=h(donor_token))
        assert_eq("SEC-01: Donor -> admin = 403", r.status_code, 403)

        print("\n--- SEC-02: Campaigner -> admin/reports = 403 ---")
        r = requests.get(f"{BASE_URL}/admin/reports", headers=h(camp_token))
        assert_eq("SEC-02: Campaigner -> admin = 403", r.status_code, 403)

        print("\n--- SEC-03: Donor -> Campaign Creation = 403 ---")
        r = requests.post(f"{BASE_URL}/campaigns/",
                          json={"title": "Donor Hack Attempt", "description": "Trying to create as donor",
                                "goal_amount": 100.0, "category": "Other",
                                "start_date": str(datetime.date.today()),
                                "end_date": str(datetime.date.today() + datetime.timedelta(days=7))},
                          headers=h(donor_token))
        assert_eq("SEC-03: Donor create campaign = 403", r.status_code, 403)

        print("\n--- SEC-04: Campaigner -> Other's Campaign Modify = 403 ---")
        r = requests.put(f"{BASE_URL}/campaigns/{camp2.campaign_id}",
                         json={"title": "Hacked"},
                         headers=h(camp_token))
        assert_eq("SEC-04: Campaigner -> other campaign PUT = 403", r.status_code, 403)

        print("\n--- SEC-05: No Token -> Protected = 401/403 ---")
        r = requests.get(f"{BASE_URL}/donations/my")
        assert_true("SEC-05: No token = 401 or 403", r.status_code in [401, 403])

        print("\n--- SEC-06: Invalid JWT -> Protected = 401 ---")
        r = requests.get(f"{BASE_URL}/donations/my",
                         headers={"Authorization": "Bearer thisisaninvalidjwt.notreal.ever"})
        assert_eq("SEC-06: Invalid JWT = 401", r.status_code, 401)

        print("\n--- SEC-07: Saved Campaigns Scoped to JWT User ---")
        r1 = requests.post(f"{BASE_URL}/saved-campaigns/{active_campaign.campaign_id}", headers=h(donor2_token))
        assert_true("SEC-07a: Donor2 saves campaign", r1.status_code in [201, 409])
        r2 = requests.delete(f"{BASE_URL}/saved-campaigns/{active_campaign.campaign_id}", headers=h(donor_token))
        assert_true("SEC-07b: Saved campaigns scoped to user", r2.status_code in [204, 404])

        print("\n--- SEC-08: Admin Self-Deactivation = 400 ---")
        r = requests.patch(f"{BASE_URL}/admin/users/{admin.user_id}/deactivate", headers=h(admin_token))
        assert_eq("SEC-08: Self-deactivate = 400", r.status_code, 400)

        print("\n--- SEC-09a: Donation Amount=0 -> 400 ---")
        r = requests.post(f"{BASE_URL}/donations/",
                          json={"campaign_id": active_campaign.campaign_id, "amount": 0},
                          headers=h(donor_token))
        assert_eq("SEC-09a: Amount=0 = 400", r.status_code, 400)

        print("\n--- SEC-09b: Donation Amount=-50 -> 400 ---")
        r = requests.post(f"{BASE_URL}/donations/",
                          json={"campaign_id": active_campaign.campaign_id, "amount": -50},
                          headers=h(donor_token))
        assert_eq("SEC-09b: Amount=-50 = 400", r.status_code, 400)

        print("\n--- SEC-10: Duplicate Save -> 409 ---")
        fresh_camp = make_active_campaign(db, campaigner.user_id, "P19 Dup Save Test Camp")
        r1 = requests.post(f"{BASE_URL}/saved-campaigns/{fresh_camp.campaign_id}", headers=h(donor_token))
        assert_eq("SEC-10a: First save = 201", r1.status_code, 201)
        r2 = requests.post(f"{BASE_URL}/saved-campaigns/{fresh_camp.campaign_id}", headers=h(donor_token))
        assert_eq("SEC-10b: Duplicate save = 409", r2.status_code, 409)

        print("\n--- SEC-11: Donor Edits Other User's Comment -> 403 ---")
        r_d2c = requests.post(f"{BASE_URL}/comments/",
                              json={"campaign_id": active_campaign.campaign_id, "comment_text": "Donor2 comment"},
                              headers=h(donor2_token))
        assert_eq("SEC-11a: Donor2 posts comment = 201", r_d2c.status_code, 201)
        d2_cid = r_d2c.json()["comment_id"]
        r = requests.put(f"{BASE_URL}/comments/{d2_cid}",
                         json={"comment_text": "Hacked!"},
                         headers=h(donor_token))
        assert_eq("SEC-11b: Edit other's comment = 403", r.status_code, 403)
        r = requests.delete(f"{BASE_URL}/comments/{d2_cid}", headers=h(donor_token))
        assert_eq("SEC-11c: Delete other's comment = 403", r.status_code, 403)

        print("\n--- SEC-12: Deactivated User (with valid token) -> 401 ---")
        requests.patch(f"{BASE_URL}/admin/users/{donor2.user_id}/deactivate", headers=h(admin_token))
        fresh_deactivated_token = create_access_token(donor2.user_id, donor2.role)
        r = requests.get(f"{BASE_URL}/donations/my", headers=h(fresh_deactivated_token))
        assert_eq("SEC-12: Deactivated user = 401", r.status_code, 401)
        assert_true("SEC-12: Detail mentions deactivated", "deactivated" in r.json().get("detail","").lower(), r.json().get("detail"))
        requests.patch(f"{BASE_URL}/admin/users/{donor2.user_id}/activate", headers=h(admin_token))

    finally:
        db.close()

    print("\n" + "="*70)
    if failures:
        print(f"PHASE 19 VERIFICATION FAILED: {len(failures)} test(s) failed")
        for f in failures:
            print(f"  FAIL: {f}")
        sys.exit(1)
    else:
        print("ALL PHASE 19 TESTS PASSED SUCCESSFULLY!")
        print("  Section 20A: Donor End-to-End Flow            -- PASSED")
        print("  Section 20B: Campaigner End-to-End Flow       -- PASSED")
        print("  Section 20C: Admin End-to-End Flow            -- PASSED")
        print("  Section 21:  12 Security Negative Tests       -- PASSED")
        print("  Section 22:  Acceptance Criteria              -- PASSED")
    print("="*70)

if __name__ == "__main__":
    run_all()
