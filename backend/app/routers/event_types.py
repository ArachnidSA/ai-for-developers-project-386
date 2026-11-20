from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.event_type import EventType, EventTypeStatus
from app.schemas.event_type import EventTypeCreate, EventTypeRead

router = APIRouter()


@router.get("/event-types")
def list_event_types(session: Annotated[Session, Depends(get_session)]) -> list[EventTypeRead]:
    """Список типов событий. Гостю — только действующие, владельцу — все."""
    statement = (
        select(EventType)
        .where(EventType.status == EventTypeStatus.active)
        .order_by(EventType.id)
    )
    return [EventTypeRead.model_validate(event_type) for event_type in session.scalars(statement)]


@router.post("/event-types", status_code=status.HTTP_201_CREATED)
def create_event_type(
    payload: EventTypeCreate,
    session: Annotated[Session, Depends(get_session)],
) -> EventTypeRead:
    """Создать тип события."""
    event_type = EventType(
        name=payload.name,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        status=EventTypeStatus.active.value,
    )
    session.add(event_type)
    session.commit()
    session.refresh(event_type)
    return EventTypeRead.model_validate(event_type)
