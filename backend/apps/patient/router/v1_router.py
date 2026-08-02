import os
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from config.database import get_db
from apps.utils.role_guard import require_patient, verify_patient_self_access
from apps.db_models import (
    User, PatientProfile, SymptomReport, Allergy, MedicalHistory,
    PatientReportedMedication, PatientTimeline, PatientAttachment,
    DoctorQueuedQuestion, IntakeSession, AuditLog
)
from apps.patient.models.v1_model import (
    PatientProfileUpdate, SymptomReportCreate, SymptomReportUpdate, SymptomReportResponse,
    AllergyCreate, AllergyResponse, MedicalHistoryCreate, MedicalHistoryResponse,
    PatientReportedMedicationCreate, PatientReportedMedicationResponse, TimelineEntryResponse,
    QuickUpdateChipRequest, PatientAttachmentResponse, QueuedQuestionResponse
)
from services.embedding_service import store_patient_document_embedding
from services.llm_service import generate_doctor_brief

router = APIRouter()


@router.get("/profile/")
async def get_patient_profile(
    patient: PatientProfile = Depends(verify_patient_self_access),
    current_user: User = Depends(require_patient)
):
    """Get authenticated patient's health profile (PATIENT ONLY)."""
    return {
        "id": patient.id,
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "birthday": current_user.birthday,
        "gender": current_user.gender,
        "blood_group": patient.blood_group,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "medical_notes": patient.medical_notes
    }


