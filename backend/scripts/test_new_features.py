"""
Comprehensive verification script for new Patient, Doctor, and Safety Features.
"""
import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"


def safe_print(text: str):
    print(text.encode("ascii", "replace").decode("ascii"))


def test_new_features():
    print("=" * 70)
    print("CLINIC INTAKE ASSISTANT -- NEW FEATURE ENDPOINTS AUDIT")
    print("=" * 70)

    session = requests.Session()

    # Logins
    r_p = session.post(f"{BASE_URL}/v1/custom-auth/login/", data={"username": "patient_demo", "password": "Password@123"})
    assert r_p.status_code == 200
    p_data = r_p.json()
    p_headers = {"Authorization": f"Bearer {p_data['access_token']}"}
    p_id = p_data["patient_id"]

    r_d = session.post(f"{BASE_URL}/v1/custom-auth/login/", data={"username": "doctor_demo", "password": "Password@123"})
    assert r_d.status_code == 200
    d_data = r_d.json()
    d_headers = {"Authorization": f"Bearer {d_data['access_token']}"}

    # 1. Resume Prompt
    print("\n1. Testing Resume Prompt Endpoint...")
    res = session.get(f"{BASE_URL}/v1/patient/resume-prompt/", headers=p_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] Prompt: {res.json()['resume_prompt']}")

    # 2. Quick-Update Chips
    print("\n2. Testing Quick-Update Chip ('got_worse')...")
    res = session.post(f"{BASE_URL}/v1/patient/quick-update/", headers=p_headers, json={"chip_type": "got_worse"})
    assert res.status_code == 200
    safe_print(f"   [OK] Action Description: {res.json()['action_description']}")

    # 3. Photo Attachment Upload (Medication box)
    print("\n3. Testing Photo Attachment Upload (Medication Box)...")
    dummy_img_path = "scratch/dummy_med_box.jpg"
    os.makedirs("scratch", exist_ok=True)
    with open(dummy_img_path, "wb") as f:
        f.write(b"JPEG_DUMMY_IMAGE_BYTES_FOR_MEDICATION_BOX")

    with open(dummy_img_path, "rb") as f:
        res = session.post(
            f"{BASE_URL}/v1/patient/attachments/upload/",
            headers=p_headers,
            files={"file": ("med_box.jpg", f, "image/jpeg")},
            data={"category": "medication_strip", "note": "Patient photo of BP tablet box"}
        )
    assert res.status_code == 200
    safe_print(f"   [OK] Uploaded Attachment Path: {res.json()['file_path']}")

    # 4. Read-Back Confirmation Card in Intake Chat
    print("\n4. Testing GenAI Intake Chat with 'Read it back' Card & Completeness Ring...")
    res = session.post(f"{BASE_URL}/v1/intake/sessions/", headers=p_headers)
    sess_id = res.json()["id"]

    res = session.post(f"{BASE_URL}/v1/intake/sessions/{sess_id}/message/", headers=p_headers, json={"message": "My headache is back, severity 7/10."})
    assert res.status_code == 200
    c_res = res.json()
    safe_print(f"   [OK] Completeness Ring Score: {c_res['completeness_percentage']}%")
    safe_print(f"   [OK] Read-Back Card: {c_res['read_it_back_card']['card_text']}")

    # 5. Patient Confirms Extraction ("Read it back" Card)
    print("\n5. Patient Validates Extracted Card ('Yes, correct')...")
    res = session.post(f"{BASE_URL}/v1/intake/sessions/{sess_id}/confirm-extraction/", headers=p_headers, json={"confirmed": True})
    assert res.status_code == 200
    safe_print(f"   [OK] Confirmation Response: {res.json()['message']}")

    # 6. 'Skip' Button
    print("\n6. Patient Uses 'Skip' Button on missing field...")
    res = session.post(f"{BASE_URL}/v1/intake/sessions/{sess_id}/skip-field/", headers=p_headers, json={"field_name": "Medication dosage"})
    assert res.status_code == 200
    safe_print(f"   [OK] Skip Response: {res.json()['message']}")

    # 7. Doctor 'Ask the patient this' Question Queue
    print("\n7. Doctor Queues a Question for Patient ('Ask the patient this')...")
    res = session.post(
        f"{BASE_URL}/v1/doctor/patients/{p_id}/queue-question/",
        headers=d_headers,
        json={"question_text": "What is the exact mg dose printed on your BP tablet box?", "target_field": "Medication dose"}
    )
    assert res.status_code == 200
    safe_print(f"   [OK] Response: {res.json()['message']}")

    # Patient fetches queued questions
    res = session.get(f"{BASE_URL}/v1/patient/queued-questions/", headers=p_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] Patient fetched doctor-queued question: {res.json()[0]['question_text']}")

    # 8. Doctor 'Mark as Reviewed' Checkpoint
    print("\n8. Doctor Sets 'Mark as Reviewed' Baseline Checkpoint...")
    res = session.post(f"{BASE_URL}/v1/doctor/patients/{p_id}/mark-reviewed/", headers=d_headers, json={"notes": "Baseline review completed"})
    assert res.status_code == 200
    safe_print(f"   [OK] Reviewed Checkpoint Saved: {res.json()['reviewed_at']}")

    # 9. Priority Patient List with Change Badges
    print("\n9. Doctor Patient List with Priority Sorting & Change Badges...")
    res = session.get(f"{BASE_URL}/v1/doctor/patients/", headers=d_headers)
    assert res.status_code == 200
    p_item = res.json()[0]
    safe_print(f"   [OK] Top Patient: {p_item['name']} | Safety Flag: {p_item['has_safety_flag']} | Change Count: {p_item['change_count']}")

    # 10. EHR Export Brief
    print("\n10. Doctor Exports Plain-Text Intake Brief for EHR Copy-Paste...")
    res = session.get(f"{BASE_URL}/v1/doctor/patients/{p_id}/export-brief/", headers=d_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] EHR Export Sample:\n{res.json()['export_formatted_text'][:250]}...")

    # 11. Doctor Photo Attachment Viewer
    print("\n11. Doctor Views Patient Photo Attachments...")
    res = session.get(f"{BASE_URL}/v1/doctor/patients/{p_id}/attachments/", headers=d_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] Attachments Found: {len(res.json())} photo(s). File Path: {res.json()[0]['file_path']}")

    # 12. Trust Touch: 'What your doctor sees' Preview
    print("\n12. Patient Trust Touch -- 'What your doctor sees' Preview...")
    res = session.get(f"{BASE_URL}/v1/patient/doctor-view-preview/", headers=p_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] Trust Banner: {res.json()['trust_banner']}")

    # 13. Timeline Filters
    print("\n13. Patient Timeline with Category and Date Filtering...")
    res = session.get(f"{BASE_URL}/v1/patient/timeline/?category=Symptom&days=7", headers=p_headers)
    assert res.status_code == 200
    safe_print(f"   [OK] Filtered Timeline Entries Count: {len(res.json())}")

    print("\n" + "=" * 70)
    print("ALL 13 NEW FEATURE ENDPOINTS AUDITED & PASSED 100% SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    test_new_features()
