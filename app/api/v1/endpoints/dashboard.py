from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.auth import User, Worker
from app.models.inventory import Diamond
from app.models.manufacturing import WorkOrder
from app.schemas.dashboard import DashboardStatsResponse
from app.middleware.rbac import get_optional_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    query_diamonds = db.query(Diamond).filter(Diamond.status != "SCRAPPED")
    query_wo = db.query(WorkOrder).filter(WorkOrder.status.in_(["PENDING", "IN_PROGRESS"]))
    query_workers = db.query(Worker)

    if current_user:
        org_id = current_user.organization_id
        query_diamonds = query_diamonds.filter(Diamond.organization_id == org_id)
        query_wo = query_wo.filter(WorkOrder.organization_id == org_id)
        query_workers = query_workers.filter(Worker.organization_id == org_id)

    # 1. Total Diamonds Count
    total_diamonds = query_diamonds.count()

    # 2. Total Rough Carats
    rough_carats = query_diamonds.filter(Diamond.stage == "ROUGH").with_entities(
        func.sum(Diamond.current_weight_carat)
    ).scalar() or Decimal("0.0000")

    # 3. Total Polished Carats
    polished_carats = query_diamonds.filter(
        Diamond.stage.in_(["CERTIFIED", "IN_VAULT"])
    ).with_entities(
        func.sum(Diamond.current_weight_carat)
    ).scalar() or Decimal("0.0000")

    # 4. Active Work Orders
    active_wo = query_wo.count()

    # 5. Active Workers
    active_workers = query_workers.count()

    # 6. Repolish Count
    repolish_count = query_diamonds.filter(Diamond.status == "HOLD_REPOLISH").count()

    # 7. Total Estimated Value USD
    total_val = query_diamonds.with_entities(
        func.sum(Diamond.estimated_market_value_usd)
    ).scalar() or Decimal("0.00")

    return {
        "total_diamonds_in_inventory": total_diamonds,
        "total_rough_carats": rough_carats,
        "total_polished_carats": polished_carats,
        "active_work_orders": active_wo,
        "total_workers_active": active_workers,
        "total_repolish_diamonds": repolish_count,
        "total_estimated_inventory_usd": total_val
    }
