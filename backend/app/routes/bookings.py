import os
from fastapi import APIRouter, HTTPException, Depends, Path, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional, Any

from starlette.responses import FileResponse

from app.database import get_db
from app.models import Booking, Event
from app.schemas import (
    CreateBookingRequest,
    UpdateBookingRequest,
    BookingResponse,
    CreateOrUpdateBookingResponse,
    SuccessResponse,
)
from utils.oauth import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"], dependencies=[Depends(get_current_user)])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


@router.get("/", response_model=List[BookingResponse])
async def get_all_bookings(
        event_guid: Optional[UUID] = Query(None, description="GUID мероприятия для фильтрации бронирований"),
        db: AsyncSession = Depends(get_db),
):
    """
    Получить список всех бронирований.
    Если указан параметр event_guid, возвращаются бронирования только для указанного мероприятия.
    """
    query = select(Booking)
    if event_guid:
        query = query.filter(Booking.event_guid == event_guid)

    result = await db.execute(query)
    bookings = result.scalars().all()
    return bookings


@router.post("/{booking_guid}/upload-payment-file")
async def upload_payment_file(
        booking_guid: UUID,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Загрузка файла оплаты для бронирования.
    """
    # Проверяем существование бронирования
    result = await db.execute(select(Booking).filter(Booking.guid == booking_guid))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    # Сохраняем файл
    file_path = os.path.join(UPLOAD_DIR, f"{booking_guid}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Сохраняем путь к файлу в базе данных
    booking.payment_file = file_path
    await db.commit()

    return {"detail": "Файл успешно загружен."}


@router.get("/{booking_guid}/payment-file", response_class=FileResponse)
async def get_payment_file(booking_guid: UUID, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для получения файла оплаты.
    """
    result = await db.execute(select(Booking).filter(Booking.guid == booking_guid))
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if not booking.payment_file or not os.path.exists(booking.payment_file):
        raise HTTPException(status_code=404, detail="Файл оплаты не найден")

    # Определяем MIME-тип файла
    file_path = booking.payment_file
    file_extension = os.path.splitext(file_path)[1].lower()
    mime_type = MIME_TYPES.get(file_extension, "application/octet-stream")

    # Определяем имя файла
    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        media_type=mime_type,  # Указываем MIME-тип
        filename=filename,
        headers={
            'Access-Control-Expose-Headers': 'Content-Disposition',
        }  # Указываем имя файла
    )


@router.post("/", response_model=CreateOrUpdateBookingResponse)
async def create_booking(booking: CreateBookingRequest, db: AsyncSession = Depends(get_db)):
    """
    Создать бронирование.
    """
    # Проверяем, существует ли мероприятие
    result = await db.execute(select(Event).filter(Event.guid == booking.event_guid))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    # Проверяем, достаточно ли свободных мест
    total_booked = await db.execute(
        select(Booking).filter(Booking.event_guid == booking.event_guid)
    )
    total_booked_count = len(total_booked.scalars().all())
    if total_booked_count + booking.count_seats > event.max_seats:
        raise HTTPException(status_code=400, detail="Недостаточно свободных мест")

    # Создаём бронирование
    new_booking = Booking(**booking.dict())
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    return {"guid": new_booking.guid}


@router.get("/{guid}", response_model=BookingResponse)
async def get_booking(guid: UUID, db: AsyncSession = Depends(get_db)):
    """
    Получить информацию о бронировании.
    """
    result = await db.execute(select(Booking).filter(Booking.guid == guid))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return booking


@router.patch("/{guid}", response_model=CreateOrUpdateBookingResponse)
async def update_booking(guid: UUID, update_data: UpdateBookingRequest, db: AsyncSession = Depends(get_db)):
    """
    Обновить бронирование.
    """
    result = await db.execute(select(Booking).filter(Booking.guid == guid))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    # Обновляем только переданные поля
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    await db.commit()
    await db.refresh(booking)
    return {"guid": booking.guid}


@router.delete("/{guid}", response_model=SuccessResponse)
async def delete_booking(guid: UUID, db: AsyncSession = Depends(get_db)):
    """
    Удалить бронирование.
    """
    result = await db.execute(select(Booking).filter(Booking.guid == guid))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    await db.delete(booking)
    await db.commit()
    return {"success": True}
