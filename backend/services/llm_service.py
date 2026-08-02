"""
LLM Service using Gemma offline model via llama-cpp-python.
Implements prompts A-F with strict anti-hallucination, no-diagnosis guardrails.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("llm_service")

# Global model instance
_llm_instance = None


def get_llm():
    """Singleton getter for Gemma llama-cpp model."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    model_path = os.getenv("GEMMA_MODEL_PATH", r"C:\Users\Acer\Documents\model\gemma-3-12b-it-qat-q4_0.gguf")
    n_gpu_layers = int(os.getenv("LLM_N_GPU_LAYERS", "-1"))
    n_ctx = int(os.getenv("LLM_N_CTX", "8192"))
    n_threads = int(os.getenv("LLM_N_THREADS", "8"))

    if not os.path.exists(model_path):
        logger.warning(f"Gemma model file not found at {model_path}. Using fallback rule-based response generator.")
        return None

    try:
        from llama_cpp import Llama
        logger.info(f"Loading Gemma model from {model_path} (n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx})...")
        _llm_instance = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )
        logger.info("✅ Gemma model loaded successfully.")
        return _llm_instance
    except Exception as e:
        logger.error(f"Failed to load Gemma model via llama-cpp-python: {e}")
        return None


def run_gemma_prompt(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 1024) -> str:
    """Executes prompt on Gemma model or returns fallback text."""
    llm = get_llm()
    if llm is None:
        return ""

    prompt = f"<bos><start_of_turn>system\n{system_prompt}<end_of_turn>\n<start_of_turn>user\n{user_prompt}<end_of_turn>\n<start_of_turn>model\n"
    
    try:
        response = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<end_of_turn>", "<eos>"]
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Error running Gemma prompt: {e}")
        return ""


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Cleans markdown JSON code blocks from LLM responses."""
    if not raw_text:
        return {}
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Simple extraction attempt
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end+1])
            except Exception:
                pass
        return {}


# ----------------------------------------------------
# PROMPT A: PATIENT INFORMATION EXTRACTION
# ----------------------------------------------------
PROMPT_A_SYSTEM = """You are a medical intake AI assistant.
Your task is to extract structured patient-reported information from natural language.

STRICT GUARDRAILS:
1. SUMMARIZE, DON'T DIAGNOSE.
2. NEVER suggest or infer a disease, condition, or medical diagnosis.
3. NEVER prescribe or recommend medication or treatment.
4. Only extract facts explicitly reported by the patient. Do not fabricate or guess.
5. If information is not mentioned, use null or "Not provided".

Return ONLY valid JSON matching this schema:
{
  "reported_symptoms": [
    {
      "concern": "string",
      "severity": 1-10 or null,
      "duration": "string or Not provided",
      "pattern": "string or Not provided"
    }
  ],
  "patient_reported_medications": [
    {
      "medication_name": "string",
      "dosage": "string or Not provided",
      "frequency": "string or Not provided"
    }
  ],
  "allergies": ["string"],
  "medical_history": ["string"],
  "patient_context": "string"
}"""


def extract_patient_info(patient_input: str, existing_context: str = "") -> Dict[str, Any]:
    """Extracts structured patient facts from natural text."""
    user_prompt = f"Patient Input: \"{patient_input}\"\n"
    if existing_context:
        user_prompt += f"Existing Patient Context: {existing_context}\n"
    user_prompt += "Extract structured patient-reported information as JSON."

    raw = run_gemma_prompt(PROMPT_A_SYSTEM, user_prompt, temperature=0.1)
    extracted = clean_json_response(raw)

    if not extracted:
        # Fallback deterministic extraction for basic keywords
        extracted = {
            "reported_symptoms": [],
            "patient_reported_medications": [],
            "allergies": [],
            "medical_history": [],
            "patient_context": patient_input
        }
        lower = patient_input.lower()
        if "pain" in lower or "fever" in lower or "cough" in lower or "headache" in lower or "nausea" in lower:
            extracted["reported_symptoms"].append({
                "concern": patient_input.strip(),
                "severity": None,
                "duration": "Not provided",
                "pattern": "Not provided"
            })
        if "taking" in lower or "medication" in lower or "medicine" in lower or "pill" in lower:
            extracted["patient_reported_medications"].append({
                "medication_name": "Patient-reported medication",
                "dosage": "Not provided",
                "frequency": "Not provided"
            })

    return extracted


# ----------------------------------------------------
# PROMPT B & C: MISSING INFO DETECTION & FOLLOW-UP
# ----------------------------------------------------
PROMPT_BC_SYSTEM = """You are a warm, empathetic clinical intake assistant preparing a structured handoff report for a doctor.
Analyze the patient's reported information and generate a thoughtful, empathetic, and comprehensive response.

