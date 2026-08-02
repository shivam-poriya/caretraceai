"""
Seed script for synthetic demo patient and doctor accounts.
Run: python -m scripts.seed_data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SessionLocal, init_db
from apps.db_models import (
    User, PatientProfile, DoctorProfile, DoctorPatientAssignment,
    SymptomReport, PatientReportedMedication, Allergy, MedicalHistory,
    PatientTimeline, UserRole
)
from apps.custom_auth.utils import get_password_hash


def seed():
    init_db()
    db = SessionLocal()

    try:
        print("[+] Seeding Clinic Intake Assistant demo data...")

        # 1. Create Patient User
        patient_user = db.query(User).filter(User.username == "patient_demo").first()
        if not patient_user:
            patient_user = User(
                username="patient_demo",
                email="patient@example.com",
                password=get_password_hash("Password@123"),
                role=UserRole.PATIENT.value,
                first_name="Ramesh",
                last_name="Patel",
                phone="+91 9876543210",
                birthday="1980-05-15",
                gender="Male",
                address="Ahmedabad, Gujarat"
            )
            db.add(patient_user)
            db.commit()
            db.refresh(patient_user)

        # Patient Profile
        patient_prof = db.query(PatientProfile).filter(PatientProfile.user_id == patient_user.id).first()
        if not patient_prof:
            patient_prof = PatientProfile(
                user_id=patient_user.id,
                blood_group="B+",
                emergency_contact_name="Savitri Patel",
                emergency_contact_phone="+91 9876543211"
            )
            db.add(patient_prof)
            db.commit()
            db.refresh(patient_prof)

        # 2. Create Doctor User
        doctor_user = db.query(User).filter(User.username == "doctor_demo").first()
        if not doctor_user:
            doctor_user = User(
                username="doctor_demo",
                email="doctor@example.com",
                password=get_password_hash("Password@123"),
                role=UserRole.DOCTOR.value,
                first_name="Dr. Ananya",
                last_name="Sharma",
                phone="+91 9123456789",
                organization_name="City General Hospital"
            )
            db.add(doctor_user)
            db.commit()
            db.refresh(doctor_user)

        # Doctor Profile
        doctor_prof = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_user.id).first()
        if not doctor_prof:
            doctor_prof = DoctorProfile(
                user_id=doctor_user.id,
                specialty="Cardiology / Internal Medicine",
                license_number="MCI-2015-88492"
            )
            db.add(doctor_prof)
            db.commit()
            db.refresh(doctor_prof)

        # 3. Doctor-Patient Assignment
        assign = db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.doctor_id == doctor_prof.id,
            DoctorPatientAssignment.patient_id == patient_prof.id
        ).first()
        if not assign:
            assign = DoctorPatientAssignment(
                doctor_id=doctor_prof.id,
                patient_id=patient_prof.id,
                is_active=True
            )
            db.add(assign)
            db.commit()

        # 4. Seed Initial Patient Reported Facts (2 Aug scenario)
        sym1 = db.query(SymptomReport).filter(SymptomReport.patient_id == patient_prof.id).first()
        if not sym1:
            sym1 = SymptomReport(
                patient_id=patient_prof.id,
                concern="Headache",
                severity=4,
                duration="2 days",
                pattern="Continuous dull ache",
                source_text="I've been having headaches since yesterday."
            )
            db.add(sym1)

            med1 = PatientReportedMedication(
                patient_id=patient_prof.id,
                medication_name="BP Medication (Unspecified)",
                dosage="Not provided",
                frequency="Once daily",
                as_reported_text="I take BP medication daily."
            )
            db.add(med1)

            alg1 = Allergy(
                patient_id=patient_prof.id,
                allergen="Penicillin",
                reaction="Skin rash",
                severity="Moderate"
            )
            db.add(alg1)

            t1 = PatientTimeline(
                patient_id=patient_prof.id,
                category="Symptom",
                action_type="Added",
                previous_value=None,
                new_value="Headache reported — severity 4/10, duration 2 days",
                source="patient_input"
            )
            db.add(t1)

            t2 = PatientTimeline(
                patient_id=patient_prof.id,
                category="Patient-Reported Medication",
                action_type="Added",
                previous_value=None,
                new_value="BP medication (unspecified dose)",
                source="patient_input"
            )
            db.add(t2)

            db.commit()

        print("[+] Demo data seeded successfully!")
        print("  - Patient Login: username='patient_demo', password='Password@123'")
        print("  - Doctor Login:  username='doctor_demo',  password='Password@123'")

    except Exception as e:
        print(f"[-] Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
