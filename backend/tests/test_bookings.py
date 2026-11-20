import threading
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

# Границы из спеки: рабочие часы 09:00–21:00 в поясе владельца.
OWNER_TZ = ZoneInfo("Asia/Yekaterinburg")


def owner_today() -> date:
    """Сегодняшний день в поясе владельца."""
    return datetime.now(OWNER_TZ).date()


def owner_time(day: date, hour: int, minute: int) -> datetime:
    """Время в поясе владельца, переведённое в UTC."""
    return datetime.combine(day, time(hour, minute), tzinfo=OWNER_TZ).astimezone(UTC)


def create_event_type(client: TestClient, duration_minutes: int) -> int:
    """Заводит тип события через API и возвращает его id."""
    response = client.post(
        "/api/event-types",
        json={"name": "Звонок", "description": "", "duration_minutes": duration_minutes},
    )
    assert response.status_code == 201
    event_type_id = response.json()["id"]
    assert isinstance(event_type_id, int)
    return event_type_id


def book(
    client: TestClient,
    event_type_id: int,
    start: datetime,
    *,
    guest_name: str = "Гость",
    guest_email: str | None = None,
    note: str | None = None,
):
    """Отправляет запрос на создание записи."""
    body: dict[str, object] = {
        "event_type_id": event_type_id,
        "start": start.isoformat(),
        "guest_name": guest_name,
    }
    if guest_email is not None:
        body["guest_email"] = guest_email
    if note is not None:
        body["note"] = note
    return client.post("/api/bookings", json=body)


def add_booking(
    session_factory: sessionmaker[Session],
    event_type_id: int,
    start: datetime,
    end: datetime,
) -> None:
    """Кладёт запись в БД напрямую (в UTC), минуя HTTP."""
    with session_factory() as session:
        session.add(
            Booking(
                event_type_id=event_type_id,
                guest_name="Гость",
                guest_email=None,
                note=None,
                start=start.astimezone(UTC).replace(tzinfo=None),
                end=end.astimezone(UTC).replace(tzinfo=None),
            )
        )
        session.commit()


