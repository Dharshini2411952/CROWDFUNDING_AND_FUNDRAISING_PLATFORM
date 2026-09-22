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
from app.models.audit_log import AuditLog
from app.core.security import create_access_token

def run_tests():
    print("=" * 70)
    print("RUNNING PHASE 18 ADMIN DASHBOARD & PLATFORM MANAGEMENT VERIFICATION")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Create test users
        donor_email = f"p18_donor_{uuid.uuid4().hex[:6]}@test.com"
        donor = User(email=donor_email, name="P18 Donor", password="hashedpassword123", role="DONOR")
        
        admin_email = f"p18_admin_{uuid.uuid4().hex[:6]}@test.com"
        admin = User(email=admin_email, name="P18 Admin", password="hashedpassword123", role="ADMIN")
        
        db.add_all([donor, admin])
        db.commit()
        db.refresh(donor)
        db.refresh(admin)

        donor_token = create_access_token(donor.user_id, donor.role)
        admin_token = create_access_token(admin.user_id, admin.role)

        headers_donor = {"Authorization": f"Bearer {donor_token}"}
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        # -------------------------------------------------------------
        # Test 1: Non-Admin Access Forbidden (403)
        # -------------------------------------------------------------
        print("\n--- Test 1: Non-Admin Access Forbidden (403) ---")
        res = requests.get(f"{BASE_URL}/admin/reports", headers=headers_donor)
        assert res.status_code == 403, f"Expected 403 for non-admin, got {res.status_code}"
        print("PASSED: Donor access to admin API returned 403 Forbidden.")

        # -------------------------------------------------------------
        # Test 2: Admin Reports API
        # -------------------------------------------------------------
        print("\n--- Test 2: Admin Reports API ---")
        res = requests.get(f"{BASE_URL}/admin/reports", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json().get("data", {})
        assert "total_users" in data
        assert "total_donors" in data
        assert "total_campaigners" in data
        assert "total_campaigns" in data
        assert "campaigns_by_category" in data
        print(f"PASSED: Reports API returned stats (Total Users: {data['total_users']}).")

        # -------------------------------------------------------------
        # Test 3: Get Admin Users List
        # -------------------------------------------------------------
        print("\n--- Test 3: Get Users List ---")
        res = requests.get(f"{BASE_URL}/admin/users", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        users = res.json()
        assert any(u["user_id"] == donor.user_id for u in users)
        print(f"PASSED: Users list returned {len(users)} users.")

        # -------------------------------------------------------------
        # Test 4: User Deactivation & Activation
        # -------------------------------------------------------------
        print("\n--- Test 4: User Deactivation & Activation ---")
        res = requests.patch(f"{BASE_URL}/admin/users/{donor.user_id}/deactivate", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert res.json()["is_active"] == False

        res = requests.patch(f"{BASE_URL}/admin/users/{donor.user_id}/activate", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert res.json()["is_active"] == True
        print("PASSED: User deactivate and activate working cleanly.")

        # -------------------------------------------------------------
        # Test 5: Prevent Admin Self-Deactivation
        # -------------------------------------------------------------
        print("\n--- Test 5: Prevent Admin Self-Deactivation ---")
        res = requests.patch(f"{BASE_URL}/admin/users/{admin.user_id}/deactivate", headers=headers_admin)
        assert res.status_code == 400, f"Expected 400 for self-deactivation, got {res.status_code}"
        print("PASSED: Admin self-deactivation prevented with 400 Bad Request.")

        # -------------------------------------------------------------
        # Test 6: Campaign Approval, Rejection & Audit Logging
        # -------------------------------------------------------------
        print("\n--- Test 6: Campaign Approval & Audit Logging ---")
        camp = Campaign(
            title="P18 Campaign",
            description="Testing admin approval & audit log",
            goal_amount=500.0,
            collected_amount=0.0,
            category="Community",
            status="PENDING",
            creator_id=donor.user_id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=10),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)

        res = requests.patch(f"{BASE_URL}/admin/campaigns/{camp.campaign_id}/approve", headers=headers_admin)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"

        res_audit = requests.get(f"{BASE_URL}/admin/audit-logs", headers=headers_admin)
        assert res_audit.status_code == 200, f"Expected 200 for audit logs, got {res_audit.status_code}"
        logs = res_audit.json()
        assert any(l["action"] == "CAMPAIGN_APPROVED" and l["entity_id"] == camp.campaign_id for l in logs)
        print("PASSED: Campaign approval recorded in audit logs successfully.")

        print("\n" + "=" * 70)
        print("ALL PHASE 18 ADMIN VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
