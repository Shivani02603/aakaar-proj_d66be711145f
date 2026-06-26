import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import RequestIdPlugin
from datetime import datetime
from database.config import init_db
from backend.routers.auth import router as auth_router
from backend.routers.core_ai_qa import router as core_ai_qa_router
from backend.routers.data_persistence import router as data_persistence_router
from backend.routers.data_storage import router as data_storage_router
from backend.routers.document_management import router as document_management_router
from backend.routers.document_processing import router as document_processing_router
from backend.routers.sessions import router as sessions_router
from backend.routers.users import router as users_router

# Initialize FastAPI app
app = FastAPI(
    title="Aakaar Project",
    description="Backend for AI-powered web application",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# SlowAPI Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"detail": str(exc)}, status_code=429)

app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# Context Middleware for Request ID
app.add_middleware(
    RawContextMiddleware,
    plugins=[RequestIdPlugin()]
)

# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Lifespan Context Manager
@app.on_event("startup")
async def startup_event():
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    pass

# Mount Routers
app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])
app.include_router(core_ai_qa_router, prefix='/api/ai', tags=['Core Ai Qa'])
app.include_router(data_persistence_router, prefix='/api/chat', tags=['Data Persistence'])
app.include_router(data_storage_router, prefix='/api/auth/register', tags=['Data Storage'])
app.include_router(document_management_router, prefix='/api/documents', tags=['Document Management'])
app.include_router(document_processing_router, prefix='/api', tags=['Document Processing'])
app.include_router(sessions_router, prefix='/api/chat/sessions', tags=['Sessions'])
app.include_router(users_router, prefix='/api/auth/register', tags=['Users'])

# AI_ROUTER_INJECTION_POINT — do not remove this line
# AI layer — mounted by Agent 8B
from ai.routes import router as ai_router
app.include_router(ai_router, prefix='/api/ai', tags=['AI'])
