from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TravelPlanCreate(BaseModel):
    destination: str
    days: int
    preference: Optional[str] = None
    plan_content: Optional[str] = None


class TravelPlanUpdate(BaseModel):
    destination: Optional[str] = None
    days: Optional[int] = None
    preference: Optional[str] = None
    plan_content: Optional[str] = None


class AiPlanRequest(BaseModel):
    destination: str
    days: int
    budget: Optional[str] = None
    preference: Optional[str] = None
    language: Optional[str] = "zh"


class ScenicCreate(BaseModel):
    city: str
    name: str
    address: Optional[str] = None
    lng: Optional[str] = None
    lat: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    cover_url: Optional[str] = None


class ScenicUpdate(BaseModel):
    city: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    lng: Optional[str] = None
    lat: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    cover_url: Optional[str] = None


class ExtractSpotRequest(BaseModel):
    destination: str
    content: str
    language: Optional[str] = "zh"