STRICT INSTRUCTIONS:
1. EMPATHETIC ACKNOWLEDGMENT: Warmly acknowledge what the patient just reported.
2. RECORD CONFIRMATION: Briefly confirm what details have been added or updated in their care summary.
3. CLEAR FOLLOW-UP: Ask 1-2 respectful follow-up questions to gather missing clinical details (such as severity on a 0-10 scale, exact duration, timing, or medication dosages).
4. STRICT GUARDRAILS: NEVER diagnose medical conditions or suggest treatment/prescriptions.

Return ONLY JSON:
{
  "missing_information": ["string"],
  "followup_question": "string (A complete 2-3 sentence empathetic response acknowledging what was reported, confirming what was recorded, and asking clarifying follow-up questions)",
  "safety_flag": boolean,
  "safety_message": "string or null"
}"""


def detect_missing_and_followup(structured_data: Dict[str, Any], conversation_history: List[str] = None) -> Dict[str, Any]:
    """Identifies missing intake fields and generates next follow-up question."""
    history_str = "\n".join(conversation_history[-4:]) if conversation_history else "None"
    user_prompt = f"Current Structured Data: {json.dumps(structured_data)}\nRecent Conversation: {history_str}\nProvide missing information list and empathetic follow-up response."

    raw = run_gemma_prompt(PROMPT_BC_SYSTEM, user_prompt, temperature=0.3)
    result = clean_json_response(raw)

    if not result or not result.get("followup_question"):
        # Rich rule-based fallback response
        symptoms = structured_data.get("reported_symptoms", [])
        meds = structured_data.get("patient_reported_medications", [])
        missing = []
        
        ack_parts = []
        if symptoms:
            sym_names = ", ".join([s.get("concern") for s in symptoms if s.get("concern")])
            if sym_names:
                ack_parts.append(f"Thank you for sharing your update regarding {sym_names}.")
        if meds:
            med_names = ", ".join([m.get("medication_name") for m in meds if m.get("medication_name") and m.get("medication_name") != "Patient-reported medication"])
            if med_names:
                ack_parts.append(f"I've also recorded your medication details for {med_names}.")

        ack_text = " ".join(ack_parts) if ack_parts else "Thank you for sharing your health update with me."

        question = f"{ack_text} I've updated your care summary for your doctor to review. Could you tell me a bit more about when these symptoms started and how severe they feel right now?"

        if symptoms:
            sym = symptoms[0]
            concern_name = sym.get("concern", "symptom")
            if sym.get("severity") is None:
                missing.append("Symptom severity (0-10 scale)")
                question = (
                    f"{ack_text} To help your doctor assess how you're feeling, "
                    f"how would you rate the pain or discomfort of your {concern_name} on a scale from 0 (no pain) to 10 (worst pain imaginable)?"
                )
            elif sym.get("duration") == "Not provided":
                missing.append("Symptom duration")
                question = (
                    f"{ack_text} I've noted a severity of {sym.get('severity')}/10 for your {concern_name}. "
                    f"When did this first begin, and is it constant or coming and going?"
                )
            else:
                question = (
                    f"{ack_text} Your intake summary for {concern_name} (Severity: {sym.get('severity')}/10, Duration: {sym.get('duration')}) "
                    f"has been recorded for your doctor. Is there any other symptom, allergy, or medication you would like to update today?"
                )

        if meds and not missing:
            med = meds[0]
            med_name = med.get("medication_name", "medication")
            if med_name in ["Patient-reported medication", "Not provided"] or med.get("dosage") == "Not provided":
                missing.append("Medication name and dosage")
                question = (
                    f"{ack_text} Could you specify the exact brand or generic name and dosage of the medication you're taking, if you have it nearby?"
                )

        result = {
            "missing_information": missing,
            "followup_question": question,
            "safety_flag": False,
            "safety_message": None
        }

    return result


# ----------------------------------------------------
# PROMPT D: DOCTOR INTAKE SUMMARY
# ----------------------------------------------------
PROMPT_D_SYSTEM = """You are a clinical documentation AI. Create a structured Patient Intake Brief for the doctor.

CRITICAL SAFETY DIRECTIVES:
1. Label all facts as PATIENT-REPORTED.
2. NEVER diagnose, predict diseases, or suggest treatment.
3. Clearly separate reported facts, missing info, and safety flags.

