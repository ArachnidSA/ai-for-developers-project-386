from pydantic import BaseModel, ConfigDict, Field

from app.models.event_type import EventTypeStatus


class EventTypeCreate(BaseModel):
    """Данные для создания типа события."""

    name: str
    description: str
    duration_minutes: int = Field(ge=5, le=720)


class EventTypeRead(BaseModel):
    """Тип события в ответе API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    duration_minutes: int
    status: EventTypeStatus
