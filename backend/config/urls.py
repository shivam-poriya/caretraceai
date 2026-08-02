from fastapi import APIRouter
from apps.custom_auth.router.v1_router import router as custom_auth_v1_router
from apps.patient.router.v1_router import router as patient_v1_router
from apps.intake.router.v1_router import router as intake_v1_router
from apps.doctor.router.v1_router import router as doctor_v1_router

urls_router = APIRouter()

# Include version 1 routers
urls_router.include_router(custom_auth_v1_router, prefix="/v1/custom-auth", tags=["Auth"])
urls_router.include_router(patient_v1_router, prefix="/v1/patient", tags=["Patient"])
urls_router.include_router(intake_v1_router, prefix="/v1/intake", tags=["GenAI Intake"])
urls_router.include_router(doctor_v1_router, prefix="/v1/doctor", tags=["Doctor Dashboard"])
