import os
import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
import shutil
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File, Request, BackgroundTasks
from apps.custom_auth.models.v1_model import (
    UserLogin, BaseUser as User, UserUpdate,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from apps.custom_auth.utils import (
    get_password_hash,
    pwd_context,
    create_access_token,
    create_refresh_token,
)
from apps.utils.send_email import register_user_send_email, send_otp_email
from apps.utils.permission import verify_user_token
from config.database import SessionLocal
from config.settings import base as settings
from jinja2 import Environment, FileSystemLoader, select_autoescape
from apps.db_models import User as DBUser, PatientProfile, DoctorProfile, UserRole
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()


@router.get("/test")
async def custom_auth_root():
    return {"message": "Custom Auth API Root"}


@router.post("/register/")
async def register_user(
        user: User,
        background_tasks: BackgroundTasks
):
    session = SessionLocal()
    try:
        existing_user = session.query(DBUser).filter(
            (DBUser.username == user.username) | (DBUser.email == user.email)
        ).first()
        if existing_user:
            if existing_user.username == user.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            if existing_user.email == user.email:
                raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = get_password_hash(user.password)
        role = user.role.lower() if user.role and user.role.lower() in [UserRole.PATIENT.value, UserRole.DOCTOR.value] else UserRole.PATIENT.value

        db_user = DBUser(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role=role,
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            phone=user.phone or "",
            birthday=user.birthday or "",
            gender=user.gender or "",
            address=user.address or ""
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        user_id = db_user.id

        if role == UserRole.PATIENT.value:
            patient_prof = PatientProfile(user_id=user_id)
            session.add(patient_prof)
        elif role == UserRole.DOCTOR.value:
            doctor_prof = DoctorProfile(
                user_id=user_id,
                specialty=user.specialty or "General Physician"
            )
            session.add(doctor_prof)

        session.commit()
    finally:
        session.close()

    return {
        "message": "User registered successfully",
        "user_id": str(user_id),
        "role": role
    }


@router.post("/login/")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    session = SessionLocal()
    try:
        user = session.query(DBUser).filter(
            (DBUser.username == form_data.username) | (DBUser.email == form_data.username)
        ).first()

        if not user or not pwd_context.verify(form_data.password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )

        patient_id = None
        doctor_id = None

        if user.role == UserRole.PATIENT.value:
            patient = session.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
            if not patient:
                patient = PatientProfile(user_id=user.id)
                session.add(patient)
                session.commit()
                session.refresh(patient)
            patient_id = patient.id
        elif user.role == UserRole.DOCTOR.value:
            doctor = session.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
            if not doctor:
                doctor = DoctorProfile(user_id=user.id, specialty="General Physician")
                session.add(doctor)
                session.commit()
                session.refresh(doctor)
            doctor_id = doctor.id

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "refresh_token": refresh_token,
        }
    finally:
        session.close()


@router.get("/get-user-profile/")
async def read_protected(
        request: Request, current_user: dict = Depends(verify_user_token)
):
    session = SessionLocal()
    try:
        user = session.query(DBUser).filter(DBUser.id == int(current_user.get("_id"))).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "address": user.address,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "organization_name": user.organization_name,
            "location": user.location,
            "phone": user.phone,
            "birthday": user.birthday,
            "gender": user.gender,
            "profile_photo": user.profile_photo,
        }
        if user.profile_photo:
            user_data["profile_photo_path"] = (
                f"{request.base_url}media/user_profile/{user.profile_photo}"
            )
        return user_data
    finally:
        session.close()


# ---------------- FORGOT PASSWORD / OTP ENDPOINTS ----------------
@router.post("/forgot-password/")
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks
):
    """
    Step 1: Patient or Doctor requests password reset.
    Generates a 6-digit OTP, stores it with 10-minute expiry, and emails it.
    """
    session = SessionLocal()
    try:
        user = session.query(DBUser).filter(DBUser.email == data.email).first()
        if not user:
            return {"message": "If an account with that email exists, an OTP has been sent."}

        # Generate 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

        user.reset_otp = otp
        user.reset_otp_expiry = expiry
        session.commit()

        # Send OTP email in background
        background_tasks.add_task(send_otp_email, user.email, otp)

        return {
            "message": "If an account with that email exists, an OTP has been sent to your email.",
            "email": user.email
        }
    finally:
        session.close()


@router.post("/verify-otp/")
async def verify_otp(data: VerifyOTPRequest):
    """
    Step 2: Verify if the submitted OTP is valid and not expired.
    """
    session = SessionLocal()
    try:
        user = session.query(DBUser).filter(DBUser.email == data.email).first()
        if not user or not user.reset_otp or user.reset_otp != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP code")

        if user.reset_otp_expiry:
            expiry_utc = user.reset_otp_expiry.replace(tzinfo=timezone.utc) if user.reset_otp_expiry.tzinfo is None else user.reset_otp_expiry
            if expiry_utc < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

        return {
            "message": "OTP verified successfully. You may now reset your password.",
            "email": user.email,
            "otp_valid": True
        }
    finally:
        session.close()


@router.post("/reset-password/")
async def reset_password(data: ResetPasswordRequest):
    """
    Step 3: Reset user password using verified OTP.
    """
    session = SessionLocal()
    try:
        user = session.query(DBUser).filter(DBUser.email == data.email).first()
        if not user or not user.reset_otp or user.reset_otp != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP code")

        if user.reset_otp_expiry:
            expiry_utc = user.reset_otp_expiry.replace(tzinfo=timezone.utc) if user.reset_otp_expiry.tzinfo is None else user.reset_otp_expiry
            if expiry_utc < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

        # Update password
        user.password = get_password_hash(data.new_password)
        # Clear used OTP
        user.reset_otp = None
        user.reset_otp_expiry = None

        session.commit()

        return {
            "message": "Password reset successfully. You can now log in with your new password."
        }
    finally:
        session.close()
