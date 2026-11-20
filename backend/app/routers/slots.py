from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from app.schemas.slot import SlotRead
from app.services.slots import (
    business_hours,
    generate_slots,
    owner_today,
    within_booking_window,
)

router = APIRouter()


@router.get("/event-types/{event_type_id}/slots")
def list_event_type_slots(
    event_type_id: int,
    day: Annotated[date, Query(alias="date")],
    session: Annotated[Session, Depends(get_session)],
) -> list[SlotRead]:
    """Свободные слоты типа события на календарный день в поясе владельца."""
    event_type = session.get(EventType, event_type_id)
    if event_type is None or event_type.status != EventTypeStatus.active.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тип события не найден")

    if not within_booking_window(day, owner_today()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата вне окна записи",
        )

    day_start, day_end = business_hours(day)
    # Записи хранятся как naive-UTC; сравниваем с границами дня в том же виде.
    statement = select(Booking).where(
        Booking.start < day_end.replace(tzinfo=None),
        Booking.end > day_start.replace(tzinfo=None),
    )
    busy = [(booking.start, booking.end) for booking in session.scalars(statement)]
    slots = generate_slots(day, event_type.duration_minutes, busy)
    return [SlotRead(start=start, end=end) for start, end in slots]
