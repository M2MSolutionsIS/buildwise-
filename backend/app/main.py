"""FastAPI application entry point."""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logger = logging.getLogger("buildwise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("BuildWise ERP starting — prototype %s", settings.DEFAULT_PROTOTYPE)
    # Temporary debug: log DATABASE_URL prefix to verify Railway env
    db_url = os.environ.get("DATABASE_URL", "NOT SET")
    logger.info("DATABASE_URL prefix: %s", db_url[:20])

    # Run Alembic migrations in background so the server starts immediately
    import subprocess
    logger.info("Starting Alembic migrations in background…")
    subprocess.Popen(
        ["alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )

    yield
    logger.info("BuildWise ERP shutting down")


app = FastAPI(
    title="BuildWise ERP",
    description="Platformă ERP verticală pentru eficiență energetică a clădirilor",
    version="0.1.0",
    docs_url="/api/docs" if settings.APP_DEBUG else None,
    redoc_url="/api/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Import all models so they're registered with SQLAlchemy ─────────────────
from app.system import models as system_models  # noqa: F401, E402
from app.crm import models as crm_models  # noqa: F401, E402
from app.pipeline import models as pipeline_models  # noqa: F401, E402
from app.pm import models as pm_models  # noqa: F401, E402
from app.rm import models as rm_models  # noqa: F401, E402
from app.bi import models as bi_models  # noqa: F401, E402

# ─── Register routers ────────────────────────────────────────────────────────
from app.system.router import auth_router, health_router, system_router, user_router  # noqa: E402
from app.crm.router import crm_router  # noqa: E402
from app.pipeline.router import pipeline_router  # noqa: E402
from app.pm.router import pm_router  # noqa: E402
from app.rm.router import rm_router  # noqa: E402
from app.bi.router import bi_router  # noqa: E402
from app.search.router import search_router  # noqa: E402

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(system_router)
app.include_router(crm_router)
app.include_router(pipeline_router)
app.include_router(pm_router)
app.include_router(rm_router)
app.include_router(bi_router)
app.include_router(search_router)
