from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from apps.utils.role_guard import require_patient, verify_patient_self_access
from apps.db_models import (
    User, PatientProfile, IntakeSession, ConversationMessage,
    SymptomReport, PatientReportedMedication, Allergy, MedicalHistory, PatientTimeline
)
from apps.intake.models.v1_model import (
    IntakeMessageCreate, IntakeSessionResponse, MessageResponse, IntakeChatResponse,
    ConfirmationCardRequest, SkipFieldRequest
)
from services.llm_service import (
    extract_patient_info, detect_missing_and_followup,
    generate_doctor_brief, check_safety_escalation
)
from services.embedding_service import store_patient_document_embedding, search_similar_patient_context

router = APIRouter()


def compute_completeness_percentage(missing_info: List[str], structured_data: Dict[str, Any]) -> int:
    """Computes Completeness Ring Metric (0-100%)."""
    base_score = 40
    if structured_data.get("reported_symptoms"):
        base_score += 30
    if structured_data.get("patient_reported_medications"):
        base_score += 15
    if structured_data.get("allergies") or structured_data.get("medical_history"):
        base_score += 15

    deduction = len(missing_info) * 10
    final_score = max(20, min(100, base_score - deduction))
    return final_score


def format_read_it_back_card(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Formats 'Read it back' confirmation card payload for UX validation."""
    summary_parts = []
    for s in extracted.get("reported_symptoms", []):
        c = s.get("concern", "Symptom")
        sev = f", severity {s.get('severity')}/10" if s.get("severity") is not None else ""
        dur = f", duration {s.get('duration')}" if s.get("duration") and s.get("duration") != "Not provided" else ""
        summary_parts.append(f"{c}{sev}{dur}")

    for m in extracted.get("patient_reported_medications", []):
        mn = m.get("medication_name")
        if mn and mn not in ["Not provided", "Patient-reported medication"]:
            summary_parts.append(f"Taking {mn}")

    card_text = "I've recorded: " + ("; ".join(summary_parts) if summary_parts else "your health report") + ". Is this right?"

    return {
        "title": "Read-Back Confirmation",
        "card_text": card_text,
        "extracted_summary": summary_parts,
        "options": ["Yes, correct", "Fix this"]
    }


@router.post("/sessions/", response_model=IntakeSessionResponse)
async def create_intake_session(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Start a new AI-guided intake session for patient."""
    session = IntakeSession(
        patient_id=patient.id,
        status="active",
        structured_data={
            "reported_symptoms": [],
            "patient_reported_medications": [],
            "allergies": [],
            "medical_history": []
        }
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/", response_model=List[IntakeSessionResponse])
async def list_intake_sessions(
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """List all intake sessions for authenticated patient."""
    return db.query(IntakeSession).filter(
        IntakeSession.patient_id == patient.id
    ).order_by(IntakeSession.created_at.desc()).all()


@router.get("/sessions/{session_id}/", response_model=IntakeSessionResponse)
async def get_session_details(
    session_id: int,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Get session details and current structured data state."""
    session = db.query(IntakeSession).filter(
        IntakeSession.id == session_id,
        IntakeSession.patient_id == patient.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Intake session not found.")
    return session


@router.post("/sessions/{session_id}/message/", response_model=IntakeChatResponse)
async def process_patient_message(
    session_id: int,
    data: IntakeMessageCreate,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    GENAI INTAKE PIPELINE:
    - RAG pgvector retrieval
    - Urgency safety screening (Prompt F)
    - Fact extraction (Prompt A)
    - Database store & timeline updates
    - Missing info & adaptive follow-up (Prompts B & C)
    - Completeness ring calculation & 'Read it back' confirmation card
    """
    session = db.query(IntakeSession).filter(
        IntakeSession.id == session_id,
        IntakeSession.patient_id == patient.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Intake session not found.")

    patient_input = data.message.strip()

    # Handle Skip action ("I don't know" / "Skip" button)
    if data.action == "skip" or patient_input.lower() in ["skip", "i don't know", "dont know", "not sure"]:
        patient_input = f"[Skipped question regarding {data.skip_field or 'missing detail'}]"

    # 1. Save patient message
    patient_msg = ConversationMessage(
        session_id=session.id,
        sender="patient",
        content=patient_input,
        source_reference=f"Session #{session.id}"
    )
    db.add(patient_msg)
    db.commit()

    # 2. RAG Context Retrieval (pgvector)
    similar_docs = search_similar_patient_context(db, patient.id, patient_input, top_k=3)
    rag_context = "\n".join([f"[{d['category']}] {d['content']}" for d in similar_docs]) if similar_docs else ""

    # 3. Safety Screening
    safety_res = check_safety_escalation(patient_input)
    if safety_res["safety_flag"]:
        session.safety_flag = True
        session.safety_message = safety_res["safety_message"]

    # 4. GenAI Fact Extraction (Prompt A)
    extracted = extract_patient_info(patient_input, existing_context=rag_context)
    patient_msg.extracted_json = extracted
    db.commit()

    # 5. Database updates + Timeline entries
    for sym in extracted.get("reported_symptoms", []):
        concern = sym.get("concern")
        if concern and concern != "Not provided":
            exist = db.query(SymptomReport).filter(
                SymptomReport.patient_id == patient.id,
                SymptomReport.concern.ilike(concern)
            ).first()

            if exist:
                prev = f"Severity: {exist.severity}/10, Duration: {exist.duration}"
                if sym.get("severity") is not None:
                    exist.severity = sym.get("severity")
                if sym.get("duration") and sym.get("duration") != "Not provided":
                    exist.duration = sym.get("duration")
                if sym.get("pattern") and sym.get("pattern") != "Not provided":
                    exist.pattern = sym.get("pattern")
                db.commit()

                db.add(PatientTimeline(
                    patient_id=patient.id,
                    category="Symptom",
                    action_type="Updated",
                    previous_value=prev,
                    new_value=f"Concern: {concern} | Severity: {exist.severity}/10 | Duration: {exist.duration}",
                    source="ai_extracted",
                    conversation_ref=f"Message #{patient_msg.id}"
                ))
            else:
                s_obj = SymptomReport(
                    patient_id=patient.id,
                    concern=concern,
                    severity=sym.get("severity"),
                    duration=sym.get("duration", "Not provided"),
                    pattern=sym.get("pattern", "Not provided"),
                    source_text=patient_input
                )
                db.add(s_obj)
                db.commit()

                db.add(PatientTimeline(
                    patient_id=patient.id,
                    category="Symptom",
                    action_type="Added",
                    previous_value=None,
                    new_value=f"Concern: {concern} | Severity: {sym.get('severity')}/10 | Duration: {sym.get('duration')}",
                    source="ai_extracted",
                    conversation_ref=f"Message #{patient_msg.id}"
                ))

    # Process Patient-Reported Medications
    for med in extracted.get("patient_reported_medications", []):
        med_name = med.get("medication_name")
        if med_name and med_name not in ["Not provided", "Patient-reported medication"]:
            m_obj = PatientReportedMedication(
                patient_id=patient.id,
                medication_name=med_name,
                dosage=med.get("dosage", "Not provided"),
                frequency=med.get("frequency", "Not provided"),
                as_reported_text=patient_input
            )
            db.add(m_obj)
            db.commit()

            db.add(PatientTimeline(
                patient_id=patient.id,
                category="Patient-Reported Medication",
                action_type="Added",
                previous_value=None,
                new_value=f"Medication: {med_name} | Dose: {med.get('dosage')} | Freq: {med.get('frequency')}",
                source="ai_extracted",
                conversation_ref=f"Message #{patient_msg.id}"
            ))

    # 6. Vector store message in pgvector
    store_patient_document_embedding(
        db, patient.id, "conversation", patient_input, {"session_id": session_id}
    )

    all_symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient.id).all()
    all_meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient.id).all()

    updated_struct = {
        "reported_symptoms": [{"concern": s.concern, "severity": s.severity, "duration": s.duration, "pattern": s.pattern} for s in all_symptoms],
        "patient_reported_medications": [{"medication_name": m.medication_name, "dosage": m.dosage, "frequency": m.frequency} for m in all_meds],
        "allergies": [a.allergen for a in db.query(Allergy).filter(Allergy.patient_id == patient.id).all()],
        "medical_history": [h.condition_name for h in db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient.id).all()]
    }
    session.structured_data = updated_struct
    db.commit()

    # 7 & 8. Missing Info & Follow-up Question
    recent_msgs = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at.asc()).all()
    history_texts = [m.content for m in recent_msgs]

    bc_res = detect_missing_and_followup(updated_struct, history_texts)

    if safety_res["safety_flag"]:
        ai_response_text = f"⚠️ {safety_res['safety_message']}\n\n{bc_res.get('followup_question', '')}"
    else:
        ai_response_text = bc_res.get("followup_question", "Thank you for sharing. Is there anything else you would like to report to your doctor?")

    ai_msg = ConversationMessage(
        session_id=session.id,
        sender="ai",
        content=ai_response_text,
        source_reference=f"Session #{session.id}"
    )
    db.add(ai_msg)
    db.commit()

    missing_list = bc_res.get("missing_information", [])
    completeness = compute_completeness_percentage(missing_list, updated_struct)
    read_back_card = format_read_it_back_card(extracted)

    return IntakeChatResponse(
        session_id=session.id,
        ai_response=ai_response_text,
        safety_flag=session.safety_flag,
        safety_message=session.safety_message,
        extracted_data=extracted,
        missing_information=missing_list,
        followup_question=bc_res.get("followup_question"),
        completeness_percentage=completeness,
        read_it_back_card=read_back_card
    )


@router.post("/sessions/{session_id}/confirm-extraction/")
async def confirm_extraction(
    session_id: int,
    data: ConfirmationCardRequest,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    'READ IT BACK' CONFIRMATION CARD:
    Patient validates extracted facts. If confirmed=True, status set to validated.
    If confirmed=False, records patient's correction in timeline.
    """
    session = db.query(IntakeSession).filter(
        IntakeSession.id == session_id,
        IntakeSession.patient_id == patient.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Intake session not found.")

    if data.confirmed:
        session.status = "validated"
        db.commit()
        msg = "Thank you! Your extracted health facts have been verified and saved."
    else:
        session.status = "correction_requested"
        db.commit()
        if data.corrections:
            db.add(PatientTimeline(
                patient_id=patient.id,
                category="Symptom Correction",
                action_type="Updated",
                previous_value="AI Extracted Facts",
                new_value=f"Patient Correction: {data.corrections}",
                source="patient_validation"
            ))
            db.commit()
        msg = "Correction recorded. The AI assistant will update your intake report accordingly."

    return {
        "session_id": session.id,
        "confirmed": data.confirmed,
        "message": msg
    }


@router.post("/sessions/{session_id}/skip-field/")
async def skip_field(
    session_id: int,
    data: SkipFieldRequest,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """
    'I DON'T KNOW' / 'SKIP' BUTTON:
    Allows patient to skip a follow-up question without abandoning intake.
    """
    session = db.query(IntakeSession).filter(
        IntakeSession.id == session_id,
        IntakeSession.patient_id == patient.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Intake session not found.")

    skip_msg = ConversationMessage(
        session_id=session.id,
        sender="patient",
        content=f"[Skipped: {data.field_name}]",
        source_reference=f"Session #{session.id}"
    )
    db.add(skip_msg)
    db.commit()

    return {
        "session_id": session.id,
        "skipped_field": data.field_name,
        "message": f"Field '{data.field_name}' skipped. Proceeding with intake."
    }


@router.get("/sessions/{session_id}/messages/", response_model=List[MessageResponse])
async def get_session_conversation(
    session_id: int,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """Get complete conversation transcript for session."""
    return db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at.asc()).all()


@router.post("/sessions/{session_id}/end/", response_model=IntakeSessionResponse)
async def end_intake_session(
    session_id: int,
    patient: PatientProfile = Depends(verify_patient_self_access),
    db: Session = Depends(get_db)
):
    """End intake session and generate Doctor Summary Brief (Prompt D)."""
    session = db.query(IntakeSession).filter(
        IntakeSession.id == session_id,
        IntakeSession.patient_id == patient.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Intake session not found.")

    session.status = "completed"

    symptoms = db.query(SymptomReport).filter(SymptomReport.patient_id == patient.id).all()
    meds = db.query(PatientReportedMedication).filter(PatientReportedMedication.patient_id == patient.id).all()
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient.id).all()
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient.id).all()

    sym_list = [{"concern": s.concern, "severity": s.severity, "duration": s.duration, "pattern": s.pattern} for s in symptoms]
    med_list = [{"medication_name": m.medication_name, "dosage": m.dosage, "frequency": m.frequency} for m in meds]
    hist_list = [{"condition_name": h.condition_name} for h in history]
    alg_list = [{"allergen": a.allergen} for a in allergies]

    doctor_brief = generate_doctor_brief(
        symptoms=sym_list,
        medications=med_list,
        history=hist_list,
        allergies=alg_list,
        missing_info=["Full medical history if applicable"],
        safety_message=session.safety_message if session.safety_flag else None
    )

    session.summary_generated = doctor_brief
    db.commit()
    db.refresh(session)
    return session
