from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ClinicalAssessmentCreate(BaseModel):
    clinical_notes: str = Field(..., description="Doctor's clinical assessment notes")
    diagnosis: Optional[str] = Field(None, description="Doctor diagnosis")
    treatment_plan: Optional[str] = Field(None, description="Treatment plan")
    follow_up_instructions: Optional[str] = Field(None, description="Instructions for patient")


class ClinicianPrescriptionCreate(BaseModel):
    medication_name: str = Field(..., max_length=150)
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=100)
    instructions: Optional[str] = ""


class DoctorNoteCreate(BaseModel):
    note_text: str = Field(..., description="Private doctor note")


class QueueQuestionCreate(BaseModel):
    question_text: str = Field(..., description="Question for patient e.g. 'What is your exact BP medication dose?'")
    target_field: Optional[str] = Field("General", max_length=100)


class MarkReviewedCreate(BaseModel):
    notes: Optional[str] = Field("", description="Doctor's review notes")


class PatientListItem(BaseModel):
    patient_id: int
    user_id: int
    name: str
    username: str
    phone: Optional[str]
    birthday: Optional[str]
    gender: Optional[str]
    blood_group: Optional[str]
    has_safety_flag: bool
    change_count: int = Field(0, description="Number of new/updated items since last review")
    last_reviewed_at: Optional[datetime] = None
    last_update: Optional[datetime] = None

    class Config:
        from_attributes = True


class WhatChangedResponse(BaseModel):
    patient_id: int
    last_reviewed_at: Optional[datetime]
    new_items: List[str]
    updated_items: List[str]
    unchanged_items: List[str]
    summary: str


class ClinicalAssessmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    clinical_notes: str
    diagnosis: Optional[str]
    treatment_plan: Optional[str]
    follow_up_instructions: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ClinicianPrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: str
    frequency: str
    instructions: Optional[str]
    prescribed_at: datetime

    class Config:
        from_attributes = True


class DoctorNoteResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExportBriefResponse(BaseModel):
    patient_id: int
    patient_name: str
    export_formatted_text: str
