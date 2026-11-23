from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_info: dict

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    employee_code: str
    phone: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    organization_id: UUID
    department_id: Optional[UUID] = None
    role_id: UUID
    password: str

class UserResponse(UserBase):
    id: UUID
    organization_id: UUID
    department_id: Optional[UUID] = None
    role_id: UUID
    is_super_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    account_type: str = "CLIENT"  # "CLIENT" or "EMPLOYEE"
    department_code: Optional[str] = None
    role_code: Optional[str] = "CLIENT_USER"
    specialty: Optional[str] = None
    government_id: Optional[str] = None

class RegisterResponse(BaseModel):
    id: str
    user_id_code: str
    full_name: str
    email: str
    account_type: str
    is_active: bool
    requires_approval: bool
    message: str

class PendingEmployeeResponse(BaseModel):
    id: str
    employee_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    department_name: Optional[str] = None
    role_name: Optional[str] = None
    created_at: datetime
