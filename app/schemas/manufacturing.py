from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field

class WorkOrderCreate(BaseModel):
    organization_id: UUID
    diamond_id: UUID
    process_type_id: UUID
    department_id: UUID
    assigned_worker_id: Optional[UUID] = None
    target_carats: Optional[Decimal] = None
    target_completion_date: Optional[date] = None
    priority: str = "NORMAL"

class WorkOrderResponse(BaseModel):
    id: UUID
    work_order_no: str
    diamond_id: UUID
    process_type_id: UUID
    department_id: UUID
    assigned_worker_id: Optional[UUID] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProductionRecordCreate(BaseModel):
    organization_id: UUID
    work_order_id: Optional[UUID] = None
    diamond_id: UUID
    process_type_id: UUID
    worker_id: UUID
    machine_id: Optional[str] = None
    input_weight_carat: Decimal = Field(..., max_digits=10, decimal_places=4)
    output_weight_carat: Optional[Decimal] = Field(None, max_digits=10, decimal_places=4)
    boort_recovered_carat: Optional[Decimal] = Decimal("0.0000")
    scale_verified_in: bool = False
    scale_verified_out: bool = False
    labor_rate_per_carat: Decimal = Decimal("0.00")
    notes: Optional[str] = None
