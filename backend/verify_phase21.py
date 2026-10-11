"""
Phase 21 Verification: Signup & Login Validation Rules
Tests backend validation, email normalization, phone, password rules.
"""
import sys
import os
import uuid
import requests

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")

passed = 0
failed = 0


def ok(name):
    global passed
    passed += 1
    print(f"  [PASS] {name}")


def fail(name, detail=""):
    global failed
    failed += 1
    print(f"  [FAIL] {name}" + (f" -- {detail}" if detail else ""))


def post(path, body, expected_status=None):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=body, timeout=15)
        return r
    except Exception as e:
        print(f"  ⚠ Request error for {path}: {e}")
        return None


def run():
    uid = uuid.uuid4().hex[:6]
    valid_email = f"testuser_{uid}@example.com"
    valid_phone = "9876543210"
    valid_password = "ValidPass1!"
    valid_name = "Test User"

    print("=" * 65)
    print("PHASE 21 — SIGNUP & LOGIN VALIDATION TESTS")
    print("=" * 65)

    # ── Signup: valid request ─────────────────────────────────────
    print("\n--- Signup: valid request ---")
    r = post("/auth/signup", {"name": valid_name, "email": valid_email,
                              "password": valid_password, "phone": valid_phone, "role": "DONOR"})
    if r and r.status_code == 200:
        ok("Valid signup succeeds (HTTP 200)")
        data = r.json()
        if data.get("email") == valid_email:
            ok("Email stored in lowercase")
        else:
            fail("Email stored in lowercase", f"got {data.get('email')!r}")
        if "access_token" in data:
            ok("JWT token returned on signup")
        else:
            fail("JWT token returned on signup")
        if "password" not in data:
            ok("Password NOT exposed in response")
        else:
            fail("Password NOT exposed in response — password is in response!")
    else:
        fail("Valid signup succeeds", f"status={r.status_code if r else 'None'}, body={r.text[:200] if r else ''}")

    # ── Signup: uppercase email normalized ────────────────────────
    print("\n--- Signup: uppercase email normalized ---")
    uid2 = uuid.uuid4().hex[:6]
    upper_email = f"TEST_{uid2}@EXAMPLE.COM"
    r = post("/auth/signup", {"name": "Upper Email", "email": upper_email,
                              "password": valid_password, "phone": valid_phone, "role": "DONOR"})
    if r and r.status_code == 200:
        stored = r.json().get("email", "")
        if stored == upper_email.lower():
            ok("Uppercase email normalized to lowercase on signup")
        else:
            fail("Uppercase email normalized", f"expected {upper_email.lower()!r}, got {stored!r}")
    else:
        fail("Uppercase email signup", f"status={r.status_code if r else 'None'}")

    # ── Signup: duplicate email ───────────────────────────────────
    print("\n--- Signup: duplicate email ---")
    r = post("/auth/signup", {"name": valid_name, "email": valid_email,
                              "password": valid_password, "phone": valid_phone, "role": "DONOR"})
    if r is not None and r.status_code == 400:
        ok("Duplicate email rejected (HTTP 400)")
    else:
        fail("Duplicate email rejected", f"status={r.status_code if r is not None else 'None'}")

    # ── Signup: invalid email format ──────────────────────────────
    print("\n--- Signup: invalid email format ---")
    r = post("/auth/signup", {"name": valid_name, "email": "notanemail",
                              "password": valid_password, "phone": valid_phone, "role": "DONOR"})
    if r is not None and r.status_code in (400, 422):
        ok("Invalid email format rejected")
    else:
        fail("Invalid email format rejected", f"status={r.status_code if r is not None else 'None'}")

    # ── Signup: phone validation ──────────────────────────────────
    print("\n--- Signup: phone validation ---")

    bad_phones = [
        ("123456789", "9 digits"),
        ("12345678901", "11 digits"),
        ("123456789a", "contains letter"),
        ("123 456 789", "contains spaces"),
        ("", "empty"),
    ]
    for phone_val, desc in bad_phones:
        r = post("/auth/signup", {"name": valid_name, "email": f"ph_{uuid.uuid4().hex[:4]}@example.com",
                                  "password": valid_password, "phone": phone_val, "role": "DONOR"})
        if r is not None and r.status_code in (400, 422):
            ok(f"Phone '{desc}' rejected")
        else:
            fail(f"Phone '{desc}' rejected", f"status={r.status_code if r is not None else 'None'}")

    # ── Signup: password validation ───────────────────────────────
    print("\n--- Signup: password validation ---")

    bad_passwords = [
        ("short1!", "less than 8 chars"),
        ("nouppercase1!", "no uppercase"),
        ("NoDigitHere!", "no digit"),
        ("NoSpecial1", "no special char"),
    ]
    for pw, desc in bad_passwords:
        r = post("/auth/signup", {"name": valid_name, "email": f"pw_{uuid.uuid4().hex[:4]}@example.com",
                                  "password": pw, "phone": valid_phone, "role": "DONOR"})
        if r is not None and r.status_code in (400, 422):
            ok(f"Password ({desc}) rejected")
        else:
            fail(f"Password ({desc}) rejected", f"status={r.status_code if r is not None else 'None'}, body={r.text[:100] if r is not None else ''}")

    # ── Login: valid (existing account just created) ──────────────
    print("\n--- Login: valid account ---")
    r = post("/auth/login", {"email": valid_email, "password": valid_password})
    if r is not None and r.status_code == 200:
        ok("Valid login succeeds")
        data = r.json()
        if "access_token" in data:
            ok("JWT returned on login")
        else:
            fail("JWT returned on login")
    else:
        fail("Valid login succeeds", f"status={r.status_code if r is not None else 'None'}")

    # ── Login: uppercase email normalized ─────────────────────────
    print("\n--- Login: email case normalization ---")
    r = post("/auth/login", {"email": valid_email.upper(), "password": valid_password})
    if r is not None and r.status_code == 200:
        ok("Login works with uppercase email input")
    else:
        fail("Login works with uppercase email input", f"status={r.status_code if r is not None else 'None'}")

    # ── Login: wrong password ─────────────────────────────────────
    print("\n--- Login: invalid credentials ---")
    r = post("/auth/login", {"email": valid_email, "password": "WrongPassword99!"})
    if r is not None and r.status_code == 401:
        ok("Wrong password rejected (HTTP 401)")
    else:
        fail("Wrong password rejected", f"status={r.status_code if r is not None else 'None'}")

    # ── Login: non-existent email ─────────────────────────────────
    r = post("/auth/login", {"email": "nobody@nowhere.com", "password": "AnyPass1!"})
    if r is not None and r.status_code == 401:
        ok("Non-existent email rejected (HTTP 401)")
    else:
        fail("Non-existent email rejected", f"status={r.status_code if r is not None else 'None'}")

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 65)
    return failed == 0


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
