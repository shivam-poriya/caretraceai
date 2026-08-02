"""
Exhaustive verification script testing ALL 32 backend API endpoints.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def safe_print(text: str):
    """Safely prints text on Windows console."""
    print(text.encode("ascii", "replace").decode("ascii"))


def run_full_api_audit():
    print("=" * 70)
    print("CLINIC INTAKE ASSISTANT -- COMPLETE API AUDIT (32 ENDPOINTS)")
    print("=" * 70)

    session = requests.Session()
    passed_count = 0
    total_count = 0

    def check(name, response, expected_status=200):
        nonlocal passed_count, total_count
        total_count += 1
        status = response.status_code
        if status == expected_status:
            passed_count += 1
            safe_print(f"  [PASS] {name} -> Status {status}")
            return True
        else:
            safe_print(f"  [FAIL] {name} -> Expected {expected_status}, got {status}: {response.text[:200]}")
            return False

    # ----------------------------------------------------
    # MODULE 1: AUTHENTICATION
    # ----------------------------------------------------
    print("\n--- MODULE 1: AUTHENTICATION ---")
    
    # 1. Auth root test
    r = session.get(f"{BASE_URL}/v1/custom-auth/test")
    check("GET /v1/custom-auth/test", r)

    # 2. Register new patient
    new_patient_data = {
        "username": "test_patient_audit",
        "email": "audit_patient@example.com",
        "password": "Password@123",
        "role": "patient",
        "first_name": "Audit",
        "last_name": "Patient",
        "phone": "+91 9999988888",
        "birthday": "1995-01-01",
        "gender": "Female"
    }
    r = session.post(f"{BASE_URL}/v1/custom-auth/register/", json=new_patient_data)
    if r.status_code == 400 and "already exists" in r.text:
        safe_print("  [INFO] Register patient (Already exists, proceeding)")
    else:
        check("POST /v1/custom-auth/register/ (Patient)", r)

    # 3. Patient Login
    r = session.post(f"{BASE_URL}/v1/custom-auth/login/", data={"username": "patient_demo", "password": "Password@123"})
    check("POST /v1/custom-auth/login/ (Patient)", r)
    p_data = r.json()
    patient_token = p_data["access_token"]
    patient_id = p_data["patient_id"]
    patient_headers = {"Authorization": f"Bearer {patient_token}"}

    # 4. Doctor Login
    r = session.post(f"{BASE_URL}/v1/custom-auth/login/", data={"username": "doctor_demo", "password": "Password@123"})
    check("POST /v1/custom-auth/login/ (Doctor)", r)
    d_data = r.json()
    doctor_token = d_data["access_token"]
    doctor_id = d_data["doctor_id"]
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}

    # 5. Get User Profile
    r = session.get(f"{BASE_URL}/v1/custom-auth/get-user-profile/", headers=patient_headers)
    check("GET /v1/custom-auth/get-user-profile/", r)

    # ----------------------------------------------------
    # MODULE 2: PATIENT MODULE
    # ----------------------------------------------------
    print("\n--- MODULE 2: PATIENT HEALTH RECORD ---")

    # 6. Get Patient Profile
    r = session.get(f"{BASE_URL}/v1/patient/profile/", headers=patient_headers)
    check("GET /v1/patient/profile/", r)

    # 7. Update Patient Profile
    r = session.put(f"{BASE_URL}/v1/patient/profile/", headers=patient_headers, json={
        "blood_group": "O+",
        "emergency_contact_name": "Rajesh Patel",
        "emergency_contact_phone": "+91 9876500000"
    })
    check("PUT /v1/patient/profile/", r)

    # 8. Report Symptom
    r = session.post(f"{BASE_URL}/v1/patient/symptoms/", headers=patient_headers, json={
        "concern": "Mild Dizziness",
        "severity": 3,
        "duration": "1 day",
        "pattern": "Intermittent"
    })
    check("POST /v1/patient/symptoms/", r)
    symptom_id = r.json()["id"] if r.status_code == 200 else 1

    # 9. Update Symptom
    r = session.put(f"{BASE_URL}/v1/patient/symptoms/{symptom_id}/", headers=patient_headers, json={
        "severity": 5,
        "duration": "2 days"
    })
    check(f"PUT /v1/patient/symptoms/{symptom_id}/", r)

    # 10. List Symptoms
    r = session.get(f"{BASE_URL}/v1/patient/symptoms/", headers=patient_headers)
    check("GET /v1/patient/symptoms/", r)

    # 11. Add Allergy
    r = session.post(f"{BASE_URL}/v1/patient/allergies/", headers=patient_headers, json={
        "allergen": "Dust",
        "reaction": "Sneezing",
        "severity": "Mild"
    })
    check("POST /v1/patient/allergies/", r)

    # 12. List Allergies
    r = session.get(f"{BASE_URL}/v1/patient/allergies/", headers=patient_headers)
    check("GET /v1/patient/allergies/", r)

    # 13. Add Medical History
    r = session.post(f"{BASE_URL}/v1/patient/medical-history/", headers=patient_headers, json={
        "condition_name": "Hypertension",
        "diagnosed_year": "2020",
        "notes": "Managed with diet and routine medication"
    })
    check("POST /v1/patient/medical-history/", r)

    # 14. List Medical History
    r = session.get(f"{BASE_URL}/v1/patient/medical-history/", headers=patient_headers)
    check("GET /v1/patient/medical-history/", r)

    # 15. Report Medication (Patient-Reported)
    r = session.post(f"{BASE_URL}/v1/patient/medications/", headers=patient_headers, json={
        "medication_name": "Amlodipine",
        "dosage": "5mg",
        "frequency": "Once daily morning"
    })
    check("POST /v1/patient/medications/", r)

    # 16. List Patient Medications
    r = session.get(f"{BASE_URL}/v1/patient/medications/", headers=patient_headers)
    check("GET /v1/patient/medications/", r)

    # 17. Get Patient Timeline
    r = session.get(f"{BASE_URL}/v1/patient/timeline/", headers=patient_headers)
    check("GET /v1/patient/timeline/", r)

    # ----------------------------------------------------
    # MODULE 3: INTAKE & GENAI CHAT
    # ----------------------------------------------------
    print("\n--- MODULE 3: INTAKE & GENAI CHAT PIPELINE ---")

    # 18. Create Intake Session
    r = session.post(f"{BASE_URL}/v1/intake/sessions/", headers=patient_headers)
    check("POST /v1/intake/sessions/", r)
    sess_id = r.json()["id"]

    # 19. List Intake Sessions
    r = session.get(f"{BASE_URL}/v1/intake/sessions/", headers=patient_headers)
    check("GET /v1/intake/sessions/", r)

    # 20. Get Session Details
    r = session.get(f"{BASE_URL}/v1/intake/sessions/{sess_id}/", headers=patient_headers)
    check(f"GET /v1/intake/sessions/{sess_id}/", r)

    # 21. Process Patient Message (GenAI Pipeline: Extraction, RAG, Safety, Missing Info, Follow-up)
    r = session.post(f"{BASE_URL}/v1/intake/sessions/{sess_id}/message/", headers=patient_headers, json={
        "message": "I have severe chest pain and nausea since morning."
    })
    check(f"POST /v1/intake/sessions/{sess_id}/message/", r)

    # 22. Get Session Conversation Transcript
    r = session.get(f"{BASE_URL}/v1/intake/sessions/{sess_id}/messages/", headers=patient_headers)
    check(f"GET /v1/intake/sessions/{sess_id}/messages/", r)

    # 23. End Intake Session & Generate Doctor Brief
    r = session.post(f"{BASE_URL}/v1/intake/sessions/{sess_id}/end/", headers=patient_headers)
    check(f"POST /v1/intake/sessions/{sess_id}/end/", r)

    # ----------------------------------------------------
    # MODULE 4: DOCTOR DASHBOARD & CLINICAL RECORDS
    # ----------------------------------------------------
    print("\n--- MODULE 4: DOCTOR DASHBOARD & CLINICAL RECORDS ---")

    # 24. List Assigned Patients
    r = session.get(f"{BASE_URL}/v1/doctor/patients/", headers=doctor_headers)
    check("GET /v1/doctor/patients/", r)

    # 25. Search Patients
    r = session.get(f"{BASE_URL}/v1/doctor/patients/search/?q=Ramesh", headers=doctor_headers)
    check("GET /v1/doctor/patients/search/?q=Ramesh", r)

    # 26. Get Patient Overview
    r = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/overview/", headers=doctor_headers)
    check(f"GET /v1/doctor/patients/{patient_id}/overview/", r)

    # 27. Get Doctor Patient Timeline
    r = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/timeline/", headers=doctor_headers)
    check(f"GET /v1/doctor/patients/{patient_id}/timeline/", r)

    # 28. Get AI Intake Brief Summary
    r = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/intake-summary/", headers=doctor_headers)
    check(f"GET /v1/doctor/patients/{patient_id}/intake-summary/", r)

    # 29. Get "WHAT CHANGED?" Comparison
    r = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/what-changed/", headers=doctor_headers)
    check(f"GET /v1/doctor/patients/{patient_id}/what-changed/", r)

    # 30. Get Original Patient Conversation Transcript
    r = session.get(f"{BASE_URL}/v1/doctor/patients/{patient_id}/conversations/", headers=doctor_headers)
    check(f"GET /v1/doctor/patients/{patient_id}/conversations/", r)

    # 31. Add Doctor Clinical Assessment (Doctor-Only)
    r = session.post(f"{BASE_URL}/v1/doctor/patients/{patient_id}/clinical-assessment/", headers=doctor_headers, json={
        "clinical_notes": "Patient audited in comprehensive check.",
        "diagnosis": "Angina Pectoris",
        "treatment_plan": "Cardiology evaluation and ECG monitoring",
        "follow_up_instructions": "Return in 1 week"
    })
    check(f"POST /v1/doctor/patients/{patient_id}/clinical-assessment/", r)

    # 32. Add Clinician Prescription (Doctor-Only)
    r = session.post(f"{BASE_URL}/v1/doctor/patients/{patient_id}/prescription/", headers=doctor_headers, json={
        "medication_name": "Nitroglycerin",
        "dosage": "0.4mg",
        "frequency": "Sublingual as needed for chest pain",
        "instructions": "Place under tongue"
    })
    check(f"POST /v1/doctor/patients/{patient_id}/prescription/", r)

    # 33. Add Doctor Note (Doctor-Only)
    r = session.post(f"{BASE_URL}/v1/doctor/patients/{patient_id}/notes/", headers=doctor_headers, json={
        "note_text": "Private note: Monitor patient's BP log next week."
    })
    check(f"POST /v1/doctor/patients/{patient_id}/notes/", r)

    # ----------------------------------------------------
    # MODULE 5: SECURITY & PRIVACY VERIFICATION
    # ----------------------------------------------------
    print("\n--- MODULE 5: SECURITY & PRIVACY VERIFICATION ---")

    # Patient accessing doctor endpoint -> must fail with 403
    r = session.post(f"{BASE_URL}/v1/doctor/patients/{patient_id}/clinical-assessment/", headers=patient_headers, json={
        "clinical_notes": "Patient attempting doctor action"
    })
    check("SECURITY: Patient block on Clinical Assessment", r, expected_status=403)

    r = session.post(f"{BASE_URL}/v1/doctor/patients/{patient_id}/prescription/", headers=patient_headers, json={
        "medication_name": "Self-prescribed",
        "dosage": "100mg",
        "frequency": "Daily"
    })
    check("SECURITY: Patient block on Prescription", r, expected_status=403)

    # Summary
    print("\n" + "=" * 70)
    safe_print(f"TOTAL ENDPOINTS TESTED: {total_count}")
    safe_print(f"SUCCESSFUL / PASSED:   {passed_count} / {total_count}")
    print("=" * 70)

    if passed_count == total_count:
        safe_print("🎉 ALL API ENDPOINTS ARE WORKING 100% AS INTENDED!")
    else:
        safe_print(f"⚠️ {total_count - passed_count} endpoints failed. See details above.")


if __name__ == "__main__":
    run_full_api_audit()
