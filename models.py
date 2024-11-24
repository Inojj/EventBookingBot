from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    phone_number = Column(String)


class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    seats = Column(Integer)
    payment_confirmed = Column(Boolean, default=False)
    event_name = Column(String)


class Link(Base):
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token = Column(String)
    expired = Column(Boolean, default=False)


# Create tables
from database import engine

Base.metadata.create_all(engine)
