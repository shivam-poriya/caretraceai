from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PatientProfileUpdate(BaseModel):
    blood_group: Optional[str] = Field(None, max_length=10)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    medical_notes: Optional[str] = None


class SymptomReportCreate(BaseModel):
    concern: str = Field(..., description="Reported symptom name e.g. Chest pain", max_length=150)
    severity: Optional[int] = Field(None, ge=0, le=10, description="Severity 0-10")
    duration: Optional[str] = Field("Not provided", max_length=100)
    pattern: Optional[str] = Field("Not provided", max_length=100)
    source_text: Optional[str] = None


class SymptomReportUpdate(BaseModel):
    severity: Optional[int] = Field(None, ge=0, le=10)
    duration: Optional[str] = Field(None, max_length=100)
    pattern: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)


class AllergyCreate(BaseModel):
    allergen: str = Field(..., max_length=150)
    reaction: Optional[str] = Field("", max_length=200)
    severity: Optional[str] = Field("Unknown", max_length=50)


class MedicalHistoryCreate(BaseModel):
    condition_name: str = Field(..., max_length=150)
    diagnosed_year: Optional[str] = Field("", max_length=50)
    notes: Optional[str] = ""


class PatientReportedMedicationCreate(BaseModel):
    medication_name: str = Field(..., max_length=150)
    dosage: Optional[str] = Field("Not provided", max_length=100)
    frequency: Optional[str] = Field("Not provided", max_length=100)
    purpose_reported: Optional[str] = Field("", max_length=200)
    as_reported_text: Optional[str] = ""


class QuickUpdateChipRequest(BaseModel):
    chip_type: str = Field(..., description="Choice: 'got_worse', 'got_better', 'same', 'new_symptom'")
    symptom_id: Optional[int] = Field(None, description="Target symptom ID if updating existing symptom")
    note: Optional[str] = Field("", description="Optional short patient note")


# Response schemas
class SymptomReportResponse(BaseModel):
    id: int
    concern: str
    severity: Optional[int]
    duration: Optional[str]
    pattern: Optional[str]
    status: str
    reported_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AllergyResponse(BaseModel):
    id: int
    allergen: str
    reaction: Optional[str]
    severity: Optional[str]
    reported_at: datetime

    class Config:
        from_attributes = True


class MedicalHistoryResponse(BaseModel):
    id: int
    condition_name: str
    diagnosed_year: Optional[str]
    notes: Optional[str]
    reported_at: datetime

    class Config:
        from_attributes = True


class PatientReportedMedicationResponse(BaseModel):
    id: int
    medication_name: str
    dosage: Optional[str]
    frequency: Optional[str]
    purpose_reported: Optional[str]
    as_reported_text: Optional[str]
    reported_at: datetime

    class Config:
        from_attributes = True


class TimelineEntryResponse(BaseModel):
    id: int
    category: str
    action_type: str
    previous_value: Optional[str]
    new_value: str
    source: str
    conversation_ref: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class PatientAttachmentResponse(BaseModel):
    id: int
    patient_id: int
    session_id: Optional[int]
    file_path: str
    file_name: str
    category: str
    note: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class QueuedQuestionResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    question_text: str
    target_field: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
