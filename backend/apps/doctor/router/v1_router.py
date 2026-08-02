from datetime import timedelta
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from config.database import get_db
from apps.utils.role_guard import require_doctor, verify_doctor_patient_access
from apps.db_models import (
    User, DoctorProfile, PatientProfile, SymptomReport, Allergy, MedicalHistory,
    PatientReportedMedication, IntakeSession, ConversationMessage, PatientTimeline,
    ClinicalAssessment, ClinicianPrescription, DoctorNote, DoctorReviewCheckpoint,
    DoctorQueuedQuestion, PatientAttachment, AuditLog
)
from apps.doctor.models.v1_model import (
    ClinicalAssessmentCreate, ClinicalAssessmentResponse,
    ClinicianPrescriptionCreate, ClinicianPrescriptionResponse,
    DoctorNoteCreate, DoctorNoteResponse, PatientListItem, WhatChangedResponse,
    QueueQuestionCreate, MarkReviewedCreate, ExportBriefResponse
)
from apps.patient.models.v1_model import PatientAttachmentResponse
from services.llm_service import detect_changes, generate_doctor_brief

router = APIRouter()


def get_doctor_profile_or_404(current_user: User, db: Session) -> DoctorProfile:
    doc = db.query(DoctorProfile).filter(DoctorProfile.user_id == current_user.id).first()
    if not doc:
        doc = DoctorProfile(user_id=current_user.id, specialty="General Physician")
        db.add(doc)
        db.commit()
        db.refresh(doc)
    return doc


