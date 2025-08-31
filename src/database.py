from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

Base = declarative_base()
engine = create_engine(config.DB_URL)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

    appointments = relationship('Appointment', back_populates='user')


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    duration = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    appointments = relationship('Appointment', back_populates='service')


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.now)

    user = relationship('User', back_populates='appointments')
    service = relationship('Service', back_populates='appointments')


def init_db():
    Base.metadata.create_all(engine)


def get_db_session():
    return Session()