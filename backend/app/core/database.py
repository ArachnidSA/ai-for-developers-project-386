from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс моделей SQLAlchemy."""


def _connect_args(database_url: str) -> dict[str, object]:
    # SQLite в FastAPI используется из разных потоков, поэтому снимаем проверку потока.
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, connect_args=_connect_args(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Iterator[Session]:
    """Отдаёт сессию БД на время запроса."""
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    """Создаёт таблицы, если их ещё нет."""
    # Импорт регистрирует модели в metadata Base.
    from app.models import booking, event_type  # noqa: F401

    Base.metadata.create_all(bind=engine)
