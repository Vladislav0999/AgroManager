from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class Field:
    id: Optional[int] = None
    name: str = ""
    area: float = 0.0
    soil_type: str = ""
    description: str = ""
    created_date: Optional[datetime] = None

@dataclass
class Crop:
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    sowing_season: str = ""
    harvest_period: int = 0
    average_yield: float = 0.0
    description: str = ""

@dataclass
class PlantingPlan:
    id: Optional[int] = None
    field_id: int = 0
    crop_id: int = 0
    season_year: str = ""
    planned_area: float = 0.0
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    status: str = "planned"

@dataclass
class Expense:
    id: Optional[int] = None
    field_id: Optional[int] = None
    crop_id: Optional[int] = None
    expense_type: str = ""
    amount: float = 0.0
    quantity: float = 0.0
    unit: str = ""
    total_cost: float = 0.0
    date: Optional[date] = None
    description: str = ""

@dataclass
class Harvest:
    id: Optional[int] = None
    field_id: int = 0
    crop_id: int = 0
    actual_yield: float = 0.0
    harvest_date: Optional[date] = None
    quality_rating: int = 3
    moisture_content: float = 0.0
    notes: str = ""