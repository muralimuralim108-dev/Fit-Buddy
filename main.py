import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from gemini_service import gemini_service
import qna
import explanation_module
import quiz_module
import summary_module
import learning_path

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("edugenie.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("EduGenie application starting up...")
    if gemini_service.is_configured():
        logger.info(f"EduGenie initialized with model: {gemini_service.default_model}")
    else:
        logger.warning("GEMINI_API_KEY is missing or invalid. Set it in .env to enable AI features.")
    yield
    logger.info("EduGenie application shutting down...")

app = FastAPI(
    title="EduGenie – AI-Powered Learning Assistant",
    description="Intelligent educational platform providing Q&A, Concept Explanations, Quiz Generation, Summarization, and Roadmaps.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static Files & Templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include API module routers
app.include_router(qna.router)
app.include_router(explanation_module.router)
app.include_router(quiz_module.router)
app.include_router(summary_module.router)
app.include_router(learning_path.router)

# Custom Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Invalid input provided.")
    field = " -> ".join([str(loc) for loc in first_error.get("loc", []) if loc != "body"])

    user_msg = f"Please check your input: {msg}"
    if field:
        user_msg = f"Input error on '{field}': {msg}"

    logger.warning(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": user_msg, "error_type": "validation_error"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "EduGenie couldn't process your request right now. Please try again.",
            "error_type": "internal_server_error"
        }
    )

# Root dashboard route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Renders the main EduGenie student dashboard."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": "EduGenie",
            "tagline": "Your AI-Powered Learning Companion",
            "is_configured": gemini_service.is_configured(),
            "model_name": gemini_service.default_model
        }
    )

# System health / configuration status endpoint
@app.get("/api/status")
async def get_system_status():
    """Returns the operational status and Gemini configuration state."""
    return {
        "status": "online",
        "app": "EduGenie",
        "version": "1.0.0",
        "api_configured": gemini_service.is_configured(),
        "model": gemini_service.default_model
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting EduGenie server at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
