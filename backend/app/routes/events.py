from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.models import Event
from app.schemas import (
    CreateEventRequest,
    UpdateEventRequest,
    EventResponse,
    SuccessResponse,
)
from utils.oauth import get_current_user

router = APIRouter(prefix="/events",
                   tags=["events"],
                   dependencies=[Depends(get_current_user)]
                   )


@router.get("/", response_model=List[EventResponse])
async def get_all_events(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех мероприятий.
    """
    result = await db.execute(select(Event))
    events = result.scalars().all()
    return events


@router.post("/", response_model=EventResponse)
async def create_event(event: CreateEventRequest, db: AsyncSession = Depends(get_db)):
    """
    Создать мероприятие.
    """
    db_event = Event(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event


@router.get("/{guid}", response_model=EventResponse)
async def get_event(guid: UUID, db: AsyncSession = Depends(get_db)):
    """
    Получить информацию о мероприятии.
    """
    result = await db.execute(select(Event).filter(Event.guid == guid))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return event


@router.patch("/{guid}", response_model=SuccessResponse)
async def update_event(guid: UUID, event: UpdateEventRequest, db: AsyncSession = Depends(get_db)):
    """
    Обновить информацию о мероприятии.
    """
    result = await db.execute(select(Event).filter(Event.guid == guid))
    db_event = result.scalars().first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    # Обновляем только переданные поля
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)

    await db.commit()
    return {"success": True}


@router.delete("/{guid}", response_model=SuccessResponse)
async def delete_event(guid: UUID, db: AsyncSession = Depends(get_db)):
    """
    Удалить мероприятие.
    """
    result = await db.execute(select(Event).filter(Event.guid == guid))
    db_event = result.scalars().first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    await db.delete(db_event)
    await db.commit()
    return {"success": True}
