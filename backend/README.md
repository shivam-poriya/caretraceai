# Clinic Intake Assistant — FastAPI Backend

> **“Let patients tell their story. Let doctors focus on care.”**

A GenAI-powered continuous patient intake and clinical handoff system built for the **GenAI for Good Hackathon**. 

This FastAPI backend uses **Gemma 4 12B-IT (q4_0)** via `llama-cpp-python` and a **RAG (Retrieval-Augmented Generation)** pipeline powered by **PostgreSQL + pgvector** to extract patient-reported symptoms, track changes chronologically, enforce strict medical safety guardrails, and present a doctor-ready intake brief.

---

## 🌟 Key Innovations & Competition Features

1. **“What Changed Since the Last Visit?”**: Dynamic comparison of new vs updated patient-reported symptoms between consultations.
2. **“Mark as Reviewed” Doctor Checkpoint**: Doctor-set baseline checkpoint that makes the "What Changed?" diff crisp, explainable, and precise.
3. **“Read It Back” Confirmation Card**: Patient validates extracted facts (`"I've recorded: chest pain, 2 days, severity 6/10. Is this right?"`) with `Yes` / `Fix this`. Reduces hallucinations and empowers patients.
4. **Completeness Ring Metric**: Dynamic computation of intake completion percentage (`0–100%`) encouraging completion.
5. **“I Don't Know” / “Skip” Option**: Allows low-literacy/elderly patients to skip unanswered questions without abandoning intake.
6. **Quick-Update Chips**: One-tap updates (`Got worse`, `Got better`, `Same`, `New symptom`) pre-seeding conversations.
7. **Photo Attachment for Medication Strips**: Patients photograph medication boxes; stored as raw patient-reported attachments for doctor review (no silent AI OCR inference).
8. **“Ask the Patient This” Doctor Queue**: Doctors queue specific questions for patients before appointments.
9. **EHR Brief Export**: One-click plain-text brief export for instant pasting into any existing clinic EHR.
10. **Resume Prompt**: Continuous prompt on app reopen (`"Last time you mentioned a headache. Has anything changed?"`).
11. **"What Your Doctor Sees" Preview**: Patient trust preview showing exact brief sent to doctor while clarifying private doctor notes.
12. **Forgot Password via OTP**: Secure 3-step OTP password reset flow delivered via SMTP (`caretrace7@gmail.com`) with 10-minute expiry validation.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend Server                        │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│   Auth Router   │ Patient Router  │  Doctor Router  │ GenAI Intake Router│
├─────────────────┴─────────────────┴─────────────────┴───────────────────┤
│                      Role-Based Access Guard (RBAC)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                          Service Layer                                  │
│  - LLM Service: Gemma 4 12B-IT Offline (llama-cpp-python, CUDA GPU)     │
│  - RAG Embedding Service: sentence-transformers & pgvector search        │
│  - SMTP Email Service: OTP delivery for password reset                  │
├─────────────────────────────────────────────────────────────────────────┤
│                Docker PostgreSQL 16 + pgvector (Port 5435)              │
│  ┌──────────────────────────────┬─────────────────────────────────────┐ │
│  │ Patient-Reported Data        │ Doctor-Only Clinical Data           │ │
│  │ (symptoms, meds, photos)     │ (assessments, prescriptions, notes) │ │
│  └──────────────────────────────┴─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.115+ with Uvicorn
- **Database**: PostgreSQL 16 with `pgvector` extension (Docker container on port `5435`)
- **ORM**: SQLAlchemy 2.0+ with `psycopg2-binary`
- **GenAI Engine**: Gemma 4 12B-IT (q4_0 quantized) loaded offline via `llama-cpp-python`
- **RAG & Vector Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions)
- **Authentication**: JWT (JSON Web Tokens) with `bcrypt` password hashing and role enforcement
- **Email Service**: SMTP email delivery via Gmail (`caretrace7@gmail.com`)

---

## 🚀 Quick Start Guide

### 1. Start PostgreSQL + pgvector Docker Container
```bash
docker-compose up -d
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirement.txt
```

### 3. Model & Environment Configuration
Check `config/settings/env/.env.development`:
```env
GEMMA_MODEL_PATH=C:\Users\Acer\Documents\model\gemma-3-12b-it-qat-q4_0.gguf
DB_URI=postgresql://postgres:123@127.0.0.1:5435/clinic_intake

SMTP_USERNAME=caretrace7@gmail.com
SMTP_PASSWORD=nvnv zqit pajg gkfd
```

### 4. Seed Synthetic Demo Data
```bash
python -m scripts.seed_data
```
- **Demo Patient**: `username='patient_demo'`, `password='Password@123'`
- **Demo Doctor**: `username='doctor_demo'`, `password='Password@123'`

### 5. Run Backend Server
```bash
python main.py
```
- Server URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### 6. Run Complete API Audit Test Suites
```bash
# Test complete 35-endpoint API audit suite
python -m scripts.test_all_endpoints

# Test Forgot Password OTP workflow
python -m scripts.test_otp

# Test new UX, accessibility, doctor checkpoint, and trust features
python -m scripts.test_new_features
```

---

## 📋 Complete API Endpoints Reference

