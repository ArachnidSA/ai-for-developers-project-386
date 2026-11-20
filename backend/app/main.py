from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import bookings, event_types, health, slots


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Готовит хранилище к работе при старте приложения."""
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(event_types.router, prefix="/api", tags=["event-types"])
app.include_router(slots.router, prefix="/api", tags=["slots"])
app.include_router(bookings.router, prefix="/api", tags=["bookings"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