@router.put("/profile/")
async def update_patient_profile(
    data: PatientProfileUpdate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Update patient health profile fields."""
    if data.blood_group is not None:
        patient.blood_group = data.blood_group
    if data.emergency_contact_name is not None:
        patient.emergency_contact_name = data.emergency_contact_name
    if data.emergency_contact_phone is not None:
        patient.emergency_contact_phone = data.emergency_contact_phone
    if data.medical_notes is not None:
        patient.medical_notes = data.medical_notes

    db.commit()
    db.refresh(patient)
    return {"message": "Profile updated successfully"}


# ---------------- RESUME PROMPT & QUICK UPDATES ----------------
@router.get("/resume-prompt/")
async def get_resume_prompt(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    RESUME PROMPT: Turns one-off intake into a continuous health assistant.
    Returns: 'Last time you mentioned [Concern]. Has anything changed?'
    """
    last_symptom = db.query(SymptomReport).filter(
        SymptomReport.patient_id == patient.id
    ).order_by(SymptomReport.reported_at.desc()).first()

    if last_symptom:
        prompt_text = f"Welcome back! Last time you mentioned experiencing {last_symptom.concern}. Has anything changed since then?"
    else:
        prompt_text = "Welcome to Clinic Intake Assistant! What symptoms or health updates would you like to report today?"

    return {
        "patient_id": patient.id,
        "last_symptom": last_symptom.concern if last_symptom else None,
        "resume_prompt": prompt_text
    }


@router.post("/quick-update/")
async def quick_update_chip(
    data: QuickUpdateChipRequest,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    QUICK-UPDATE CHIPS: One-tap pre-seeded update for low-literacy / elderly users.
    Options: 'got_worse', 'got_better', 'same', 'new_symptom'
    """
    target_sym = None
    if data.symptom_id:
        target_sym = db.query(SymptomReport).filter(
            SymptomReport.id == data.symptom_id,
            SymptomReport.patient_id == patient.id
        ).first()

    if not target_sym:
        target_sym = db.query(SymptomReport).filter(
            SymptomReport.patient_id == patient.id
        ).order_by(SymptomReport.reported_at.desc()).first()

    sym_name = target_sym.concern if target_sym else "reported condition"
    prev_sev = target_sym.severity if (target_sym and target_sym.severity is not None) else 5

    new_sev = prev_sev
    action_desc = "Quick update submitted"

    if data.chip_type == "got_worse":
        new_sev = min(10, prev_sev + 2)
        action_desc = f"Patient reported symptom '{sym_name}' got worse (Severity increased to {new_sev}/10)."
    elif data.chip_type == "got_better":
        new_sev = max(0, prev_sev - 2)
        action_desc = f"Patient reported symptom '{sym_name}' got better (Severity reduced to {new_sev}/10)."
    elif data.chip_type == "same":
        action_desc = f"Patient reported symptom '{sym_name}' remains unchanged at {prev_sev}/10."
    elif data.chip_type == "new_symptom":
        action_desc = f"Patient selected New Symptom update: {data.note or 'New health concern'}"

    if target_sym and data.chip_type in ["got_worse", "got_better", "same"]:
        target_sym.severity = new_sev
        target_sym.updated_at = datetime.now(timezone.utc)
        db.commit()

    # Timeline entry
    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Symptom",
        action_type="Updated" if target_sym else "Added",
        previous_value=f"Severity: {prev_sev}/10" if target_sym else None,
        new_value=action_desc,
        source="quick_chip"
    )
    db.add(timeline)
    db.commit()

    return {
        "message": "Quick update recorded successfully.",
        "action_description": action_desc,
        "symptom": sym_name,
        "new_severity": new_sev
    }


# ---------------- PHOTO ATTACHMENTS (MEDICATION STRIPS) ----------------
@router.post("/attachments/upload/", response_model=PatientAttachmentResponse)
async def upload_patient_attachment(
    file: UploadFile = File(...),
    category: str = Form("medication_strip"),
    note: str = Form(""),
    session_id: Optional[int] = Form(None),
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    PHOTO ATTACHMENT FOR MEDICATION STRIPS:
    Allows patient to photograph medication boxes/strips.
    Stored as patient-reported attachment for doctor review -- NO SILENT OCR INFERENCE.
    """
    os.makedirs("media/attachments", exist_ok=True)
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"att_{patient.id}_{uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join("media/attachments", unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    attachment = PatientAttachment(
        patient_id=patient.id,
        session_id=session_id,
        file_path=f"media/attachments/{unique_filename}",
        file_name=file.filename,
        category=category,
        note=note or f"Patient uploaded {category} photo"
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    # Timeline entry
    db.add(PatientTimeline(
        patient_id=patient.id,
        category="Attachment",
        action_type="Added",
        previous_value=None,
        new_value=f"Uploaded photo attachment: {file.filename} ({category})",
        source="patient_upload"
    ))
    db.commit()

    return attachment


@router.get("/attachments/", response_model=List[PatientAttachmentResponse])
async def list_patient_attachments(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List uploaded photo attachments for patient."""
    return db.query(PatientAttachment).filter(
        PatientAttachment.patient_id == patient.id
    ).order_by(PatientAttachment.uploaded_at.desc()).all()


# ---------------- DOCTOR QUEUED QUESTIONS & PREVIEW ----------------
@router.get("/queued-questions/", response_model=List[QueuedQuestionResponse])
async def get_queued_questions_for_patient(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Fetch questions queued by doctor for patient ('Ask the patient this')."""
    return db.query(DoctorQueuedQuestion).filter(
        DoctorQueuedQuestion.patient_id == patient.id,
        DoctorQueuedQuestion.status == "pending"
    ).order_by(DoctorQueuedQuestion.created_at.desc()).all()


@router.get("/doctor-view-preview/")
async def get_doctor_view_preview(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    TRUST TOUCH: 'WHAT YOUR DOCTOR SEES' PREVIEW
    Read-only render of the intake brief being sent to doctor.
    Builds trust and clarifies that doctor's clinical notes are private.
    """
    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient.id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient.id).all()
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient.id).all()
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient.id).all()

    sym_list = [{"concern": s.concern, "severity": s.severity, "duration": s.duration, "pattern": s.pattern} for s in symptoms]
    med_list = [{"medication_name": m.medication_name, "dosage": m.dosage, "frequency": m.frequency} for m in meds]

    brief = generate_doctor_brief(
        symptoms=sym_list,
        medications=med_list,
        history=[{"condition_name": h.condition_name} for h in history],
        allergies=[{"allergen": a.allergen} for a in allergies],
        missing_info=["Check medication dosage if unverified"]
    )

    return {
        "patient_id": patient.id,
        "trust_banner": "This is an exact preview of the Patient Intake Brief visible to your doctor.",
        "privacy_notice": "Doctor clinical assessments and private notes are maintained separately for professional medical documentation.",
        "brief_markdown": brief
    }


# ---------------- SYMPTOMS ----------------
@router.post("/symptoms/", response_model=SymptomReportResponse)
async def report_symptom(
    data: SymptomReportCreate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Report a new symptom."""
    symptom = SymptomReport(
        patient_id=patient.id,
        concern=data.concern,
        severity=data.severity,
        duration=data.duration,
        pattern=data.pattern,
        source_text=data.source_text or data.concern
    )
    db.add(symptom)
    db.commit()
    db.refresh(symptom)

    new_val = f"Concern: {data.concern}"
    if data.severity is not None:
        new_val += f" | Severity: {data.severity}/10"
    if data.duration:
        new_val += f" | Duration: {data.duration}"

    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Symptom",
        action_type="Added",
        previous_value=None,
        new_value=new_val,
        source="patient_input"
    )
    db.add(timeline)
    db.commit()

    store_patient_document_embedding(
        db, patient.id, "symptom", new_val, {"symptom_id": symptom.id}
    )

    return symptom


@router.put("/symptoms/{symptom_id}/", response_model=SymptomReportResponse)
async def update_symptom(
    symptom_id: int,
    data: SymptomReportUpdate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Update existing symptom severity, duration, or pattern (Preserves timeline)."""
    symptom = db.query(SymptomReport).filter(
        SymptomReport.id == symptom_id,
        SymptomReport.patient_id == patient.id
    ).first()

    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom report not found.")

    prev_val = f"Severity: {symptom.severity}/10 | Duration: {symptom.duration} | Pattern: {symptom.pattern}"

    if data.severity is not None:
        symptom.severity = data.severity
    if data.duration is not None:
        symptom.duration = data.duration
    if data.pattern is not None:
        symptom.pattern = data.pattern
    if data.status is not None:
        symptom.status = data.status

    db.commit()
    db.refresh(symptom)

    new_val = f"Severity: {symptom.severity}/10 | Duration: {symptom.duration} | Pattern: {symptom.pattern}"

    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Symptom",
        action_type="Updated",
        previous_value=prev_val,
        new_value=new_val,
        source="patient_input"
    )
    db.add(timeline)
    db.commit()

    return symptom


@router.get("/symptoms/", response_model=List[SymptomReportResponse])
async def list_symptoms(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List all reported symptoms for the patient."""
    return db.query(SymptomReport).filter(
        SymptomReport.patient_id == patient.id
    ).order_by(SymptomReport.reported_at.desc()).all()


# ---------------- ALLERGIES ----------------
@router.post("/allergies/", response_model=AllergyResponse)
async def add_allergy(
    data: AllergyCreate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Report an allergy."""
    allergy = Allergy(
        patient_id=patient.id,
        allergen=data.allergen,
        reaction=data.reaction or "",
        severity=data.severity or "Unknown"
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)

    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Allergy",
        action_type="Added",
        previous_value=None,
        new_value=f"Allergen: {data.allergen} | Reaction: {data.reaction}",
        source="patient_input"
    )
    db.add(timeline)
    db.commit()

    store_patient_document_embedding(
        db, patient.id, "allergy", f"Allergy: {data.allergen}, Reaction: {data.reaction}"
    )

    return allergy


@router.get("/allergies/", response_model=List[AllergyResponse])
async def list_allergies(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List reported allergies."""
    return db.query(Allergy).filter(Allergy.patient_id == patient.id).all()


# ---------------- MEDICAL HISTORY ----------------
@router.post("/medical-history/", response_model=MedicalHistoryResponse)
async def add_medical_history(
    data: MedicalHistoryCreate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Add medical history item."""
    history = MedicalHistory(
        patient_id=patient.id,
        condition_name=data.condition_name,
        diagnosed_year=data.diagnosed_year or "",
        notes=data.notes or ""
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Medical History",
        action_type="Added",
        previous_value=None,
        new_value=f"Condition: {data.condition_name} ({data.diagnosed_year})",
        source="patient_input"
    )
    db.add(timeline)
    db.commit()

    store_patient_document_embedding(
        db, patient.id, "medical_history", f"History: {data.condition_name}, Notes: {data.notes}"
    )

    return history


@router.get("/medical-history/", response_model=List[MedicalHistoryResponse])
async def list_medical_history(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List medical history."""
    return db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient.id).all()


# ---------------- PATIENT-REPORTED MEDICATIONS ----------------
@router.post("/medications/", response_model=PatientReportedMedicationResponse)
async def report_medication(
    data: PatientReportedMedicationCreate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Report a medication currently being taken (PATIENT-REPORTED ONLY)."""
    med = PatientReportedMedication(
        patient_id=patient.id,
        medication_name=data.medication_name,
        dosage=data.dosage or "Not provided",
        frequency=data.frequency or "Not provided",
        purpose_reported=data.purpose_reported or "",
        as_reported_text=data.as_reported_text or f"Patient reports taking {data.medication_name}"
    )
    db.add(med)
    db.commit()
    db.refresh(med)

    new_val = f"Medication: {data.medication_name} | Dose: {data.dosage} | Freq: {data.frequency}"
    timeline = PatientTimeline(
        patient_id=patient.id,
        category="Patient-Reported Medication",
        action_type="Added",
        previous_value=None,
        new_value=new_val,
        source="patient_input"
    )
    db.add(timeline)
    db.commit()

    store_patient_document_embedding(
        db, patient.id, "medication", new_val
    )

    return med


@router.get("/medications/", response_model=List[PatientReportedMedicationResponse])
async def list_patient_medications(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List patient-reported medications."""
    return db.query(PatientReportedMedication).filter(
        PatientReportedMedication.patient_id == patient.id
    ).all()


# ---------------- TIMELINE WITH FILTERING ----------------
@router.get("/timeline/", response_model=List[TimelineEntryResponse])
async def get_patient_timeline(
    category: Optional[str] = Query(None, description="Filter by category: Symptom, Medication, Allergy, Medical History, Attachment"),
    days: Optional[int] = Query(None, description="Filter timeline entries from the last N days (e.g. 7)"),
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    Get patient's chronological change history timeline.
    Supports filtering by category and date range (last N days).
    """
    query = db.query(PatientTimeline).filter(PatientTimeline.patient_id == patient.id)

    if category:
        query = query.filter(PatientTimeline.category.ilike(f"%{category}%"))

    if days and days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(PatientTimeline.timestamp >= cutoff)

    return query.order_by(PatientTimeline.timestamp.desc()).all()
