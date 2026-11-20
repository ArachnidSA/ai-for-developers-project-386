import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Приложению в тестах не нужна файловая БД: подменяем зависимость сессии на
# in-memory SQLite, поэтому переменная окружения лишь отводит реальный движок
# от рабочего `calendar.db`.
os.environ.setdefault("DATABASE_URL", "sqlite://")


@pytest.fixture
def client() -> Iterator[TestClient]:
    """HTTP-клиент с изолированной in-memory БД для каждого теста."""
    from app.core.database import Base, get_session

    # Регистрируем модели в metadata до создания таблиц.
    from app.models import event_type  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_session() -> Iterator[Session]:
        with testing_session() as session:
            yield session

    from app.main import app

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
