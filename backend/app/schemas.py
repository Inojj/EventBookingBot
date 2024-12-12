from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# Общие схемы
class SuccessResponse(BaseModel):
    """
    Общая схема для успешных ответов.
    """
    success: bool = Field(..., example=True)


class ErrorResponse(BaseModel):
    """
    Общая схема для ошибок.
    """
    error: str = Field(..., example="Мероприятие не найдено")
    code: int = Field(..., example=404)


# Схемы для мероприятий
class CreateEventRequest(BaseModel):
    """
    Схема для создания мероприятия.
    """
    name: str = Field(..., example="Концерт группы XYZ")
    text: str = Field(..., example="Невероятное музыкальное шоу!")
    max_seats: int = Field(..., example=100)
    price: int = Field(..., example=500)


class UpdateEventRequest(BaseModel):
    """
    Схема для обновления мероприятия.
    """
    name: Optional[str] = Field(None, example="Новое название мероприятия")
    text: Optional[str] = Field(None, example="Обновлённое описание мероприятия")
    max_seats: Optional[int] = Field(None, example=150)
    price: Optional[int] = Field(None, example=700)


class EventResponse(BaseModel):
    """
    Схема для возврата информации о мероприятии.
    """
    guid: UUID
    name: str
    text: str
    max_seats: int
    price: int

    class Config:
        orm_mode = True


# Схемы для бронирований
class CreateBookingRequest(BaseModel):
    """
    Схема для создания бронирования.
    """
    event_guid: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    user_phone: str = Field(..., example="+71234567890")
    user_nickname: Optional[str] = Field(None, example="user123")
    count_seats: int = Field(..., example=2)
    total_cash: int = Field(..., example=1000)


class UpdateBookingRequest(BaseModel):
    """
    Схема для обновления бронирования.
    """
    user_phone: Optional[str] = Field(None, example="+71234567890")
    user_nickname: Optional[str] = Field(None, example="new_nickname")
    count_seats: Optional[int] = Field(None, example=3)
    total_cash: Optional[int] = Field(None, example=1500)
    verified: Optional[bool] = Field(None, example=True)
    expired: Optional[bool] = Field(None, example=False)


class BookingResponse(BaseModel):
    """
    Схема для возврата информации о бронировании.
    """
    guid: UUID
    event_guid: UUID
    user_phone: str
    user_nickname: Optional[str]
    count_seats: int
    total_cash: int
    verified: bool
    expired: bool

    class Config:
        orm_mode = True


class CreateOrUpdateBookingResponse(BaseModel):
    """
    Схема для ответа при создании или обновлении бронирования.
    """
    guid: UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
