from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    email = Column(String(70), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.PATIENT.value, nullable=False)
    
    first_name = Column(String(70), default="")
    last_name = Column(String(70), default="")
    phone = Column(String(70), nullable=True)
    birthday = Column(String(70), default="")
    gender = Column(String(20), default="")
    address = Column(String(255), default="")
    organization_name = Column(String(70), default="")
    location = Column(String(70), default="")
    profile_photo = Column(String(255), nullable=True)
    
    reset_otp = Column(String(6), nullable=True)
    reset_otp_expiry = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    blood_group = Column(String(10), default="")
    emergency_contact_name = Column(String(100), default="")
    emergency_contact_phone = Column(String(50), default="")
    medical_notes = Column(Text, default="")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="patient_profile")
    symptoms = relationship("SymptomReport", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    medical_history = relationship("MedicalHistory", back_populates="patient", cascade="all, delete-orphan")
    reported_medications = relationship("PatientReportedMedication", back_populates="patient", cascade="all, delete-orphan")
    intake_sessions = relationship("IntakeSession", back_populates="patient", cascade="all, delete-orphan")
    timeline_entries = relationship("PatientTimeline", back_populates="patient", cascade="all, delete-orphan")
    clinical_assessments = relationship("ClinicalAssessment", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("ClinicianPrescription", back_populates="patient", cascade="all, delete-orphan")
    doctor_notes = relationship("DoctorNote", back_populates="patient", cascade="all, delete-orphan")


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialty = Column(String(100), default="General Physician")
    license_number = Column(String(50), default="")
    hospital_affiliation = Column(String(150), default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="doctor_profile")
    assignments = relationship("DoctorPatientAssignment", back_populates="doctor", cascade="all, delete-orphan")


class DoctorPatientAssignment(Base):
    __tablename__ = "doctor_patient_assignments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    doctor = relationship("DoctorProfile", back_populates="assignments")
    patient = relationship("PatientProfile")


class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    concern = Column(String(150), nullable=False)
    severity = Column(Integer, nullable=True)  # Scale 0-10
    duration = Column(String(100), nullable=True)
    pattern = Column(String(100), nullable=True)  # e.g., continuous, comes and goes
    source_text = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, resolved, updated
    
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", back_populates="symptoms")


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    allergen = Column(String(150), nullable=False)
    reaction = Column(String(200), default="")
    severity = Column(String(50), default="Unknown")
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="allergies")


class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    condition_name = Column(String(150), nullable=False)
    diagnosed_year = Column(String(50), default="")
    notes = Column(Text, default="")
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="medical_history")


class PatientReportedMedication(Base):
    """MEDICATION REPORTED BY PATIENT - STRICTLY SEPARATE FROM DOCTOR PRESCRIPTION"""
    __tablename__ = "patient_reported_medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    medication_name = Column(String(150), nullable=False)
    dosage = Column(String(100), default="Not provided")
    frequency = Column(String(100), default="Not provided")
    purpose_reported = Column(String(200), default="")
    as_reported_text = Column(Text, default="")
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="reported_medications")


class IntakeSession(Base):
    __tablename__ = "intake_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="active")  # active, completed, flag_raised
    safety_flag = Column(Boolean, default=False)
    safety_message = Column(Text, nullable=True)
    structured_data = Column(JSON, default=dict)
    summary_generated = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", back_populates="intake_sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("intake_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False)  # "patient" or "ai"
    content = Column(Text, nullable=False)
    extracted_json = Column(JSON, nullable=True)
    source_reference = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("IntakeSession", back_populates="messages")


class PatientTimeline(Base):
    """Chronological patient health history timeline - Never overwritten"""
    __tablename__ = "patient_timeline"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # Symptom, Medication, Allergy, History, AI_Intake
    action_type = Column(String(50), nullable=False)  # Added, Updated, Resolved
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=False)
    source = Column(String(50), default="patient_input")  # patient_input, ai_extracted, doctor_entry
    conversation_ref = Column(String(100), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="timeline_entries")


class ClinicalAssessment(Base):
    """DOCTOR ONLY - Private Clinical Assessment & Diagnosis"""
    __tablename__ = "clinical_assessments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    clinical_notes = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    follow_up_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", back_populates="clinical_assessments")
    doctor = relationship("DoctorProfile")


class ClinicianPrescription(Base):
    """DOCTOR ONLY - Clinician Prescribed Medication"""
    __tablename__ = "clinician_prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    medication_name = Column(String(150), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    instructions = Column(Text, default="")
    prescribed_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="prescriptions")
    doctor = relationship("DoctorProfile")


class DoctorNote(Base):
    """DOCTOR ONLY - Private Notes"""
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("PatientProfile", back_populates="doctor_notes")
    doctor = relationship("DoctorProfile")


class DocumentEmbedding(Base):
    """pgvector Store for Patient RAG Embeddings"""
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # symptom, conversation, history, medication
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # 384 dimensions for all-MiniLM-L6-v2
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """System Audit Trail"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    role = Column(String(20), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(150), nullable=False)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class PatientAttachment(Base):
    """Patient Photo Attachments (e.g., medication strips, rash photos) - No automatic AI OCR inference"""
    __tablename__ = "patient_attachments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("intake_sessions.id", ondelete="SET NULL"), nullable=True)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(150), nullable=False)
    category = Column(String(50), default="medication_strip")  # medication_strip, rash, document
    note = Column(Text, default="")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class DoctorReviewCheckpoint(Base):
    """Doctor-set baseline review checkpoint for What Changed diffing"""
    __tablename__ = "doctor_review_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, default="")
    snapshot_json = Column(JSON, default=dict)


class DoctorQueuedQuestion(Base):
    """Doctor-queued questions for patient ('Ask the patient this')"""
    __tablename__ = "doctor_queued_questions"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    target_field = Column(String(100), default="General")  # e.g., Medication dose
    status = Column(String(20), default="pending")  # pending, answered, skipped
    created_at = Column(DateTime(timezone=True), server_default=func.now())