Return a clean markdown document with these exact sections:
## PATIENT INTAKE BRIEF
### Reason for visit / Reported Symptoms
### Associated Context & Duration
### Patient-Reported Medication (Not Prescriptions)
### Missing Information for Clinical Review
### Safety & Urgency Flag"""


def generate_doctor_brief(symptoms: List[Dict], medications: List[Dict], history: List[Dict], allergies: List[Dict], missing_info: List[str], safety_message: Optional[str] = None) -> str:
    """Generates doctor-facing summary brief."""
    input_data = {
        "symptoms": symptoms,
        "medications": medications,
        "history": history,
        "allergies": allergies,
        "missing_info": missing_info,
        "safety_message": safety_message
    }
    user_prompt = f"Patient Intake Data: {json.dumps(input_data)}\nGenerate Doctor Brief."

    summary = run_gemma_prompt(PROMPT_D_SYSTEM, user_prompt, temperature=0.1)

    if not summary or len(summary) < 50:
        # Fallback structured markdown generator
        sym_text = "\n".join([f"- **{s.get('concern')}**: Duration: {s.get('duration', 'Not provided')}, Severity: {s.get('severity', 'Not provided')}/10, Pattern: {s.get('pattern', 'Not provided')}" for s in symptoms]) or "- None reported"
        med_text = "\n".join([f"- **{m.get('medication_name')}**: Dose: {m.get('dosage', 'Not provided')}, Freq: {m.get('frequency', 'Not provided')}" for m in medications]) or "- No current patient-reported medications"
        miss_text = "\n".join([f"- {m}" for m in missing_info]) or "- Basic intake information complete"
        safety_text = f"⚠️ {safety_message}" if safety_message else "No immediate urgency flag raised during intake."

        summary = f"""## PATIENT INTAKE BRIEF

### Reason for visit / Reported Symptoms
{sym_text}

### Associated Context & Duration
Patient-provided details recorded above.

### Patient-Reported Medication (Not Prescriptions)
{med_text}

### Missing Information for Clinical Review
{miss_text}

### Safety & Urgency Flag
{safety_text}
"""

    return summary


# ----------------------------------------------------
# PROMPT E: "WHAT CHANGED?" COMPARISON
# ----------------------------------------------------
PROMPT_E_SYSTEM = """You are a clinical tracking AI. Compare a patient's previous reported health state with their current state.

RULES:
- Identify NEW symptoms or medications.
- Identify UPDATED severity, duration, or patterns.
- Do NOT infer diagnoses or medical causes for changes.

Return JSON:
{
  "new_items": ["string"],
  "updated_items": ["string"],
  "unchanged_items": ["string"],
  "summary": "string"
}"""


def detect_changes(previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
    """Compares previous patient report with current report."""
    user_prompt = f"Previous State: {json.dumps(previous_state)}\nCurrent State: {json.dumps(current_state)}\nIdentify changes."

    raw = run_gemma_prompt(PROMPT_E_SYSTEM, user_prompt, temperature=0.1)
    res = clean_json_response(raw)

    if not res:
        res = {
            "new_items": ["Recent symptom update submitted"],
            "updated_items": ["Information updated since last check"],
            "unchanged_items": ["Allergies and baseline history"],
            "summary": "Patient submitted updated symptom details."
        }

    return res


# ----------------------------------------------------
# PROMPT F: SAFETY & URGENCY ESCALATION GUARDRAIL
# ----------------------------------------------------
DETERMINISTIC_URGENT_KEYWORDS = [
    "chest pain", "difficulty breathing", "shortness of breath", "severe bleeding",
    "sudden numbness", "stroke", "loss of consciousness", "coughing blood", "anaphylaxis"
]


def check_safety_escalation(text_input: str) -> Dict[str, Any]:
    """Screening for urgent symptoms requiring medical escalation."""
    lower = text_input.lower()
    triggered_keywords = [kw for kw in DETERMINISTIC_URGENT_KEYWORDS if kw in lower]

    if triggered_keywords:
        return {
            "safety_flag": True,
            "safety_message": (
                "You have reported symptoms (e.g., " + ", ".join(triggered_keywords) + 
                ") that may require urgent medical evaluation. The Clinic Intake Assistant cannot diagnose medical conditions. "
                "Please seek appropriate urgent medical care immediately if symptoms are severe or worsening."
            )
        }

    return {
        "safety_flag": False,
        "safety_message": None
    }
