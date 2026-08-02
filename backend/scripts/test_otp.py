"""
Test script for Forgot Password OTP workflow.
"""
import requests
from config.database import SessionLocal
from apps.db_models import User

BASE_URL = "http://127.0.0.1:8000"


def safe_print(text: str):
    print(text.encode("ascii", "replace").decode("ascii"))


def test_otp_flow():
    print("=" * 60)
    print("FORGOT PASSWORD OTP WORKFLOW TEST")
    print("=" * 60)

    email = "patient@example.com"
    session = requests.Session()

    # 1. Request OTP
    print("\n1. Requesting Password Reset OTP for patient@example.com...")
    res = session.post(f"{BASE_URL}/v1/custom-auth/forgot-password/", json={"email": email})
    assert res.status_code == 200, f"Forgot password failed: {res.text}"
    print(f"   [OK] Response: {res.json()['message']}")

    # Query DB to get the generated OTP for testing
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    assert user and user.reset_otp, "OTP was not saved in DB"
    otp = user.reset_otp
    print(f"   [OK] Generated OTP retrieved from DB/Email queue: {otp}")

    # 2. Verify OTP
    print("\n2. Verifying OTP...")
    res = session.post(f"{BASE_URL}/v1/custom-auth/verify-otp/", json={"email": email, "otp": otp})
    assert res.status_code == 200, f"Verify OTP failed: {res.text}"
    print(f"   [OK] Response: {res.json()['message']}")

    # 3. Reset Password
    print("\n3. Resetting Password to 'NewPassword@123'...")
    res = session.post(
        f"{BASE_URL}/v1/custom-auth/reset-password/",
        json={"email": email, "otp": otp, "new_password": "NewPassword@123"}
    )
    assert res.status_code == 200, f"Reset password failed: {res.text}"
    print(f"   [OK] Response: {res.json()['message']}")

    # 4. Login with New Password
    print("\n4. Testing Login with New Password...")
    res = session.post(
        f"{BASE_URL}/v1/custom-auth/login/",
        data={"username": "patient_demo", "password": "NewPassword@123"}
    )
    assert res.status_code == 200, f"Login with new password failed: {res.text}"
    print("   [OK] Login with NEW password successful!")

    # 5. Restore Original Password
    print("\n5. Restoring Original Password ('Password@123')...")
    res = session.post(f"{BASE_URL}/v1/custom-auth/forgot-password/", json={"email": email})
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    otp_restore = user.reset_otp
    db.close()

    res = session.post(
        f"{BASE_URL}/v1/custom-auth/reset-password/",
        json={"email": email, "otp": otp_restore, "new_password": "Password@123"}
    )
    assert res.status_code == 200, f"Password restoration failed: {res.text}"
    print("   [OK] Password restored to original!")

    print("\n" + "=" * 60)
    print("ALL FORGOT PASSWORD OTP TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_otp_flow()