def test_create_booking_returns_created_record(client: TestClient) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=60)

    response = book(
        client,
        event_type_id,
        owner_time(day, 10, 0),
        guest_name="Анна",
        guest_email="anna@example.com",
        note="Обсудить проект",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["event_type_id"] == event_type_id
    assert payload["guest_name"] == "Анна"
    assert payload["guest_email"] == "anna@example.com"
    assert payload["note"] == "Обсудить проект"
    assert isinstance(payload["id"], int)
    # end вычислен сервером как start + duration типа (60 минут).
    assert datetime.fromisoformat(payload["start"]) == owner_time(day, 10, 0)
    assert datetime.fromisoformat(payload["end"]) == owner_time(day, 11, 0)


def test_create_booking_omits_unspecified_optional_fields(client: TestClient) -> None:
    """Незаполненные email и заметка не попадают в JSON (`null` не отдаём).

    Контракт объявляет их необязательными (`guest_email?`, `note?`) — ответ должен
    совпадать с этим представлением, иначе сгенерированный SDK ждёт `string | undefined`.
    """
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(client, event_type_id, owner_time(owner_today(), 10, 0), guest_name="Анна")

    assert response.status_code == 201
    payload = response.json()
    assert "guest_email" not in payload
    assert "note" not in payload


def test_creating_overlapping_booking_is_conflict(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=30)
    add_booking(session_factory, event_type_id, owner_time(day, 10, 0), owner_time(day, 10, 30))

    response = book(client, event_type_id, owner_time(day, 10, 0))

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert detail


def test_conflict_with_booking_of_another_type(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today()
    booked_type_id = create_event_type(client, duration_minutes=60)
    other_type_id = create_event_type(client, duration_minutes=30)
    add_booking(
        session_factory,
        booked_type_id,
        owner_time(day, 10, 0),
        owner_time(day, 11, 0),
    )

    response = book(client, other_type_id, owner_time(day, 10, 30))

    assert response.status_code == 409


def test_adjacent_booking_is_allowed(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    # Касание встык: запись 10:00–11:00 не мешает записи, начинающейся в 11:00.
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=60)
    add_booking(session_factory, event_type_id, owner_time(day, 10, 0), owner_time(day, 11, 0))

    response = book(client, event_type_id, owner_time(day, 11, 0))

    assert response.status_code == 201


def test_partial_overlap_of_different_durations_is_conflict(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    # Запись 60 мин в 10:00 (10:00–11:00), затем 30 мин в 10:30 (10:30–11:00) — пересечение.
    day = owner_today()
    long_type_id = create_event_type(client, duration_minutes=60)
    short_type_id = create_event_type(client, duration_minutes=30)
    add_booking(
        session_factory,
        long_type_id,
        owner_time(day, 10, 0),
        owner_time(day, 11, 0),
    )

    response = book(client, short_type_id, owner_time(day, 10, 30))

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert detail


def test_booking_for_unknown_event_type_is_not_found(client: TestClient) -> None:
    response = book(client, 999, owner_time(owner_today(), 10, 0))

    assert response.status_code == 404


def test_booking_for_archived_event_type_is_not_found(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)
    with session_factory() as session:
        event_type = session.get(EventType, event_type_id)
        assert event_type is not None
        event_type.status = EventTypeStatus.archived.value
        session.commit()

    response = book(client, event_type_id, owner_time(owner_today(), 10, 0))

    assert response.status_code == 404


def test_booking_before_business_hours_is_rejected(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(client, event_type_id, owner_time(owner_today(), 8, 0))

    assert response.status_code == 400


def test_booking_ending_after_business_hours_is_rejected(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=60)

    # 20:30 + 60 минут = 21:30 — за пределами рабочего дня.
    response = book(client, event_type_id, owner_time(owner_today(), 20, 30))

    assert response.status_code == 400


def test_booking_for_past_date_is_rejected(client: TestClient) -> None:
    day = owner_today() - timedelta(days=1)
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(client, event_type_id, owner_time(day, 10, 0))

    assert response.status_code == 400


def test_booking_beyond_window_is_rejected(client: TestClient) -> None:
    day = owner_today() + timedelta(days=14)
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(client, event_type_id, owner_time(day, 10, 0))

    assert response.status_code == 400


def test_booking_rejects_empty_name(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(client, event_type_id, owner_time(owner_today(), 10, 0), guest_name="")

    assert response.status_code == 422


def test_booking_rejects_too_long_name(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(
        client,
        event_type_id,
        owner_time(owner_today(), 10, 0),
        guest_name="Г" * 101,
    )

    assert response.status_code == 422


def test_booking_rejects_malformed_email(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(
        client,
        event_type_id,
        owner_time(owner_today(), 10, 0),
        guest_email="не-email",
    )

    assert response.status_code == 422


def test_booking_rejects_too_long_note(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = book(
        client,
        event_type_id,
        owner_time(owner_today(), 10, 0),
        note="з" * 501,
    )

    assert response.status_code == 422


def test_booking_rejects_malformed_start(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = client.post(
        "/api/bookings",
        json={"event_type_id": event_type_id, "start": "не-дата", "guest_name": "Гость"},
    )

    assert response.status_code == 422


CONCURRENT_REQUESTS = 8


def test_concurrent_bookings_of_same_slot_leave_exactly_one(tmp_path) -> None:
    """Гонка: одновременные запросы на один слот — ровно одна запись, остальные 409.

    Используется реальная файловая SQLite и общий движок приложения: проверка
    непересечения и вставка должны быть атомарны, а писатели — сериализованы.
    """
    from app.core.database import Base, configure_sqlite_engine, get_session
    from app.main import app

    database_url = f"sqlite:///{(tmp_path / 'bookings.db').as_posix()}"
    engine = configure_sqlite_engine(
        create_engine(database_url, connect_args={"check_same_thread": False, "timeout": 30})
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_session():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    statuses: list[int] = []
    statuses_lock = threading.Lock()
    try:
        with TestClient(app) as concurrent_client:
            event_type_id = create_event_type(concurrent_client, duration_minutes=30)
            start = owner_time(owner_today(), 10, 0)
            barrier = threading.Barrier(CONCURRENT_REQUESTS)

            def worker() -> None:
                barrier.wait()
                response = book(concurrent_client, event_type_id, start)
                with statuses_lock:
                    statuses.append(response.status_code)

            threads = [threading.Thread(target=worker) for _ in range(CONCURRENT_REQUESTS)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
    finally:
        app.dependency_overrides.clear()

    assert statuses.count(201) == 1
    assert statuses.count(409) == CONCURRENT_REQUESTS - 1
    with factory() as session:
        assert len(session.scalars(select(Booking)).all()) == 1
