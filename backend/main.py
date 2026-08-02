import os
from importlib import import_module
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(
    title="Clinic Intake Assistant API",
    description="GenAI-Powered Patient Intake & Clinical Handoff System using Gemma 4 12B-IT & pgvector",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.exception_handler(RequestValidationError)
async def validation_bad_request_exception_handler(request: Request, exc: RequestValidationError):
    message = None
    for x in exc.errors():
        fields = [entry for entry in x["loc"] if entry != "body"]
        if len(fields) == 0:
            message = "Please provide a body."
        elif len(fields) == 1:
            message = f"{fields[0]} {x['msg']}"
            break
        else:
            message = f"{fields[1]} {x['msg']}"
            break

    return JSONResponse(
        status_code=400,
        content={"detail": message},
    )


SETTINGS_MODULES = {
    "development": "config.settings.development",
    "production": "config.settings.production",
}
environment = os.getenv("ENVIRONMENT", "development")
settings_module = SETTINGS_MODULES.get(environment, "config.settings.development")
settings = import_module(settings_module)

from config.urls import urls_router
app.include_router(urls_router)


@app.on_event("startup")
def startup_event():
    print("[+] Starting Clinic Intake Assistant API...")
    try:
        from config.database import init_db
        init_db()
    except Exception as e:
        print("[!] Startup DB init warning:", e)


def main():
    print(f"----------------- Running Clinic Intake Assistant ({environment}) -------------------------")
    uvicorn.run(app, host=settings.host, port=int(settings.port))


if __name__ == "__main__":
    main()
