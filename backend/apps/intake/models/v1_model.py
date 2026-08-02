from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IntakeMessageCreate(BaseModel):
    message: str = Field(..., description="Natural language input from patient e.g. 'I have chest pain for 2 days'")
    action: Optional[str] = Field("chat", description="'chat' or 'skip'")
    skip_field: Optional[str] = Field(None, description="Field name being skipped by patient")


class ConfirmationCardRequest(BaseModel):
    confirmed: bool = Field(..., description="True if patient confirms extracted facts are correct, False if corrections needed")
    corrections: Optional[str] = Field("", description="Patient's text correction if confirmed=False")


class SkipFieldRequest(BaseModel):
    field_name: str = Field(..., description="Field name to skip e.g. 'Medication dosage'")


class IntakeSessionResponse(BaseModel):
    id: int
    patient_id: int
    status: str
    safety_flag: bool
    safety_message: Optional[str]
    structured_data: Dict[str, Any]
    summary_generated: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    session_id: int
    sender: str
    content: str
    extracted_json: Optional[Dict[str, Any]]
    source_reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class IntakeChatResponse(BaseModel):
    session_id: int
    ai_response: str
    safety_flag: bool
    safety_message: Optional[str]
    extracted_data: Dict[str, Any]
    missing_information: List[str]
    followup_question: Optional[str]
    completeness_percentage: int = Field(..., description="Completeness ring metric (0-100%)")
    read_it_back_card: Dict[str, Any] = Field(..., description="'Read it back' confirmation card payload")
