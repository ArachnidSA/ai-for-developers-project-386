from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from app.schemas.booking import BookingCreate, BookingRead
from app.services.intervals import overlaps
from app.services.slots import (
    OWNER_TIMEZONE,
    as_utc,
    business_hours,
    owner_today,
    within_booking_window,
)

router = APIRouter()


@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    session: Annotated[Session, Depends(get_session)],
) -> BookingRead:
    """Создать запись гостем."""
    event_type = session.get(EventType, payload.event_type_id)
    if event_type is None or event_type.status != EventTypeStatus.active.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тип события не найден")

    start = as_utc(payload.start)
    end = start + timedelta(minutes=event_type.duration_minutes)
    # В БД время хранится как naive-UTC, поэтому и сравнения ведём в том же виде.
    start_naive = start.replace(tzinfo=None)
    end_naive = end.replace(tzinfo=None)

    # Рабочие часы и окно записи считаются в поясе владельца (ADR-0002).
    day = start.astimezone(OWNER_TIMEZONE).date()
    if not within_booking_window(day, owner_today()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Время вне окна записи")

    day_start, day_end = business_hours(day)
    if start < day_start or end > day_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время вне рабочих часов",
        )

    # Полуинтервалы [start, end): пересечение, если booking.start < end и start < booking.end.
    # SQL сужает кандидатов, решение принимает единый помощник `overlaps`.
    candidates = session.scalars(
        select(Booking).where(Booking.start < end_naive, Booking.end > start_naive)
    )
    if any(overlaps(start_naive, end_naive, item.start, item.end) for item in candidates):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Это время уже занято, выберите другой слот",
        )

    booking = Booking(
        event_type_id=event_type.id,
        guest_name=payload.guest_name,
        guest_email=payload.guest_email,
        note=payload.note,
        start=start_naive,
        end=end_naive,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return BookingRead.model_validate(booking)
