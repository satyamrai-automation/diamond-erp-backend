import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ExternalContractor(Base):
    __tablename__ = "external_contractors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    business_name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(150))
    address = Column(Text)
    tax_id = Column(String(50))
    security_deposit_amount = Column(Numeric(12, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Handover(Base):
    __tablename__ = "handovers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    jangad_no = Column(String(50), nullable=False)
    transfer_type = Column(String(50), nullable=False)
    source_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    destination_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    external_contractor_id = Column(UUID(as_uuid=True), ForeignKey("external_contractors.id"))
    dispatched_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    received_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    total_diamonds_count = Column(Integer, nullable=False)
    total_carats_sent = Column(Numeric(12, 4), nullable=False)
    total_carats_received = Column(Numeric(12, 4))
    status = Column(String(50), default="PENDING_DISPATCH")
    dispatched_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expected_return_date = Column(Date)
    received_at = Column(DateTime(timezone=True))
    dispute_reason = Column(Text)
    remarks = Column(Text)

    items = relationship("HandoverItem", back_populates="handover", cascade="all, delete-orphan")

class HandoverItem(Base):
    __tablename__ = "handover_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handover_id = Column(UUID(as_uuid=True), ForeignKey("handovers.id", ondelete="CASCADE"), nullable=False)
    diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id"), nullable=False)
    weight_sent_carat = Column(Numeric(10, 4), nullable=False)
    weight_received_carat = Column(Numeric(10, 4))
    item_status = Column(String(30), default="SENT")
    notes = Column(Text)

    handover = relationship("Handover", back_populates="items")
