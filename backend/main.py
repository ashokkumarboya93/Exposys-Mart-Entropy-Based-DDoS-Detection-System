"""
Entropy-Based DDoS Detection Platform — main.py
Production-grade FastAPI application with JWT auth,
MySQL database, rate limiting, and e-commerce simulation.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes import health, metrics, simulation
from app.api.routes import store, admin, attacker, auth
from app.core.config import settings
from app.core.events import lifespan
from app.utils.logger import setup_logging

# ── Logging ──────────────────────────────────────────────────────
setup_logging()

# ── Rate Limiter ────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

# ── Application ─────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ──────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(simulation.router)
app.include_router(metrics.router)
app.include_router(store.router)
app.include_router(admin.router)
app.include_router(attacker.router)

# ── Static File Serving ─────────────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if (FRONTEND_DIR / "store").exists():
    app.mount(
        "/store",
        StaticFiles(directory=str(FRONTEND_DIR / "store"), html=True),
        name="store",
    )

if (FRONTEND_DIR / "admin").exists():
    app.mount(
        "/admin",
        StaticFiles(directory=str(FRONTEND_DIR / "admin"), html=True),
        name="admin",
    )

if (FRONTEND_DIR / "hacker").exists():
    app.mount(
        "/hacker",
        StaticFiles(directory=str(FRONTEND_DIR / "hacker"), html=True),
        name="hacker",
    )


# ── Root Redirect ────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — redirects to the store."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/store/")


# ── Direct Execution ────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
