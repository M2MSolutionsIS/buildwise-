"""
Lightweight E2E test server using SQLite in-memory.

Mirrors the conftest.py approach: creates all tables via SQLAlchemy metadata
(no Alembic), overrides the DB dependency, then serves over HTTP.
"""

import asyncio
import os
import subprocess

# Set env before any imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Prevent Alembic from running by monkey-patching subprocess.Popen
_orig_popen = subprocess.Popen


def _noop_popen(*args, **kwargs):
    """No-op Popen to skip Alembic migration in lifespan."""
    class FakePopen:
        pid = 0
        returncode = 0
        def wait(self): return 0
        def communicate(self): return (b"", b"")
        def poll(self): return 0
    return FakePopen()


subprocess.Popen = _noop_popen

import uvicorn  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

# Import database module and patch it
import app.database as db_module  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

db_module.engine = engine_test
db_module.async_session = async_session_test


async def override_get_db():
    async with async_session_test() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables via SQLAlchemy metadata (SQLite-compatible)."""
    import app.system.models  # noqa: F401
    import app.crm.models  # noqa: F401
    import app.pipeline.models  # noqa: F401
    import app.pm.models  # noqa: F401
    import app.rm.models  # noqa: F401
    import app.bi.models  # noqa: F401

    async with engine_test.begin() as conn:
        await conn.run_sync(db_module.Base.metadata.create_all)


async def main():
    await init_db()

    from app.main import app  # noqa: E402
    from app.core.deps import get_db  # noqa: E402

    app.dependency_overrides[get_db] = override_get_db

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
