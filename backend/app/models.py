from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
# from sqlalchemy.ext.declarative import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


class Event(Base):
    """
    Модель для мероприятий.
    """
    __tablename__ = "events"

    guid = Column(UUID_PG(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=False)
    max_seats = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    # Связь с бронированиями
    bookings = relationship(
        "Booking",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class Booking(Base):
    """
    Модель для бронирований.
    """
    __tablename__ = "bookings"

    guid = Column(UUID_PG(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    event_guid = Column(UUID_PG(as_uuid=True), ForeignKey("events.guid", ondelete="CASCADE"), nullable=False)
    user_phone = Column(String, nullable=False)
    user_nickname = Column(String, nullable=True)
    count_seats = Column(Integer, nullable=False)
    total_cash = Column(Integer, nullable=False)
    verified = Column(Boolean, default=False)
    expired = Column(Boolean, default=False)

    # Новый атрибут для связи с Event
    event = relationship("Event", back_populates="bookings")

    # Поле для файла оплаты
    payment_file = Column(String, nullable=True)
