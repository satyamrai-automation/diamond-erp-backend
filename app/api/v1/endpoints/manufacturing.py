from typing import List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.auth import User
from app.models.inventory import Diamond
from app.models.manufacturing import WorkOrder, ProductionRecord
from app.schemas.manufacturing import WorkOrderCreate, WorkOrderResponse, ProductionRecordCreate
from app.middleware.rbac import get_current_user, require_roles

router = APIRouter()

@router.get("/work-orders", response_model=List[WorkOrderResponse])
def list_work_orders(
    department_id: UUID = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(WorkOrder).filter(WorkOrder.organization_id == current_user.organization_id)
    if department_id:
        query = query.filter(WorkOrder.department_id == department_id)
    return query.all()

@router.post("/work-orders", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    wo_in: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "CTO", "PRODUCTION_MANAGER"]))
):
    import random
    wo_number = f"WO-{datetime.utcnow().year}-{random.randint(10000, 99999)}"
    
    work_order = WorkOrder(
        organization_id=wo_in.organization_id,
        work_order_no=wo_number,
        diamond_id=wo_in.diamond_id,
        process_type_id=wo_in.process_type_id,
        department_id=wo_in.department_id,
        assigned_worker_id=wo_in.assigned_worker_id,
        target_carats=wo_in.target_carats,
        target_completion_date=wo_in.target_completion_date,
        priority=wo_in.priority,
        created_by=current_user.id
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order

@router.post("/production-records", status_code=status.HTTP_201_CREATED)
def record_production_step(
    record_in: ProductionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logs manufacturing execution.
    Audits input vs output weight, calculates carat loss, and verifies against scale.
    """
    diamond = db.query(Diamond).filter(Diamond.id == record_in.diamond_id).first()
    if not diamond:
        raise HTTPException(status_code=404, detail="Diamond not found")

    if record_in.output_weight_carat and record_in.output_weight_carat > record_in.input_weight_carat:
        raise HTTPException(
            status_code=400,
            detail=f"Weight Anomaly: Output weight ({record_in.output_weight_carat} ct) cannot be greater than input weight ({record_in.input_weight_carat} ct)"
        )

    # Compute labor cost
    labor_rate = record_in.labor_rate_per_carat
    output_carat = record_in.output_weight_carat or record_in.input_weight_carat
    total_labor = labor_rate * output_carat

    record = ProductionRecord(
        organization_id=record_in.organization_id,
        work_order_id=record_in.work_order_id,
        diamond_id=record_in.diamond_id,
        process_type_id=record_in.process_type_id,
        worker_id=record_in.worker_id,
        machine_id=record_in.machine_id,
        input_weight_carat=record_in.input_weight_carat,
        output_weight_carat=record_in.output_weight_carat,
        boort_recovered_carat=record_in.boort_recovered_carat,
        scale_verified_in=record_in.scale_verified_in,
        scale_verified_out=record_in.scale_verified_out,
        labor_rate_per_carat=labor_rate,
        total_labor_cost=total_labor,
        completed_at=datetime.utcnow() if record_in.output_weight_carat else None,
        status="COMPLETED" if record_in.output_weight_carat else "IN_PROGRESS",
        notes=record_in.notes
    )
    db.add(record)

    # Update diamond's current weight
    if record_in.output_weight_carat:
        diamond.current_weight_carat = record_in.output_weight_carat

    db.commit()
    db.refresh(record)
    return {
        "status": "success",
        "record_id": str(record.id),
        "diamond_id": str(diamond.id),
        "weight_loss_carat": str(record_in.input_weight_carat - (record_in.output_weight_carat or record_in.input_weight_carat)),
        "scale_verified": record_in.scale_verified_out,
        "total_labor_cost": str(total_labor)
    }
