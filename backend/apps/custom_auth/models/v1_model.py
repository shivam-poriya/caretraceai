from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    username: str = Field(..., description="Please Provide a unique Username.", max_length=32, min_length=3)
    email: EmailStr = Field(..., description="Please Provide a unique email.", max_length=70, min_length=5)
    password: str = Field(..., description="Please Provide a password ex.Example@123.", max_length=32, min_length=8)
    role: Optional[str] = Field("patient", description="Role: 'patient' or 'doctor'")
    first_name: Optional[str] = Field("", max_length=70)
    last_name: Optional[str] = Field("", max_length=70)
    phone: Optional[str] = Field("", max_length=70)
    birthday: Optional[str] = Field("", max_length=70)
    gender: Optional[str] = Field("", max_length=20)
    address: Optional[str] = Field("", max_length=255)
    specialty: Optional[str] = Field("General Physician", max_length=100)  # for doctor role


class UserLogin(BaseModel):
    username: str = Field(..., description="Please Provide a unique Username.", max_length=32, min_length=3)
    password: str = Field(..., description="Please Provide a password.", max_length=32, min_length=8)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")


class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    new_password: str = Field(..., min_length=8, max_length=32, description="New password")