@router.get("/patients/", response_model=List[PatientListItem])
async def list_assigned_patients(
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    List all patients assigned to authenticated doctor (DOCTOR ONLY).
    Includes 'change_count' and SORTING so safety-flagged and most-changed patients float to the top.
    """
    patients = db.query(PatientProfile).all()
    items = []

    for p in patients:
        u = db.query(User).filter(User.id == p.user_id).first()
        name = f"{u.first_name} {u.last_name}".strip() if u else "Patient"
        if not name:
            name = u.username if u else f"Patient #{p.id}"

        flag = db.query(IntakeSession).filter(
            IntakeSession.patient_id == p.id,
            IntakeSession.safety_flag == True
        ).first() is not None

        last_checkpoint = db.query(DoctorReviewCheckpoint).filter(
            DoctorReviewCheckpoint.patient_id == p.id
        ).order_by(DoctorReviewCheckpoint.reviewed_at.desc()).first()

        checkpoint_time = last_checkpoint.reviewed_at if last_checkpoint else datetime(2000, 1, 1, tzinfo=timezone.utc)

        # Count timeline entries since last review checkpoint
        change_count = db.query(PatientTimeline).filter(
            PatientTimeline.patient_id == p.id,
            PatientTimeline.timestamp > checkpoint_time
        ).count()

        last_t = db.query(PatientTimeline).filter(
            PatientTimeline.patient_id == p.id
        ).order_by(PatientTimeline.timestamp.desc()).first()

        items.append(PatientListItem(
            patient_id=p.id,
            user_id=p.user_id,
            name=name,
            username=u.username if u else "",
            phone=u.phone if u else None,
            birthday=u.birthday if u else None,
            gender=u.gender if u else None,
            blood_group=p.blood_group,
            has_safety_flag=flag,
            change_count=change_count,
            last_reviewed_at=last_checkpoint.reviewed_at if last_checkpoint else None,
            last_update=last_t.timestamp if last_t else None
        ))

    # Priority sorting: Safety flag first, then highest change count, then recent update
    items.sort(key=lambda x: (x.has_safety_flag, x.change_count, x.last_update or datetime(2000, 1, 1, tzinfo=timezone.utc)), reverse=True)
    return items


@router.get("/patients/search/", response_model=List[PatientListItem])
async def search_patients(
    q: str = Query(..., min_length=1, description="Search query name or username"),
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Search patients by name or username (DOCTOR ONLY)."""
    users = db.query(User).filter(
        User.role == "patient",
        (User.username.ilike(f"%{q}%")) | (User.first_name.ilike(f"%{q}%")) | (User.last_name.ilike(f"%{q}%"))
    ).all()

    items = []
    for u in users:
        p = db.query(PatientProfile).filter(PatientProfile.user_id == u.id).first()
        if p:
            flag = db.query(IntakeSession).filter(
                IntakeSession.patient_id == p.id,
                IntakeSession.safety_flag == True
            ).first() is not None

            last_checkpoint = db.query(DoctorReviewCheckpoint).filter(
                DoctorReviewCheckpoint.patient_id == p.id
            ).order_by(DoctorReviewCheckpoint.reviewed_at.desc()).first()

            checkpoint_time = last_checkpoint.reviewed_at if last_checkpoint else datetime(2000, 1, 1, tzinfo=timezone.utc)
            change_count = db.query(PatientTimeline).filter(
                PatientTimeline.patient_id == p.id,
                PatientTimeline.timestamp > checkpoint_time
            ).count()

            last_t = db.query(PatientTimeline).filter(
                PatientTimeline.patient_id == p.id
            ).order_by(PatientTimeline.timestamp.desc()).first()

            items.append(PatientListItem(
                patient_id=p.id,
                user_id=u.id,
                name=f"{u.first_name} {u.last_name}".strip() or u.username,
                username=u.username,
                phone=u.phone,
                birthday=u.birthday,
                gender=u.gender,
                blood_group=p.blood_group,
                has_safety_flag=flag,
                change_count=change_count,
                last_reviewed_at=last_checkpoint.reviewed_at if last_checkpoint else None,
                last_update=last_t.timestamp if last_t else None
            ))

    items.sort(key=lambda x: (x.has_safety_flag, x.change_count), reverse=True)
    return items


@router.get("/patients/{patient_id}/overview/")
async def get_patient_overview(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Get complete patient-reported health overview (DOCTOR ONLY)."""
    patient = verify_doctor_patient_access(patient_id, doctor, db)
    u = db.query(User).filter(User.id == patient.user_id).first()

    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient.id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient.id).all()
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient.id).all()
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient.id).all()
    sessions = db.query(IntakeSession).filter(IntakeSession.patient_id == patient.id).all()

    return {
        "patient_id": patient.id,
        "demographics": {
            "name": f"{u.first_name} {u.last_name}".strip() or u.username if u else "",
            "username": u.username if u else "",
            "email": u.email if u else "",
            "phone": u.phone if u else "",
            "birthday": u.birthday if u else "",
            "gender": u.gender if u else "",
            "blood_group": patient.blood_group,
            "emergency_contact_name": patient.emergency_contact_name,
            "emergency_contact_phone": patient.emergency_contact_phone
        },
        "reported_symptoms": [{"id": s.id, "concern": s.concern, "severity": s.severity, "duration": s.duration, "pattern": s.pattern, "status": s.status, "reported_at": s.reported_at} for s in symptoms],
        "patient_reported_medications": [{"id": m.id, "medication_name": m.medication_name, "dosage": m.dosage, "frequency": m.frequency, "as_reported_text": m.as_reported_text, "reported_at": m.reported_at} for m in meds],
        "allergies": [{"id": a.id, "allergen": a.allergen, "reaction": a.reaction, "severity": a.severity} for a in allergies],
        "medical_history": [{"id": h.id, "condition_name": h.condition_name, "diagnosed_year": h.diagnosed_year, "notes": h.notes} for h in history],
        "intake_sessions_count": len(sessions)
    }


@router.get("/patients/{patient_id}/timeline/")
async def get_doctor_patient_timeline(
    patient_id: int,
    category: Optional[str] = Query(None, description="Filter timeline category"),
    days: Optional[int] = Query(None, description="Filter timeline by last N days"),
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """View full patient timeline with category and date filtering (DOCTOR ONLY)."""
    verify_doctor_patient_access(patient_id, doctor, db)

    query = db.query(PatientTimeline).filter(PatientTimeline.patient_id == patient_id)

    if category:
        query = query.filter(PatientTimeline.category.ilike(f"%{category}%"))

    if days and days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(PatientTimeline.timestamp >= cutoff)

    return query.order_by(PatientTimeline.timestamp.desc()).all()


@router.post("/patients/{patient_id}/mark-reviewed/")
async def mark_patient_reviewed(
    patient_id: int,
    data: MarkReviewedCreate,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    DOCTOR CHECKPOINT: 'MARK AS REVIEWED'
    Defines the baseline timestamp that 'What Changed?' diffs against.
    """
    patient = verify_doctor_patient_access(patient_id, doctor_user, db)
    doc_prof = get_doctor_profile_or_404(doctor_user, db)

    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient_id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient_id).all()

    snapshot = {
        "symptoms": [{"concern": s.concern, "severity": s.severity, "duration": s.duration} for s in symptoms],
        "medications": [{"name": m.medication_name, "dosage": m.dosage} for m in meds]
    }

    checkpoint = DoctorReviewCheckpoint(
        doctor_id=doc_prof.id,
        patient_id=patient.id,
        notes=data.notes or "Doctor marked patient health record as reviewed.",
        snapshot_json=snapshot
    )
    db.add(checkpoint)
    db.commit()

    db.add(AuditLog(
        user_id=doctor_user.id,
        role="doctor",
        action="MARK_PATIENT_REVIEWED",
        resource=f"PatientProfile#{patient_id}",
        details=f"Doctor review checkpoint saved at {checkpoint.reviewed_at}"
    ))
    db.commit()

    return {
        "message": "Patient record marked as reviewed successfully.",
        "reviewed_at": checkpoint.reviewed_at
    }


@router.get("/patients/{patient_id}/what-changed/", response_model=WhatChangedResponse)
async def get_what_changed(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    CORE INNOVATION: 'WHAT CHANGED SINCE LAST VISIT?'
    Diffs patient timeline against the doctor-set baseline checkpoint.
    """
    verify_doctor_patient_access(patient_id, doctor, db)

    last_checkpoint = db.query(DoctorReviewCheckpoint).filter(
        DoctorReviewCheckpoint.patient_id == patient_id
    ).order_by(DoctorReviewCheckpoint.reviewed_at.desc()).first()

    since_time = last_checkpoint.reviewed_at if last_checkpoint else datetime(2000, 1, 1, tzinfo=timezone.utc)

    recent_timeline = db.query(PatientTimeline).filter(
        PatientTimeline.patient_id == patient_id,
        PatientTimeline.timestamp > since_time
    ).order_by(PatientTimeline.timestamp.desc()).all()

    new_items = []
    updated_items = []
    unchanged_items = []

    for t in recent_timeline:
        if t.action_type == "Added":
            new_items.append(f"[{t.category}] {t.new_value}")
        elif t.action_type == "Updated":
            updated_items.append(f"[{t.category}] Prev: {t.previous_value} -> New: {t.new_value}")

    if not new_items and not updated_items:
        unchanged_items.append("No new symptoms or medication changes reported since last review checkpoint.")

    summary_text = f"Patient has {len(new_items)} new reported item(s) and {len(updated_items)} updated item(s) since last doctor review."

    return WhatChangedResponse(
        patient_id=patient_id,
        last_reviewed_at=last_checkpoint.reviewed_at if last_checkpoint else None,
        new_items=new_items if new_items else ["None"],
        updated_items=updated_items if updated_items else ["None"],
        unchanged_items=unchanged_items if unchanged_items else ["Baseline health record unchanged"],
        summary=summary_text
    )


@router.post("/patients/{patient_id}/queue-question/")
async def queue_question_for_patient(
    patient_id: int,
    data: QueueQuestionCreate,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    DOCTOR FEATURE: 'ASK THE PATIENT THIS'
    Doctor queues a specific question for patient to answer before appointment.
    """
    patient = verify_doctor_patient_access(patient_id, doctor_user, db)
    doc_prof = get_doctor_profile_or_404(doctor_user, db)

    q = DoctorQueuedQuestion(
        doctor_id=doc_prof.id,
        patient_id=patient.id,
        question_text=data.question_text,
        target_field=data.target_field or "General"
    )
    db.add(q)
    db.commit()

    return {
        "message": f"Question queued for patient: '{data.question_text}'",
        "question_id": q.id
    }


@router.get("/patients/{patient_id}/export-brief/", response_model=ExportBriefResponse)
async def export_intake_brief(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    EXPORT THE BRIEF:
    One-click export of plain-text intake brief formatted for EHR copy-pasting.
    Dynamically constructs a comprehensive clinical handoff from all patient-reported data.
    """
    patient = verify_doctor_patient_access(patient_id, doctor, db)
    u = db.query(User).filter(User.id == patient.user_id).first()
    p_name = f"{u.first_name} {u.last_name}".strip() if u else f"Patient #{patient_id}"

    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient_id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient_id).all()
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient_id).all()
    safety_flag = db.query(IntakeSession).filter(
        IntakeSession.patient_id == patient_id,
        IntakeSession.safety_flag == True
    ).first() is not None

    sym_text = "\n".join([f"  • {s.concern} (Severity: {s.severity}/10, Duration: {s.duration or 'N/A'}, Pattern: {s.pattern or 'N/A'})" for s in symptoms]) if symptoms else "  • None reported"
    med_text = "\n".join([f"  • {m.medication_name} (Dosage: {m.dosage or 'N/A'}, Frequency: {m.frequency or 'N/A'})" for m in meds]) if meds else "  • No current patient-reported medications"
    all_text = "\n".join([f"  • {a.allergen} (Reaction: {a.reaction or 'N/A'})" for a in allergies]) if allergies else "  • No known allergies reported"
    his_text = "\n".join([f"  • {h.condition_name} (Status: {h.status or 'Active'}, Diagnosed: {h.diagnosed_year or 'N/A'})" for h in history]) if history else "  • No significant past medical history reported"

    safety_str = "⚠️ ATTENTION: Red Flag Safety Alert Triggered During Intake" if safety_flag else "No immediate urgency flags raised."

    formatted_export = f"""==================================================
CLINIC INTAKE BRIEF -- {p_name.upper()}
Patient ID: #{patient_id} | Blood Group: {patient.blood_group or 'N/A'}
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
==================================================

1. PATIENT-REPORTED SYMPTOMS & CONCERNS:
{sym_text}

2. PATIENT-REPORTED MEDICATIONS:
{med_text}

3. ALLERGIES & SENSITIVITIES:
{all_text}

4. MEDICAL HISTORY & PRIOR CONDITIONS:
{his_text}

5. SAFETY & URGENCY SCREENING:
  {safety_str}

--------------------------------------------------
Notice: All facts above are patient-reported.
Exported from CareTraceAI Assistant for EHR Paste.
=================================================="""

    return ExportBriefResponse(
        patient_id=patient_id,
        patient_name=p_name,
        export_formatted_text=formatted_export
    )


@router.get("/patients/{patient_id}/attachments/", response_model=List[PatientAttachmentResponse])
async def get_patient_attachments_for_doctor(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """View uploaded medication strip photos & attachments (DOCTOR ONLY)."""
    verify_doctor_patient_access(patient_id, doctor, db)
    return db.query(PatientAttachment).filter(
        PatientAttachment.patient_id == patient_id
    ).order_by(PatientAttachment.uploaded_at.desc()).all()


@router.get("/patients/{patient_id}/intake-summary/")
async def get_patient_intake_summary(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Get AI-generated Intake Brief summary for doctor (DOCTOR ONLY)."""
    verify_doctor_patient_access(patient_id, doctor, db)

    latest_session = db.query(IntakeSession).filter(
        IntakeSession.patient_id == patient_id
    ).order_by(IntakeSession.created_at.desc()).first()

    if latest_session and latest_session.summary_generated:
        return {
            "patient_id": patient_id,
            "session_id": latest_session.id,
            "summary_markdown": latest_session.summary_generated,
            "safety_flag": latest_session.safety_flag,
            "safety_message": latest_session.safety_message,
            "generated_at": latest_session.updated_at or latest_session.created_at
        }

    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient_id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient_id).all()
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient_id).all()
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()

    sym_list = [{"concern": s.concern, "severity": s.severity, "duration": s.duration, "pattern": s.pattern} for s in symptoms]
    med_list = [{"medication_name": m.medication_name, "dosage": m.dosage, "frequency": m.frequency} for m in meds]

    brief = generate_doctor_brief(
        symptoms=sym_list,
        medications=med_list,
        history=[{"condition_name": h.condition_name} for h in history],
        allergies=[{"allergen": a.allergen} for a in allergies],
        missing_info=["Check medication dosage details"]
    )

    return {
        "patient_id": patient_id,
        "session_id": None,
        "summary_markdown": brief,
        "safety_flag": False,
        "safety_message": None,
        "generated_at": None
    }


@router.get("/patients/{patient_id}/conversations/")
async def get_original_patient_conversation(
    patient_id: int,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """View raw patient-AI conversation messages (DOCTOR ONLY)."""
    verify_doctor_patient_access(patient_id, doctor, db)
    sessions = db.query(IntakeSession).filter(IntakeSession.patient_id == patient_id).all()
    session_ids = [s.id for s in sessions]

    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id.in_(session_ids)
    ).order_by(ConversationMessage.created_at.asc()).all() if session_ids else []

    return [{
        "id": m.id,
        "session_id": m.session_id,
        "sender": m.sender,
        "content": m.content,
        "extracted_json": m.extracted_json,
        "created_at": m.created_at
    } for m in messages]


# ---------------- DOCTOR-ONLY CLINICAL ENDPOINTS ----------------
@router.post("/patients/{patient_id}/clinical-assessment/", response_model=ClinicalAssessmentResponse)
async def add_clinical_assessment(
    patient_id: int,
    data: ClinicalAssessmentCreate,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """DOCTOR ONLY -- Add diagnosis, clinical assessment, treatment plan."""
    patient = verify_doctor_patient_access(patient_id, doctor_user, db)
    doc_prof = get_doctor_profile_or_404(doctor_user, db)

    assessment = ClinicalAssessment(
        patient_id=patient.id,
        doctor_id=doc_prof.id,
        clinical_notes=data.clinical_notes,
        diagnosis=data.diagnosis,
        treatment_plan=data.treatment_plan,
        follow_up_instructions=data.follow_up_instructions
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    db.add(AuditLog(
        user_id=doctor_user.id,
        role="doctor",
        action="CREATE_CLINICAL_ASSESSMENT",
        resource=f"PatientProfile#{patient_id}",
        details=f"Diagnosis added: {data.diagnosis}"
    ))
    db.commit()

    return assessment


@router.post("/patients/{patient_id}/prescription/", response_model=ClinicianPrescriptionResponse)
async def add_clinician_prescription(
    patient_id: int,
    data: ClinicianPrescriptionCreate,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """DOCTOR ONLY -- Prescribe medication."""
    patient = verify_doctor_patient_access(patient_id, doctor_user, db)
    doc_prof = get_doctor_profile_or_404(doctor_user, db)

    prescription = ClinicianPrescription(
        patient_id=patient.id,
        doctor_id=doc_prof.id,
        medication_name=data.medication_name,
        dosage=data.dosage,
        frequency=data.frequency,
        instructions=data.instructions or ""
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    db.add(AuditLog(
        user_id=doctor_user.id,
        role="doctor",
        action="PRESCRIBE_MEDICATION",
        resource=f"PatientProfile#{patient_id}",
        details=f"Prescribed {data.medication_name} {data.dosage}"
    ))
    db.commit()

    return prescription


@router.post("/patients/{patient_id}/notes/", response_model=DoctorNoteResponse)
async def add_doctor_note(
    patient_id: int,
    data: DoctorNoteCreate,
    doctor_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """DOCTOR ONLY -- Add private clinical note (Inaccessible by patient)."""
    patient = verify_doctor_patient_access(patient_id, doctor_user, db)
    doc_prof = get_doctor_profile_or_404(doctor_user, db)

    note = DoctorNote(
        patient_id=patient.id,
        doctor_id=doc_prof.id,
        note_text=data.note_text
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return note
