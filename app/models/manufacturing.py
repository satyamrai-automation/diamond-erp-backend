import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProcessType(Base):
    __tablename__ = "process_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"))
    standard_sequence_order = Column(Integer, nullable=False)
    default_rate_per_carat = Column(Numeric(10, 2), default=0.00)
    expected_weight_loss_pct_max = Column(Numeric(5, 2), default=30.00)
    is_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    work_order_no = Column(String(50), nullable=False)
    diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id", ondelete="RESTRICT"), nullable=False)
    process_type_id = Column(UUID(as_uuid=True), ForeignKey("process_types.id", ondelete="RESTRICT"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    assigned_worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="SET NULL"))
    target_carats = Column(Numeric(10, 4))
    target_completion_date = Column(Date)
    priority = Column(String(20), default="NORMAL")
    status = Column(String(30), default="PENDING")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="SET NULL"))
    diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id", ondelete="RESTRICT"), nullable=False)
    process_type_id = Column(UUID(as_uuid=True), ForeignKey("process_types.id", ondelete="RESTRICT"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="RESTRICT"), nullable=False)
    machine_id = Column(String(50))
    input_weight_carat = Column(Numeric(10, 4), nullable=False)
    output_weight_carat = Column(Numeric(10, 4))
    boort_recovered_carat = Column(Numeric(10, 4), default=0.0000)
    scale_verified_in = Column(Boolean, default=False)
    scale_verified_out = Column(Boolean, default=False)
    labor_rate_per_carat = Column(Numeric(10, 2), default=0.00)
    total_labor_cost = Column(Numeric(10, 2), default=0.00)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(30), default="IN_PROGRESS")
    supervisor_approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    supervisor_approval_at = Column(DateTime(timezone=True))
    notes = Column(Text)
