from decimal import Decimal
from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_diamonds_in_inventory: int
    total_rough_carats: Decimal
    total_polished_carats: Decimal
    active_work_orders: int
    total_workers_active: int
    total_repolish_diamonds: int
    total_estimated_inventory_usd: Decimal
