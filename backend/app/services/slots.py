from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.services.intervals import overlaps

# Рабочие часы и пояс владельца фиксированы спекой (ADR-0002).
OWNER_TIMEZONE = ZoneInfo("Asia/Yekaterinburg")
BUSINESS_HOURS_START = time(9, 0)
BUSINESS_HOURS_END = time(21, 0)
# Окно записи — 14 календарных дней от «сегодня» в поясе владельца.
BOOKING_WINDOW_DAYS = 14


def as_utc(value: datetime) -> datetime:
    """Приводит время к aware-UTC; naive-значение считается записанным в UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def business_hours(day: date) -> tuple[datetime, datetime]:
    """Границы рабочих часов дня как aware-UTC (`09:00–21:00` по поясу владельца)."""
    start = datetime.combine(day, BUSINESS_HOURS_START, tzinfo=OWNER_TIMEZONE).astimezone(UTC)
    end = datetime.combine(day, BUSINESS_HOURS_END, tzinfo=OWNER_TIMEZONE).astimezone(UTC)
    return start, end


def owner_today(now: datetime | None = None) -> date:
    """Сегодняшний день в поясе владельца."""
    moment = now if now is not None else datetime.now(OWNER_TIMEZONE)
    return moment.astimezone(OWNER_TIMEZONE).date()


def booking_window(today: date) -> tuple[date, date]:
    """Границы окна записи: 14 календарных дней, начиная с `today` включительно."""
    return today, today + timedelta(days=BOOKING_WINDOW_DAYS - 1)


def within_booking_window(day: date, today: date) -> bool:
    """Попадает ли день в окно записи (включая сегодня и 14-й день)."""
    first, last = booking_window(today)
    return first <= day <= last


def generate_slots(
    day: date,
    duration_minutes: int,
    busy: Sequence[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    """Свободные слоты дня: встык с шагом = длительность типа.

    Слоты идут внутри рабочих часов и не выходят за `21:00`. `busy` — занятые
    интервалы (aware или naive UTC); слоты, пересекающиеся с ними, исключаются.
    Возвращает слоты как aware-UTC полуинтервалы `[start, end)`.
    """
    step = timedelta(minutes=duration_minutes)
    limit_start, limit_end = business_hours(day)
    busy_utc = [(as_utc(start), as_utc(end)) for start, end in busy]

    slots: list[tuple[datetime, datetime]] = []
    cursor = limit_start
    while cursor + step <= limit_end:
        slot_end = cursor + step
        if not any(overlaps(cursor, slot_end, start, end) for start, end in busy_utc):
            slots.append((cursor, slot_end))
        cursor = slot_end
    return slots
