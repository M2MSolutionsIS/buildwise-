"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="BuildWise ERP",
    description="Platformă ERP verticală pentru eficiență energetică a clădirilor",
    version="0.1.0",
    docs_url="/api/docs" if settings.APP_DEBUG else None,
    redoc_url="/api/redoc" if settings.APP_DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0", "prototype": settings.DEFAULT_PROTOTYPE}


# Import all models so they're registered with SQLAlchemy
from app.system import models as system_models  # noqa: F401, E402
from app.crm import models as crm_models  # noqa: F401, E402
from app.pipeline import models as pipeline_models  # noqa: F401, E402
from app.pm import models as pm_models  # noqa: F401, E402
from app.rm import models as rm_models  # noqa: F401, E402
from app.bi import models as bi_models  # noqa: F401, E402
