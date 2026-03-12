import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.core import settings, logger, VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown tasks."""
    # --- Startup ---
    try:
        # Initialize database tables
        from src.core.database import create_tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Register Telegram commands (only if bot token is available)
        from src.core.config import settings
        if settings.get("TELEGRAM_BOT_TOKEN"):
            from src.api.v1.endpoints.webhooks.telegram import _COMMANDS
            from src.api.v1.endpoints.webhooks import telegram_client as tg
            result = await tg.set_my_commands(_COMMANDS)
            logger.info(f"Telegram commands registered: {result.get('ok')}")
        else:
            logger.info("TELEGRAM_BOT_TOKEN not set, skipping Telegram command registration")
    except Exception as e:
        logger.warning(f"Startup tasks failed: {e}")
    yield
    # --- Shutdown ---


app = FastAPI(
    title="Fina Alibaba Backend",
    description="Financial AI Agent",
    version=VERSION,
    lifespan=lifespan,
)

# CORS middleware configuration
# NOTE: Allow-all is intentional for non-production environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router)


@app.middleware("http")
async def latency_middleware(request: Request, call_next):
    """Track total request latency for all endpoints."""
    start = time.perf_counter()
    response = await call_next(request)
    total_ms = round((time.perf_counter() - start) * 1000,3)
    response.headers["X-Total-Latency-Ms"] = str(total_ms)
    return response


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for container orchestration.

    Used by load balancers and schedulers to verify
    that the service is up and responding.
    """
    return {
        "status": "healthy",
        "service": "fina-alibaba-backend",
        "version": VERSION,
    }