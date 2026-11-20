from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

# Границы из спеки: рабочие часы 09:00–21:00 в поясе владельца.
OWNER_TZ = ZoneInfo("Asia/Yekaterinburg")


def owner_today() -> date:
    """Сегодняшний день в поясе владельца."""
    return datetime.now(OWNER_TZ).date()


def owner_time(day: date, hour: int, minute: int) -> datetime:
    """Время в поясе владельца, переведённое в UTC."""
    return datetime.combine(day, time(hour, minute), tzinfo=OWNER_TZ).astimezone(UTC)


def create_event_type(client: TestClient, name: str, duration_minutes: int) -> int:
    """Заводит тип события через API и возвращает его id."""
    response = client.post(
        "/api/event-types",
        json={"name": name, "description": "", "duration_minutes": duration_minutes},
    )
    assert response.status_code == 201
    event_type_id = response.json()["id"]
    assert isinstance(event_type_id, int)
    return event_type_id


def archive_event_type(session_factory: sessionmaker[Session], event_type_id: int) -> None:
    """Переводит тип события в архивный напрямую в БД."""
    with session_factory() as session:
        event_type = session.get(EventType, event_type_id)
        assert event_type is not None
        event_type.status = EventTypeStatus.archived.value
        session.commit()


def add_booking(
    session_factory: sessionmaker[Session],
    event_type_id: int,
    start: datetime,
    end: datetime,
    *,
    guest_name: str = "Гость",
    guest_email: str | None = None,
    note: str | None = None,
) -> None:
    """Кладёт запись в БД напрямую (в UTC), минуя HTTP."""
    with session_factory() as session:
        session.add(
            Booking(
                event_type_id=event_type_id,
                guest_name=guest_name,
                guest_email=guest_email,
                note=note,
                start=start.astimezone(UTC).replace(tzinfo=None),
                end=end.astimezone(UTC).replace(tzinfo=None),
            )
        )
        session.commit()


def test_list_returns_upcoming_bookings_sorted_with_contract_fields(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today() + timedelta(days=1)
    event_type_id = create_event_type(client, "Консультация", 60)
    add_booking(
        session_factory,
        event_type_id,
        owner_time(day, 11, 0),
        owner_time(day, 12, 0),
        guest_name="Борис",
        guest_email="boris@example.com",
        note="Позже",
    )
    add_booking(
        session_factory,
        event_type_id,
        owner_time(day, 10, 0),
        owner_time(day, 11, 0),
        guest_name="Анна",
        guest_email="anna@example.com",
        note="Раньше",
    )

    response = client.get("/api/bookings")

    assert response.status_code == 200
    payload = response.json()
    assert [item["guest_name"] for item in payload] == ["Анна", "Борис"]
    first = payload[0]
    assert first["event_type_id"] == event_type_id
    assert first["event_type_name"] == "Консультация"
    assert first["guest_name"] == "Анна"
    assert first["guest_email"] == "anna@example.com"
    assert first["note"] == "Раньше"
    assert datetime.fromisoformat(first["start"]) == owner_time(day, 10, 0)
    assert datetime.fromisoformat(first["end"]) == owner_time(day, 11, 0)


def test_list_omits_unspecified_optional_fields(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    """Предстоящая запись без email и заметки не отдаёт `null` — поля отсутствуют."""
    day = owner_today() + timedelta(days=1)
    event_type_id = create_event_type(client, "Звонок", 30)
    add_booking(
        session_factory,
        event_type_id,
        owner_time(day, 10, 0),
        owner_time(day, 10, 30),
        guest_name="Анна",
    )

    response = client.get("/api/bookings")

    assert response.status_code == 200
    (item,) = response.json()
    assert "guest_email" not in item
    assert "note" not in item


def test_list_excludes_past_bookings(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    past_day = owner_today() - timedelta(days=1)
    future_day = owner_today() + timedelta(days=1)
    event_type_id = create_event_type(client, "Звонок", 30)
    add_booking(
        session_factory,
        event_type_id,
        owner_time(past_day, 10, 0),
        owner_time(past_day, 10, 30),
        guest_name="Прошедший",
    )
    add_booking(
        session_factory,
        event_type_id,
        owner_time(future_day, 10, 0),
        owner_time(future_day, 10, 30),
        guest_name="Предстоящий",
    )

    response = client.get("/api/bookings")

    assert response.status_code == 200
    assert [item["guest_name"] for item in response.json()] == ["Предстоящий"]


def test_list_includes_bookings_of_archived_event_types(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today() + timedelta(days=1)
    event_type_id = create_event_type(client, "Архивный звонок", 30)
    archive_event_type(session_factory, event_type_id)
    add_booking(
        session_factory,
        event_type_id,
        owner_time(day, 10, 0),
        owner_time(day, 10, 30),
        guest_name="Анна",
    )

    response = client.get("/api/bookings")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["event_type_name"] == "Архивный звонок"
    assert payload[0]["event_type_id"] == event_type_id


def test_delete_booking_frees_its_slot(
    client: TestClient,
) -> None:
    day = owner_today() + timedelta(days=1)
    event_type_id = create_event_type(client, "Звонок", 60)
    start = owner_time(day, 10, 0)
    created = client.post(
        "/api/bookings",
        json={"event_type_id": event_type_id, "start": start.isoformat(), "guest_name": "Анна"},
    )
    assert created.status_code == 201
    booking_id = created.json()["id"]

    before = client.get(f"/api/event-types/{event_type_id}/slots", params={"date": day.isoformat()})
    assert before.status_code == 200
    assert start not in [datetime.fromisoformat(slot["start"]) for slot in before.json()]

    response = client.delete(f"/api/bookings/{booking_id}")

    assert response.status_code == 204
    assert response.content == b""
    after = client.get(f"/api/event-types/{event_type_id}/slots", params={"date": day.isoformat()})
    assert after.status_code == 200
    assert start in [datetime.fromisoformat(slot["start"]) for slot in after.json()]

    listed = client.get("/api/bookings")
    assert listed.status_code == 200
    assert listed.json() == []


def test_delete_unknown_booking_is_not_found(client: TestClient) -> None:
    response = client.delete("/api/bookings/999")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert detail
