from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class DiamondBase(BaseModel):
    diamond_id: str
    tracking_mode: str = "SINGLE_STONE"
    stage: str = "ROUGH"
    status: str = "AVAILABLE"
    rough_weight_carat: Decimal = Field(..., max_digits=10, decimal_places=4)
    current_weight_carat: Decimal = Field(..., max_digits=10, decimal_places=4)
    expected_polished_carat: Optional[Decimal] = None
    shape: Optional[str] = "ROUND"
    color: Optional[str] = None
    clarity: Optional[str] = None
    cut_grade: Optional[str] = None
    polish_grade: Optional[str] = None
    symmetry_grade: Optional[str] = None
    fluorescence: Optional[str] = "NONE"
    laser_inscription_text: Optional[str] = None
    cost_price_inr: Optional[Decimal] = Decimal("0.00")
    estimated_market_value_usd: Optional[Decimal] = Decimal("0.00")

class DiamondCreate(DiamondBase):
    organization_id: UUID
    lot_id: Optional[UUID] = None
    current_department_id: Optional[UUID] = None

class DiamondSplitChild(BaseModel):
    diamond_id: str
    allocated_weight_carat: Decimal = Field(..., max_digits=10, decimal_places=4)
    expected_shape: str = "ROUND"

class DiamondSplitRequest(BaseModel):
    parent_diamond_id: UUID
    children: List[DiamondSplitChild]
    notes: Optional[str] = "Laser sawing 4P division"

class DiamondResponse(DiamondBase):
    id: UUID
    organization_id: UUID
    lot_id: Optional[UUID] = None
    lot_no: Optional[str] = None
    parent_diamond_id: Optional[UUID] = None
    current_department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    current_worker_id: Optional[UUID] = None
    assigned_worker_name: Optional[str] = None
    laser_inscription: Optional[str] = None
    cert_agency: Optional[str] = "GIA"
    cert_number: Optional[str] = None
    estimated_value_usd: Optional[Decimal] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
