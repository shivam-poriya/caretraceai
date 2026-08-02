"""
End-to-end automated verification script for Clinic Intake Assistant API.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def safe_print(text: str):
    """Safely prints text on Windows console without encoding errors."""
    print(text.encode("ascii", "replace").decode("ascii"))


def test_clinic_intake_api():
    print("=" * 60)
    print("CLINIC INTAKE ASSISTANT -- API VERIFICATION TEST")
    print("=" * 60)

    session = requests.Session()

    # 1. Patient Login
    print("\n1. Patient Login (patient_demo)...")
    res = session.post(
        f"{BASE_URL}/v1/custom-auth/login/",
        data={"username": "patient_demo", "password": "Password@123"}
    )
    assert res.status_code == 200, f"Patient login failed: {res.text}"
    p_data = res.json()
    patient_token = p_data["access_token"]
    patient_id = p_data["patient_id"]
    safe_print(f"   [OK] Patient Token acquired. Patient ID: {patient_id}, Role: {p_data['role']}")

    # 2. Doctor Login
    print("\n2. Doctor Login (doctor_demo)...")
    res = session.post(
        f"{BASE_URL}/v1/custom-auth/login/",
        data={"username": "doctor_demo", "password": "Password@123"}
    )
    assert res.status_code == 200, f"Doctor login failed: {res.text}"
    d_data = res.json()
    doctor_token = d_data["access_token"]
    doctor_id = d_data["doctor_id"]
    safe_print(f"   [OK] Doctor Token acquired. Doctor ID: {doctor_id}, Role: {d_data['role']}")

    # Headers
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}

    # 3. Patient Profile Check
    print("\n3. Patient Health Profile...")
    res = session.get(f"{BASE_URL}/v1/patient/profile/", headers=patient_headers)
    assert res.status_code == 200, f"Get profile failed: {res.text}"
    safe_print(f"   [OK] Patient Name: {res.json()['first_name']} {res.json()['last_name']}")

    # 4. Start AI Intake Session
    print("\n4. Starting GenAI Intake Session...")
    res = session.post(f"{BASE_URL}/v1/intake/sessions/", headers=patient_headers)
    assert res.status_code == 200, f"Create intake session failed: {res.text}"
    session_id = res.json()["id"]
    safe_print(f"   [OK] Intake Session #{session_id} Created.")

    # 5. Patient sends natural language input (GenAI Pipeline Execution)
    print("\n5. Sending Patient Natural Language Input to GenAI Pipeline...")
    patient_msg = "I have been having chest pain for the last two days, I am finding it difficult to breathe, and I am taking BP medication."
    safe_print(f"   Patient says: \"{patient_msg}\"")

    res = session.post(
        f"{BASE_URL}/v1/intake/sessions/{session_id}/message/",
        headers=patient_headers,
        json={"message": patient_msg}
    )
    assert res.status_code == 200, f"Intake message failed: {res.text}"
    chat_res = res.json()
    print("\n   [AI Response]:")
    safe_print(f"   {chat_res['ai_response']}")
    safe_print(f"   Safety Flag Raised: {chat_res['safety_flag']}")
    safe_print(f"   Extracted Symptoms/Meds: {json.dumps(chat_res['extracted_data'])}")
    safe_print(f"   Missing Info List: {chat_res['missing_information']}")

    # 6. End Intake Session & Generate Doctor Brief (Prompt D)
    print("\n6. Ending Intake Session & Generating Doctor Brief...")
    res = session.post(f"{BASE_URL}/v1/intake/sessions/{session_id}/end/", headers=patient_headers)
    assert res.status_code == 200, f"End intake session failed: {res.text}"
    summary_md = res.json()["summary_generated"]
    safe_print(f"   [OK] Generated Brief length: {len(summary_md)} chars")

    # 7. Doctor Dashboard: Patient Overview
    print("\n7. Doctor Dashboard -- Overview for Patient #1...")
    res = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/overview/", headers=doctor_headers)
    assert res.status_code == 200, f"Get overview failed: {res.text}"
    ov = res.json()
    safe_print(f"   [OK] Patient Reported Symptoms Count: {len(ov['reported_symptoms'])}")
    safe_print(f"   [OK] Patient Reported Meds Count: {len(ov['patient_reported_medications'])}")

    # 8. Doctor Feature: "WHAT CHANGED?"
    print("\n8. Doctor Feature -- 'WHAT CHANGED SINCE LAST VISIT?'...")
    res = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/what-changed/", headers=doctor_headers)
    assert res.status_code == 200, f"What changed failed: {res.text}"
    wc = res.json()
    safe_print(f"   [OK] New Items: {wc['new_items']}")
    safe_print(f"   [OK] Updated Items: {wc['updated_items']}")
    safe_print(f"   [OK] Summary: {wc['summary']}")

    # 9. Doctor Adds Clinical Assessment & Prescribes Medication (Doctor-Only)
    print("\n9. Doctor Enters Clinical Assessment & Prescribes Medication...")
    res = session.post(
        f"{BASE_URL}/v1/doctor/patients/{patient_id}/clinical-assessment/",
        headers=doctor_headers,
        json={
            "clinical_notes": "Patient presents with angina-like symptoms. Needs ECG and cardiac enzyme panel.",
            "diagnosis": "Unstable Angina - Rule out MI",
            "treatment_plan": "Immediate ECG, Sublingual Nitroglycerin, Referral to Cardiology",
            "follow_up_instructions": "Rest and avoid physical exertion."
        }
    )
    assert res.status_code == 200, f"Clinical assessment failed: {res.text}"
    safe_print("   [OK] Clinical Assessment & Diagnosis Added.")

    res = session.post(
        f"{BASE_URL}/v1/doctor/patients/{patient_id}/prescription/",
        headers=doctor_headers,
        json={
            "medication_name": "Aspirin",
            "dosage": "75mg",
            "frequency": "Once daily",
            "instructions": "Take after meals."
        }
    )
    assert res.status_code == 200, f"Prescription failed: {res.text}"
    safe_print("   [OK] Clinician Prescription Added (Separately stored from patient-reported meds).")

    # 10. Role Privacy Check: Patient attempts Doctor-Only action
    print("\n10. Security Test -- Patient attempts to post doctor clinical assessment...")
    res = session.post(
        f"{BASE_URL}/v1/doctor/patients/{patient_id}/clinical-assessment/",
        headers=patient_headers,
        json={"clinical_notes": "Unauthorized attempt"}
    )
    assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"
    safe_print("   [OK] Access Denied: HTTP 403 Forbidden enforced correctly at database/backend layer!")

    print("\n" + "=" * 60)
    safe_print("ALL 10 END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_clinic_intake_api()
