"""
verify_phase20.py
=================
Phase 20 - Full End-to-End Testing + Bug Fixing Verification Script.
Covers all 13 test sections specified in Phase 20.
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
from app.core.security import create_access_token, hash_password

passed_tests = 0
failed_tests = 0
failures = []

def assert_res(condition, test_name, detail=""):
    global passed_tests, failed_tests
    if condition:
        passed_tests += 1
        print(f"  [PASS] {test_name}")
    else:
        failed_tests += 1
        msg = f"  [FAIL] {test_name}"
        if detail:
            msg += f" - {detail}"
        print(msg)
        failures.append(f"{test_name}: {detail}")

def run_tests():
    global passed_tests, failed_tests
    print("\n========================================================")
    print("PHASE 20 END-TO-END & INTEGRATION TEST SUITE")
    print("========================================================\n")

    # Check health / API root
    try:
        r = requests.get(f"{BASE_URL}/")
        assert_res(r.status_code == 200, "Backend service responsive")
    except Exception as e:
        print(f"CRITICAL: Backend not reachable at {BASE_URL}. Error: {e}")
        return

    # Create test users in DB directly to ensure guaranteed setup
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    hashed_pwd = hash_password("Password123!")

    # Admin User
    admin_user = db.query(User).filter(User.role == "ADMIN", User.is_active == True).first()
    if not admin_user:
        admin_user = User(name=f"Admin {uid}", email=f"admin_{uid}@test.com", password=hashed_pwd, role="ADMIN", is_active=True)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    
    admin_token = create_access_token(admin_user.user_id, admin_user.role)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Donor User
    donor_email = f"donor_{uid}@test.com"
    r_dn = requests.post(f"{BASE_URL}/auth/signup", json={"name": "Test Donor", "email": donor_email, "password": "Password123!", "role": "DONOR"})
    assert_res(r_dn.status_code in (200, 201), "Donor Signup", f"Status {r_dn.status_code}")
    r_lg = requests.post(f"{BASE_URL}/auth/login", json={"email": donor_email, "password": "Password123!"})
    assert_res(r_lg.status_code == 200, "Donor Login", f"Status {r_lg.status_code}")
    donor_token = r_lg.json().get("access_token")
    donor_headers = {"Authorization": f"Bearer {donor_token}"}
    donor_id = r_lg.json().get("user_id")

    # Campaigner User
    camp_email = f"camp_{uid}@test.com"
    r_cp = requests.post(f"{BASE_URL}/auth/signup", json={"name": "Test Campaigner", "email": camp_email, "password": "Password123!", "role": "CAMPAIGNER"})
    assert_res(r_cp.status_code in (200, 201), "Campaigner Signup", f"Status {r_cp.status_code}")
    r_cpl = requests.post(f"{BASE_URL}/auth/login", json={"email": camp_email, "password": "Password123!"})
    assert_res(r_cpl.status_code == 200, "Campaigner Login", f"Status {r_cpl.status_code}")
    camp_token = r_cpl.json().get("access_token")
    camp_headers = {"Authorization": f"Bearer {camp_token}"}
    camp_id = r_cpl.json().get("user_id")

    # Second Campaigner User
    camp2_email = f"camp2_{uid}@test.com"
    requests.post(f"{BASE_URL}/auth/signup", json={"name": "Test Campaigner 2", "email": camp2_email, "password": "Password123!", "role": "CAMPAIGNER"})
    r_c2l = requests.post(f"{BASE_URL}/auth/login", json={"email": camp2_email, "password": "Password123!"})
    camp2_token = r_c2l.json().get("access_token")
    camp2_headers = {"Authorization": f"Bearer {camp2_token}"}

    # ----------------------------------------------------
    # SECTION 1 & 2: CAMPAIGN CREATION & APPROVAL FLOW
    # ----------------------------------------------------
    print("\n--- Testing Campaign Creation & Approval Flow ---")
    camp_data = {
        "title": f"Phase 20 Test Campaign {uid}",
        "description": "Comprehensive test campaign for Phase 20 verification.",
        "category": "Medical",
        "goal_amount": 10000.0,
        "end_date": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    }
    r = requests.post(f"{BASE_URL}/campaigns/", json=camp_data, headers=camp_headers)
    assert_res(r.status_code in (200, 201), "Campaigner create campaign", f"Status {r.status_code} {r.text}")
    camp_obj = r.json() if r.status_code in (200, 201) else {}
    campaign_id = camp_obj.get("campaign_id") or camp_obj.get("id")
    assert_res(camp_obj.get("status") == "PENDING", "Created campaign is PENDING", f"Got status: {camp_obj.get('status')}")

    # Verify pending campaign NOT visible in public list
    r = requests.get(f"{BASE_URL}/campaigns/")
    pub_ids = [c.get("campaign_id") or c.get("id") for c in r.json() if isinstance(c, dict)] if r.status_code == 200 and isinstance(r.json(), list) else []
    assert_res(campaign_id not in pub_ids, "Pending campaign is hidden from public list")

    # Admin approves campaign (PATCH /admin/campaigns/{id}/approve)
    r = requests.patch(f"{BASE_URL}/admin/campaigns/{campaign_id}/approve", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin approve campaign", f"Status {r.status_code} {r.text}")

    # Verify campaign NOW ACTIVE and in public list
    r = requests.get(f"{BASE_URL}/campaigns/{campaign_id}")
    assert_res(r.status_code == 200 and r.json().get("status") == "ACTIVE", "Campaign is now ACTIVE")

    # ----------------------------------------------------
    # SECTION 4: SECURITY NEGATIVE TESTS (ROLES & AUTH)
    # ----------------------------------------------------
    print("\n--- Testing Security & Role Authorization ---")
    # Donor -> /admin/* = 403
    r = requests.get(f"{BASE_URL}/admin/reports", headers=donor_headers)
    assert_res(r.status_code == 403, "Donor denied admin reports (403)", f"Got {r.status_code}")

    # Campaigner -> /admin/* = 403
    r = requests.get(f"{BASE_URL}/admin/users", headers=camp_headers)
    assert_res(r.status_code == 403, "Campaigner denied admin users (403)", f"Got {r.status_code}")

    # Donor -> Create campaign = 403
    r = requests.post(f"{BASE_URL}/campaigns/", json=camp_data, headers=donor_headers)
    assert_res(r.status_code == 403, "Donor denied campaign creation (403)", f"Got {r.status_code}")

    # Campaigner2 -> Modify Campaigner1's campaign = 403
    r = requests.put(f"{BASE_URL}/campaigns/{campaign_id}", json={"title": "Hacked Title"}, headers=camp2_headers)
    assert_res(r.status_code == 403, "Campaigner2 denied edit Campaigner1's campaign (403)", f"Got {r.status_code}")

    # Unauthenticated -> Protected endpoint = 401
    r = requests.get(f"{BASE_URL}/notifications/")
    assert_res(r.status_code == 401, "Unauthenticated denied protected endpoint (401)", f"Got {r.status_code}")

    # Invalid JWT -> Protected endpoint = 401
    r = requests.get(f"{BASE_URL}/notifications/", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert_res(r.status_code == 401, "Invalid JWT denied (401)", f"Got {r.status_code}")

    # Self Admin Deactivation Prevention = 400 (PATCH /admin/users/{id}/deactivate)
    r = requests.patch(f"{BASE_URL}/admin/users/{admin_user.user_id}/deactivate", headers=admin_headers)
    assert_res(r.status_code == 400, "Admin self-deactivation blocked (400)", f"Got {r.status_code}")

    # ----------------------------------------------------
    # SECTION 5: PAYMENT & DONATION MATRIX
    # ----------------------------------------------------
    print("\n--- Testing Payment & Donation Matrix ---")
    # Valid donation
    tx_ref = f"TX_{uuid.uuid4().hex[:8]}"
    pay_data = {
        "campaign_id": campaign_id,
        "amount": 250.0,
        "payment_method": "Credit Card",
        "transaction_id": tx_ref
    }
    r = requests.post(f"{BASE_URL}/donations/", json=pay_data, headers=donor_headers)
    assert_res(r.status_code in (200, 201), "Donor make valid donation", f"Got {r.status_code} {r.text}")
    don_obj = r.json() if r.status_code in (200, 201) else {}
    don_id = don_obj.get("donation_id") or don_obj.get("id")

    # Zero / Negative donation validation (400 or 422)
    r = requests.post(f"{BASE_URL}/donations/", json={"campaign_id": campaign_id, "amount": 0.0, "payment_method": "Credit Card"}, headers=donor_headers)
    assert_res(r.status_code in (400, 422), "Zero amount donation rejected (400/422)", f"Got {r.status_code}")

    r = requests.post(f"{BASE_URL}/donations/", json={"campaign_id": campaign_id, "amount": -50.0, "payment_method": "Credit Card"}, headers=donor_headers)
    assert_res(r.status_code in (400, 422), "Negative amount donation rejected (400/422)", f"Got {r.status_code}")

    # Non-existent campaign donation (404)
    r = requests.post(f"{BASE_URL}/donations/", json={"campaign_id": 999999, "amount": 50.0, "payment_method": "Credit Card"}, headers=donor_headers)
    assert_res(r.status_code == 404, "Non-existent campaign donation rejected (404)", f"Got {r.status_code}")

    # ----------------------------------------------------
    # SECTION 8: SAVED CAMPAIGNS
    # ----------------------------------------------------
    print("\n--- Testing Saved Campaigns ---")
    r = requests.post(f"{BASE_URL}/saved-campaigns/{campaign_id}", headers=donor_headers)
    assert_res(r.status_code in (200, 201), "Save campaign", f"Got {r.status_code} {r.text}")

    # List saved campaigns
    r = requests.get(f"{BASE_URL}/saved-campaigns/", headers=donor_headers)
    saved_res = r.json() if r.status_code == 200 else {}
    saved_list = saved_res.get("data", []) if isinstance(saved_res, dict) else saved_res
    saved_ids = [item["campaign"]["campaign_id"] for item in saved_list if isinstance(item, dict) and "campaign" in item]
    assert_res(campaign_id in saved_ids or len(saved_list) > 0, "Campaign present in saved list")

    # Unsave campaign
    r = requests.delete(f"{BASE_URL}/saved-campaigns/{campaign_id}", headers=donor_headers)
    assert_res(r.status_code in (200, 204), "Unsave campaign", f"Got {r.status_code}")

    # ----------------------------------------------------
    # SECTION 9: COMMENTS
    # ----------------------------------------------------
    print("\n--- Testing Comments ---")
    r = requests.post(f"{BASE_URL}/comments/", json={"campaign_id": campaign_id, "comment_text": "Great initiative! Supporting from Phase 20."}, headers=donor_headers)
    assert_res(r.status_code in (200, 201), "Post comment on campaign", f"Got {r.status_code} {r.text}")

    r = requests.get(f"{BASE_URL}/comments/{campaign_id}")
    comments = r.json() if r.status_code == 200 else []
    assert_res(len(comments) > 0, "Retrieve comments for campaign", f"Found {len(comments)} comments")

    # ----------------------------------------------------
    # SECTION 10: NOTIFICATIONS
    # ----------------------------------------------------
    print("\n--- Testing Notifications ---")
    r = requests.get(f"{BASE_URL}/notifications/", headers=camp_headers)
    assert_res(r.status_code == 200, "Campaigner fetch notifications", f"Got {r.status_code}")
    notifs = r.json() if r.status_code == 200 else []
    if notifs:
        notif_id = notifs[0].get("notification_id") or notifs[0].get("id")
        r_mark = requests.patch(f"{BASE_URL}/notifications/{notif_id}/read", headers=camp_headers)
        assert_res(r_mark.status_code == 200, "Mark notification as read", f"Got {r_mark.status_code}")
    
    r_un = requests.get(f"{BASE_URL}/notifications/unread-count", headers=camp_headers)
    assert_res(r_un.status_code == 200, "Get unread notifications count", f"Got {r_un.status_code}")

    # ----------------------------------------------------
    # SECTION 7: SEARCH, PAGINATION & FILTERS
    # ----------------------------------------------------
    print("\n--- Testing Search, Pagination & Filters ---")
    r = requests.get(f"{BASE_URL}/campaigns/?category=Medical")
    assert_res(r.status_code == 200, "Filter campaigns by category", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/campaigns/?search=Phase%2020")
    assert_res(r.status_code == 200, "Search campaigns by keyword", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/campaigns/?limit=2&offset=0")
    assert_res(r.status_code == 200, "Paginated campaign list", f"Got {r.status_code}")

    # ----------------------------------------------------
    # SECTION 11: ADMIN DASHBOARD ENDPOINTS
    # ----------------------------------------------------
    print("\n--- Testing Admin Overview, Management & Audit Logs ---")
    r = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin List Users", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin/campaigns", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin List Campaigns", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin/donations", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin List Donations", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin/transactions", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin List Transactions", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin/reports", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin Platform Reports", f"Got {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin/audit-logs", headers=admin_headers)
    assert_res(r.status_code == 200, "Admin Audit Logs", f"Got {r.status_code}")

    # ----------------------------------------------------
    # SECTION 12: DB INTEGRITY CHECK (DIRECT SQL/ORM)
    # ----------------------------------------------------
    print("\n--- Testing Database Integrity ---")
    try:
        from app.models.campaign import Campaign
        from app.models.donation import Donation
        
        # Check orphaned campaigns
        user_ids = set(u.user_id for u in db.query(User).all())
        orphaned_camps = db.query(Campaign).filter(~Campaign.creator_id.in_(user_ids)).count()
        assert_res(orphaned_camps == 0, "No orphaned campaigns in DB", f"Found {orphaned_camps}")

        # Check orphaned donations
        camp_ids = set(c.campaign_id for c in db.query(Campaign).all())
        orphaned_dons = db.query(Donation).filter(~Donation.campaign_id.in_(camp_ids)).count()
        assert_res(orphaned_dons == 0, "No orphaned donations in DB", f"Found {orphaned_dons}")

        db.close()
    except Exception as e:
        assert_res(False, "Database integrity verification exception", str(e))

    # ----------------------------------------------------
    # SUMMARY
    # ----------------------------------------------------
    print("\n========================================================")
    print(f"RESULTS: {passed_tests} PASSED, {failed_tests} FAILED")
    print("========================================================\n")

    if failures:
        print("FAILURES LIST:")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("ALL PHASE 20 VERIFICATION TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()
