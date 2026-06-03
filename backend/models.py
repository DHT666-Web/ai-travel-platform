from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), default="user")


class TravelPlan(Base):
    __tablename__ = "travel_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    destination = Column(String(100), nullable=False)
    days = Column(Integer, nullable=False)
    preference = Column(String(200), nullable=True)
    plan_content = Column(Text, nullable=True)
    


class ScenicSpot(Base):
    __tablename__ = "scenic_spots"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)
    lng = Column(String(50), nullable=True)
    lat = Column(String(50), nullable=True)
    tags = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(String(50), nullable=True)
    cover_url = Column(String(255), nullable=True)


class AiLog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)