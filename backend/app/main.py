"""FastAPI application entry point for UNS Rirekisho Pro."""
from contextlib import asynccontextmanager
from datetime import datetime
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.limiter import limiter


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as exc:
        print(f"Database initialization failed: {exc}")
        raise

    yield

    # Shutdown
    print("Shutting down application")


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="""
## UNS Rirekisho Pro v26.1.4 - 人材派遣管理システム API

### 主な機能
- **候補者管理**: 履歴書 (CV/Resume) の登録・管理
- **申請ワークフロー**: 派遣先への提出と結果管理
- **入社連絡票**: 承認プロセスと社員変換
- **社員管理**: 派遣社員・請負社員の管理
- **社宅管理**: 住居の割り当てと追跡

### 認証
JWT Bearer トークンを使用。ヘッダー: `Authorization: Bearer <token>`

### 会社情報
ユニバーサル企画株式会社 (Universal Kikaku Co., Ltd.)
愛知県名古屋市
""",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "UNS-Kikaku Support",
        "email": "support@uns-kikaku.com",
        "url": settings.COMPANY_WEBSITE,
    },
    license_info={"name": "Proprietary"},
    lifespan=lifespan,
)


# CORS configuration - dynamically include FRONTEND_URL if set
cors_origins = list(settings.BACKEND_CORS_ORIGINS)
if settings.FRONTEND_URL and settings.FRONTEND_URL not in cors_origins:
    cors_origins.append(settings.FRONTEND_URL)

# Log CORS configuration for debugging
if settings.DEBUG:
    print(f"CORS Origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "Accept-Language"],
    expose_headers=["X-Total-Count", "X-Page", "X-Page-Size"],
    max_age=3600,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": settings.COMPANY_NAME,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Import and register API routers
from app.api import auth, candidates, applications, joining_notices, employees, dashboard, companies, apartments

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates (候補者)"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications (申請)"])
app.include_router(joining_notices.router, prefix="/api/joining-notices", tags=["Joining Notices (入社連絡票)"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees (社員)"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies (派遣先)"])
app.include_router(apartments.router, prefix="/api/apartments", tags=["Apartments (社宅)"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
