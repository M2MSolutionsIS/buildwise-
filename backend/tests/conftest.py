"""
Pytest fixtures for BuildWise backend tests.

Uses SQLite in-memory for fast testing without PostgreSQL dependency.
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import hash_password
from app.database import Base
from app.core.deps import get_db

# Import all models so they register with Base.metadata before create_all
import app.system.models  # noqa: F401
import app.crm.models  # noqa: F401
import app.pipeline.models  # noqa: F401
import app.pm.models  # noqa: F401
import app.rm.models  # noqa: F401
import app.bi.models  # noqa: F401


# Use SQLite for tests (async via aiosqlite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with async_session_test() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Async test client with DB override."""
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_org(db_session: AsyncSession):
    """Create a test organization."""
    from app.system.models import Organization

    org = Organization(
        id=uuid.uuid4(),
        name="Test Company",
        slug="test-company",
        active_prototype="P1",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession, test_org):
    """Create an admin role for the test org."""
    from app.system.models import Role

    role = Role(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        name="Administrator",
        code="admin",
        is_system=True,
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_org, test_role):
    """Create a test user with admin role."""
    from app.system.models import User, UserRole

    user = User(
        id=uuid.uuid4(),
        email="test@buildwise.ro",
        password_hash=hash_password("TestPass123!"),
        first_name="Test",
        last_name="User",
        organization_id=test_org.id,
        is_active=True,
        gdpr_consent=True,
        gdpr_consent_date=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(
        id=uuid.uuid4(),
        user_id=user.id,
        role_id=test_role.id,
    )
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user)
    return user
