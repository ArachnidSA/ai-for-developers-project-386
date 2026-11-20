from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_session
from app.models.booking import Booking
from app.models.event_type import EventType, EventTypeStatus
from app.schemas.booking import BookingCreate, BookingRead, UpcomingBookingRead
from app.services.intervals import overlaps
from app.services.slots import (
    OWNER_TIMEZONE,
    as_utc,
    business_hours,
    owner_today,
    within_booking_window,
)

router = APIRouter()


@router.get("/bookings", response_model_exclude_none=True)
def list_upcoming_bookings(
    session: Annotated[Session, Depends(get_session)],
) -> list[UpcomingBookingRead]:
    """Предстоящие записи всех типов (в том числе архивных), по возрастанию начала.

    «Прошедшая» запись — та, что уже закончилась (`end` в прошлом). Время в БД —
    naive-UTC; в ответе поля приводятся к aware-UTC схемой.
    """
    now = datetime.now(UTC).replace(tzinfo=None)
    bookings = session.scalars(
        select(Booking)
        .where(Booking.end > now)
        .order_by(Booking.start)
        .options(selectinload(Booking.event_type))
    ).all()
    return [
        UpcomingBookingRead(
            id=booking.id,
            event_type_id=booking.event_type_id,
            event_type_name=booking.event_type.name,
            guest_name=booking.guest_name,
            guest_email=booking.guest_email,
            note=booking.note,
            start=booking.start,
            end=booking.end,
        )
        for booking in bookings
    ]


@router.post("/bookings", status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
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


@router.delete("/bookings/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    id: int,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    """Удалить запись, освободив её слот. Несуществующая запись — 404.

    Слот освобождается как следствие: свободные слоты считаются из существующих
    записей, поэтому отдельной пометки не требуется.
    """
    booking = session.get(Booking, id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")
    session.delete(booking)
    session.commit()
