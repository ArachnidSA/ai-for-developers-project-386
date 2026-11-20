from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

# Границы из спеки: рабочие часы 09:00–21:00 в поясе владельца.
OWNER_TZ = ZoneInfo("Asia/Yekaterinburg")
BUSINESS_START = time(9, 0)
BUSINESS_END = time(21, 0)


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


def add_booking(
    session_factory: sessionmaker[Session],
    event_type_id: int,
    start: datetime,
    end: datetime,
) -> None:
    """Кладёт запись в БД напрямую (в UTC), минуя ещё не сделанный API записей."""
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


def get_slots(client: TestClient, event_type_id: int, day: date) -> list[dict[str, str]]:
    response = client.get(
        f"/api/event-types/{event_type_id}/slots",
        params={"date": day.isoformat()},
    )
    assert response.status_code == 200
    slots = response.json()
    assert isinstance(slots, list)
    return slots


def test_slots_start_every_event_duration(client: TestClient) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=30)

    slots = get_slots(client, event_type_id, day)

    starts = [datetime.fromisoformat(slot["start"]) for slot in slots]
    # 09:00–21:00 при шаге 30 минут — ровно 24 слота без пропусков.
    assert starts[0] == owner_time(day, 9, 0)
    assert len(starts) == 24
    assert starts == [starts[0] + timedelta(minutes=30) * index for index in range(24)]


def test_last_slot_ends_at_business_day_end(client: TestClient) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=60)

    slots = get_slots(client, event_type_id, day)

    # 09:00–21:00 при шаге 60 минут — 12 слотов, последний заканчивается ровно в 21:00.
    assert len(slots) == 12
    assert datetime.fromisoformat(slots[-1]["start"]) == owner_time(day, 20, 0)
    assert datetime.fromisoformat(slots[-1]["end"]) == owner_time(day, 21, 0)


def test_slots_are_returned_in_utc(client: TestClient) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=30)

    slots = get_slots(client, event_type_id, day)

    # 09:00 по поясу владельца (UTC+5) — это 04:00 UTC, время отдаётся с признаком UTC.
    first = slots[0]["start"]
    assert first.startswith(f"{day.isoformat()}T04:00:00")
    assert first.endswith(("Z", "+00:00"))


def test_booking_removes_overlapping_slot(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=30)
    add_booking(session_factory, event_type_id, owner_time(day, 10, 0), owner_time(day, 10, 30))

    starts = [
        datetime.fromisoformat(slot["start"]) for slot in get_slots(client, event_type_id, day)
    ]

    assert owner_time(day, 10, 0) not in starts
    assert owner_time(day, 9, 30) in starts
    assert owner_time(day, 10, 30) in starts


def test_booking_of_another_type_also_blocks_slot(
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

    starts = [
        datetime.fromisoformat(slot["start"]) for slot in get_slots(client, other_type_id, day)
    ]

    assert owner_time(day, 10, 0) not in starts
    assert owner_time(day, 10, 30) not in starts


def test_adjacent_booking_does_not_block_neighbor(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    day = owner_today()
    event_type_id = create_event_type(client, duration_minutes=30)
    add_booking(session_factory, event_type_id, owner_time(day, 9, 0), owner_time(day, 9, 30))

    starts = [
        datetime.fromisoformat(slot["start"]) for slot in get_slots(client, event_type_id, day)
    ]

    assert owner_time(day, 9, 0) not in starts
    assert owner_time(day, 9, 30) in starts


def test_last_day_of_booking_window_is_allowed(client: TestClient) -> None:
    day = owner_today() + timedelta(days=13)
    event_type_id = create_event_type(client, duration_minutes=30)

    slots = get_slots(client, event_type_id, day)

    assert slots[0]["start"].startswith(day.isoformat())


def test_slots_for_past_date_is_rejected(client: TestClient) -> None:
    day = owner_today() - timedelta(days=1)
    event_type_id = create_event_type(client, duration_minutes=30)

    response = client.get(
        f"/api/event-types/{event_type_id}/slots",
        params={"date": day.isoformat()},
    )

    assert response.status_code == 400


def test_slots_beyond_booking_window_is_rejected(client: TestClient) -> None:
    day = owner_today() + timedelta(days=14)
    event_type_id = create_event_type(client, duration_minutes=30)

    response = client.get(
        f"/api/event-types/{event_type_id}/slots",
        params={"date": day.isoformat()},
    )

    assert response.status_code == 400


def test_slots_for_unknown_event_type_is_not_found(client: TestClient) -> None:
    response = client.get(
        "/api/event-types/999/slots",
        params={"date": owner_today().isoformat()},
    )

    assert response.status_code == 404


def test_slots_for_archived_event_type_is_not_found(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)
    with session_factory() as session:
        event_type = session.get(EventType, event_type_id)
        assert event_type is not None
        event_type.status = EventTypeStatus.archived.value
        session.commit()

    response = client.get(
        f"/api/event-types/{event_type_id}/slots",
        params={"date": owner_today().isoformat()},
    )

    assert response.status_code == 404


def test_slots_reject_malformed_date(client: TestClient) -> None:
    event_type_id = create_event_type(client, duration_minutes=30)

    response = client.get(
        f"/api/event-types/{event_type_id}/slots",
        params={"date": "не-дата"},
    )

    assert response.status_code == 422
