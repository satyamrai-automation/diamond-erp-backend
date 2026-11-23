import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

# Many-to-Many association for Role and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    legal_entity_name = Column(String(200))
    registration_no = Column(String(100))
    tax_id = Column(String(50))
    kpcs_membership_no = Column(String(100))
    headquarters_address = Column(Text)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    branches = relationship("Branch", back_populates="organization", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    branch_type = Column(String(50), default="MANUFACTURING_PLANT")
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100), default="India")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    organization = relationship("Organization", back_populates="branches")
    departments = relationship("Department", back_populates="branch")

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    code = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_production_floor = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    organization = relationship("Organization", back_populates="departments")
    branch = relationship("Branch", back_populates="departments")
    users = relationship("User", back_populates="department")

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    employee_code = Column(String(50), nullable=False)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    worker_profile = relationship("Worker", uselist=False, back_populates="user")

class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    station_no = Column(String(50))
    specialty = Column(String(100))
    wage_type = Column(String(30), default="PIECE_RATE_CARAT")
    base_rate_per_carat = Column(Numeric(10, 2), default=0.00)
    skill_level = Column(String(20), default="MASTER")
    active_jobs_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="worker_profile")
