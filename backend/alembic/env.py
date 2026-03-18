import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.database import Base

# Import all models so they're visible to Alembic
from app.system.models import *  # noqa: F401, F403
from app.crm.models import *  # noqa: F401, F403
from app.pipeline.models import *  # noqa: F401, F403
from app.pm.models import *  # noqa: F401, F403
from app.rm.models import *  # noqa: F401, F403
from app.bi.models import *  # noqa: F401, F403

target_metadata = Base.metadata


def get_url():
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    engine = create_async_engine(get_url())
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


run_migrations_online()
