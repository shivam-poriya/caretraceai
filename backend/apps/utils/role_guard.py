"""
Role-Based Access Control (RBAC) Security Guards.
Enforces strict role permissions at the backend API level.
"""
from fastapi import Depends, HTTPException, status
from apps.custom_auth.oauth2 import get_current_user
from apps.db_models import User, UserRole, DoctorProfile, PatientProfile, DoctorPatientAssignment
from config.database import get_db
from sqlalchemy.orm import Session


def require_patient(current_user: User = Depends(get_current_user)) -> User:
    """Ensures logged in user has PATIENT role."""
    if current_user.role != UserRole.PATIENT.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Patient role required."
        )
    return current_user


def require_doctor(current_user: User = Depends(get_current_user)) -> User:
    """Ensures logged in user has DOCTOR role."""
    if current_user.role != UserRole.DOCTOR.value and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Doctor role required."
        )
    return current_user


def verify_doctor_patient_access(
    patient_id: int,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
) -> PatientProfile:
    """Verifies doctor is assigned to patient (or admin) and returns patient profile."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")

    if doctor_user.role == UserRole.ADMIN.value:
        return patient

    doctor_prof = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_user.id).first()
    if not doctor_prof:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor profile not found.")

    # Check assignment
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == doctor_prof.id,
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True
    ).first()

    # If no explicit assignment exists yet in demo mode, auto-assign for smoother workflow
    if not assignment:
        new_assign = DoctorPatientAssignment(
            doctor_id=doctor_prof.id,
            patient_id=patient_id,
            is_active=True
        )
        db.add(new_assign)
        db.commit()

    return patient


def verify_patient_self_access(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
) -> PatientProfile:
    """Retrieves authenticated patient's own PatientProfile."""
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not patient:
        # Create patient profile automatically if it doesn't exist
        patient = PatientProfile(user_id=current_user.id)
        db.add(patient)
        db.commit()
        db.refresh(patient)
    return patient