### 1. Authentication & OTP (`/v1/custom-auth`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/v1/custom-auth/test` | Health check endpoint | Public |
| `POST` | `/v1/custom-auth/register/` | Register user (`patient` or `doctor`) | Public |
| `POST` | `/v1/custom-auth/login/` | OAuth2 Login (returns JWT token & role) | Public |
| `GET` | `/v1/custom-auth/get-user-profile/` | Get current user profile | Bearer Token |
| `POST` | `/v1/custom-auth/forgot-password/` | Step 1: Request 6-digit OTP via Email | Public |
| `POST` | `/v1/custom-auth/verify-otp/` | Step 2: Verify OTP validity & expiry | Public |
| `POST` | `/v1/custom-auth/reset-password/` | Step 3: Set new password using verified OTP | Public |

### 2. Patient Module (`/v1/patient`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/v1/patient/profile/` | Get patient health profile | Patient (Self) |
| `PUT` | `/v1/patient/profile/` | Update blood group, emergency contact | Patient (Self) |
| `GET` | `/v1/patient/resume-prompt/` | Continuous prompt ("Last time you mentioned...") | Patient (Self) |
| `POST` | `/v1/patient/quick-update/` | One-tap quick update chips (`got_worse`, `got_better`) | Patient (Self) |
| `POST` | `/v1/patient/symptoms/` | Report a new symptom | Patient (Self) |
| `PUT` | `/v1/patient/symptoms/{id}/` | Update symptom severity or duration | Patient (Self) |
| `GET` | `/v1/patient/symptoms/` | List all reported symptoms | Patient (Self) |
| `POST` | `/v1/patient/allergies/` | Add allergy report | Patient (Self) |
| `GET` | `/v1/patient/allergies/` | List allergies | Patient (Self) |
| `POST` | `/v1/patient/medical-history/` | Add medical history item | Patient (Self) |
| `GET` | `/v1/patient/medical-history/` | List medical history | Patient (Self) |
| `POST` | `/v1/patient/medications/` | Report medication patient is taking | Patient (Self) |
| `GET` | `/v1/patient/medications/` | List patient-reported medications | Patient (Self) |
| `POST` | `/v1/patient/attachments/upload/` | Upload photo attachment (Medication box/strip) | Patient (Self) |
| `GET` | `/v1/patient/attachments/` | List uploaded photo attachments | Patient (Self) |
| `GET` | `/v1/patient/queued-questions/` | Fetch questions queued by doctor | Patient (Self) |
| `GET` | `/v1/patient/doctor-view-preview/` | "What your doctor sees" preview | Patient (Self) |
| `GET` | `/v1/patient/timeline/?category=&days=` | Get timeline with category & date filtering | Patient (Self) |

### 3. GenAI Intake Chat Module (`/v1/intake`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/v1/intake/sessions/` | Start new AI intake chat session | Patient (Self) |
| `GET` | `/v1/intake/sessions/` | List intake sessions | Patient (Self) |
| `GET` | `/v1/intake/sessions/{id}/` | Get intake session state & structured data | Patient (Self) |
| `POST` | `/v1/intake/sessions/{id}/message/` | Send message (RAG Pipeline + Completeness Ring) | Patient (Self) |
| `POST` | `/v1/intake/sessions/{id}/confirm-extraction/` | "Read it back" confirmation card (Yes / Fix this) | Patient (Self) |
| `POST` | `/v1/intake/sessions/{id}/skip-field/` | "I don't know" / "Skip" button | Patient (Self) |
| `GET` | `/v1/intake/sessions/{id}/messages/` | Get full chat transcript | Patient (Self) |
| `POST` | `/v1/intake/sessions/{id}/end/` | End session & generate Doctor Summary | Patient (Self) |

### 4. Doctor Dashboard & Clinical Module (`/v1/doctor`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/v1/doctor/patients/` | List assigned patients (Priority sorted + change badges) | Doctor |
| `GET` | `/v1/doctor/patients/search/?q=` | Search patients by name or username | Doctor |
| `GET` | `/v1/doctor/patients/{id}/overview/` | Patient-reported data overview | Doctor |
| `GET` | `/v1/doctor/patients/{id}/timeline/` | Patient timeline | Doctor |
| `POST` | `/v1/doctor/patients/{id}/mark-reviewed/` | **"Mark as reviewed"** baseline checkpoint | Doctor |
| `GET` | `/v1/doctor/patients/{id}/intake-summary/` | Get AI Doctor Brief (Prompt D) | Doctor |
| `GET` | `/v1/doctor/patients/{id}/what-changed/` | **"WHAT CHANGED?"** comparison against checkpoint | Doctor |
| `POST` | `/v1/doctor/patients/{id}/queue-question/` | **"Ask the patient this"**: Queue question for patient | Doctor |
| `GET` | `/v1/doctor/patients/{id}/export-brief/` | One-click EHR export formatted brief | Doctor |
| `GET` | `/v1/doctor/patients/{id}/attachments/` | View patient medication strip photo attachments | Doctor |
| `GET` | `/v1/doctor/patients/{id}/conversations/` | Raw patient-AI chat transcript | Doctor |
| `POST` | `/v1/doctor/patients/{id}/clinical-assessment/` | **Doctor-Only**: Add diagnosis & assessment | Doctor |
| `POST` | `/v1/doctor/patients/{id}/prescription/` | **Doctor-Only**: Prescribe medication | Doctor |
| `POST` | `/v1/doctor/patients/{id}/notes/` | **Doctor-Only**: Add private clinical notes | Doctor |
