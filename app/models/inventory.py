import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    country = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(150))
    phone = Column(String(50))
    tax_id = Column(String(50))
    kpcs_license_no = Column(String(100))
    payment_terms_days = Column(Integer, default=30)
    rating = Column(Numeric(3, 2), default=5.00)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    purchases = relationship("Purchase", back_populates="supplier")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    invoice_no = Column(String(100), nullable=False)
    purchase_date = Column(Date, nullable=False, default=date.today)
    total_carats = Column(Numeric(12, 4), nullable=False)
    total_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="USD")
    exchange_rate_to_inr = Column(Numeric(10, 4), default=1.0000)
    kpcs_certificate_no = Column(String(100), nullable=False)
    customs_entry_bill_no = Column(String(100))
    status = Column(String(30), default="CONFIRMED")
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="purchases")
    lots = relationship("DiamondLot", back_populates="purchase")

class DiamondLot(Base):
    __tablename__ = "diamond_lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id", ondelete="SET NULL"))
    lot_no = Column(String(50), nullable=False)
    origin_country = Column(String(100))
    rough_category = Column(String(100))
    initial_carats = Column(Numeric(12, 4), nullable=False)
    remaining_carats = Column(Numeric(12, 4), nullable=False)
    total_pieces_estimated = Column(Integer)
    price_per_carat_usd = Column(Numeric(10, 2), nullable=False)
    total_cost_usd = Column(Numeric(14, 2), nullable=False)
    current_stage = Column(String(50), default="ROUGH")
    is_fully_allocated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    purchase = relationship("Purchase", back_populates="lots")
    diamonds = relationship("Diamond", back_populates="lot")

class Diamond(Base):
    __tablename__ = "diamonds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    lot_id = Column(UUID(as_uuid=True), ForeignKey("diamond_lots.id", ondelete="SET NULL"))
    parent_diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id", ondelete="SET NULL"))

    diamond_id = Column(String(50), nullable=False)
    rfid_tag = Column(String(100))
    barcode_qr = Column(String(100))
    tracking_mode = Column(String(30), default="SINGLE_STONE")
    stage = Column(String(50), default="ROUGH")
    status = Column(String(50), default="AVAILABLE")

    current_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    current_worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id"))

    rough_weight_carat = Column(Numeric(10, 4), nullable=False)
    current_weight_carat = Column(Numeric(10, 4), nullable=False)
    expected_polished_carat = Column(Numeric(10, 4))

    shape = Column(String(50), default="ROUND")
    color = Column(String(10))
    clarity = Column(String(10))
    cut_grade = Column(String(20))
    polish_grade = Column(String(20))
    symmetry_grade = Column(String(20))
    fluorescence = Column(String(20), default="NONE")
    laser_inscription_text = Column(String(100))

    cost_price_inr = Column(Numeric(14, 2), default=0.00)
    estimated_market_value_usd = Column(Numeric(14, 2), default=0.00)
    rapaport_base_price_usd = Column(Numeric(12, 2))
    rapaport_discount_pct = Column(Numeric(5, 2))

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    lot = relationship("DiamondLot", back_populates="diamonds")
    parent = relationship("Diamond", remote_side=[id], backref="children")
    department = relationship("Department", foreign_keys=[current_department_id], lazy="joined")
    worker = relationship("Worker", foreign_keys=[current_worker_id], lazy="joined")

    @property
    def lot_no(self) -> str:
        return self.lot.lot_no if self.lot else "LOT-VAULT-01"

    @property
    def department_name(self) -> str:
        return self.department.name if self.department else "Surat Manufacturing Floor"

    @property
    def assigned_worker_name(self) -> str:
        if self.worker and self.worker.user:
            return self.worker.user.full_name
        return "Karigar Bench Floor"

    @property
    def laser_inscription(self) -> str:
        return self.laser_inscription_text or ""

    @property
    def estimated_value_usd(self):
        return self.estimated_market_value_usd or 0.00

    @property
    def cert_agency(self) -> str:
        txt = (self.laser_inscription_text or "").upper()
        if "IGI" in txt:
            return "IGI"
        if "HRD" in txt:
            return "HRD"
        return "GIA"

    @property
    def cert_number(self) -> str:
        txt = self.laser_inscription_text or ""
        import re
        nums = re.findall(r'\d+', txt)
        return nums[0] if nums else "21950098"

    @property
    def image_url(self) -> str:
        shape_upper = (self.shape or "ROUND").upper()
        images = {
            "ROUND": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80",
            "CUSHION": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
            "EMERALD": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80",
            "PEAR": "https://images.unsplash.com/photo-1615655406736-b37c4fabf923?auto=format&fit=crop&w=800&q=80",
            "OVAL": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80",
        }
        return images.get(shape_upper, "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80")

class DiamondGenealogy(Base):
    __tablename__ = "diamond_genealogy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    parent_diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id", ondelete="CASCADE"), nullable=False)
    child_diamond_id = Column(UUID(as_uuid=True), ForeignKey("diamonds.id", ondelete="CASCADE"), nullable=False)
    operation_type = Column(String(50), default="SPLIT_SAWING")
    carat_weight_allocated = Column(Numeric(10, 4), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
