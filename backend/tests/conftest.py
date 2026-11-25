from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import hash_password
from app.data.areas import seed_areas
from app.db.session import get_db
from app.main import app
from app.models import Base, StaffRole, StaffUser
from app.services.areas import get_active_area
from app.services.rate_limit import rate_limiter

TEST_PASSWORD = "TestPass123!"


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    seed_areas(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    rate_limiter.reset()
    old_env = settings.env
    old_captcha = settings.captcha_provider
    old_key = settings.fernet_key
    settings.env = "test"
    settings.captcha_provider = "mock"
    settings.fernet_key = "test-fernet-key"
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        settings.env = old_env
        settings.captcha_provider = old_captcha
        settings.fernet_key = old_key
        rate_limiter.reset()


@pytest.fixture()
def admin_user(db_session: Session) -> StaffUser:
    user = StaffUser(
        email="admin@example.com",
        full_name="Admin de prueba",
        role=StaffRole.admin,
        password_hash=hash_password(TEST_PASSWORD),
    )
    user.areas = [
        get_active_area(db_session, "adultos-mayores"),
        get_active_area(db_session, "ninez-adolescencia"),
    ]
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def worker_user(db_session: Session) -> StaffUser:
    user = StaffUser(
        email="worker@example.com",
        full_name="Trabajador de prueba",
        role=StaffRole.social_worker,
        password_hash=hash_password(TEST_PASSWORD),
    )
    user.areas = [get_active_area(db_session, "adultos-mayores")]
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def report_payload() -> dict[str, object]:
    return {
        "situation_type": "neglect",
        "incident_date": "2026-11-01",
        "affected_name": "María José Pérez",
        "age_range": "range_70_79",
        "locality": "Aguilares",
        "address": "Calle Sarmiento 123",
        "description": "La persona permanece sin atención médica desde hace semanas.",
    }
