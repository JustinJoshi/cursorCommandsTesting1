from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ListingBase(SQLModel):
    title: str
    price: float
    year: int
    model: str
    trim: Optional[str] = None
    mileage: Optional[int] = None
    description: Optional[str] = None
    link: Optional[str] = None
    image_path: Optional[str] = None
    ai_summary: Optional[str] = None
    deal_rating: Optional[str] = None
    estimated_market_value: Optional[float] = None
    source_screenshot: Optional[str] = None


class Listing(ListingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ListingCreate(ListingBase):
    pass


class ListingRead(ListingBase):
    id: int
    captured_at: datetime
    created_at: datetime


class EvalRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price_accuracy: Optional[float] = None
    year_accuracy: Optional[float] = None
    model_accuracy: Optional[float] = None
    description_rouge: Optional[float] = None
    link_extraction_rate: Optional[float] = None
    valid_json_rate: Optional[float] = None
    overall_score: Optional[float] = None
    notes: Optional[str] = None


class CaptureStatus(SQLModel):
    status: str  # "idle", "capturing", "extracting", "done", "error"
    message: Optional[str] = None
    listings_found: int = 0
