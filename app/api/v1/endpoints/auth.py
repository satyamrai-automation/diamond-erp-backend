import random
from typing import List, Optional
from uuid import UUID
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.auth import User, Role, Department, Organization, Worker
from app.schemas.auth import (
    LoginRequest, 
    Token, 
    UserResponse, 
    RegisterRequest, 
    RegisterResponse, 
    PendingEmployeeResponse
)
from app.middleware.rbac import get_current_user, get_optional_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is pending verification by the Admin/CTO. Please wait for approval."
        )

    role_code = user.role.code if user.role else "USER"
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "org_id": str(user.organization_id),
            "role": role_code,
            "is_super_admin": user.is_super_admin
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "user_info": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": role_code,
            "employee_code": user.employee_code,
            "is_super_admin": user.is_super_admin,
            "department_id": str(user.department_id) if user.department_id else None
        }
    }

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    # 2. Get default organization
    org = db.query(Organization).first()
    if not org:
        raise HTTPException(status_code=500, detail="Default organization not found in database")

    is_employee = req.account_type.upper() == "EMPLOYEE"
    
    # 3. Handle Role and Department Resolution
    if is_employee:
        # Generate official Employee Code (e.g. EMP-SUR-2026-4821)
        rand_num = random.randint(1000, 9999)
        code = f"EMP-SUR-2026-{rand_num}"
        
        # Match Role
        role = None
        if req.role_code:
            role = db.query(Role).filter(Role.code == req.role_code).first()
        if not role:
            role = db.query(Role).filter(Role.code == "WORKER").first()
        
        # Match Department
        dept = None
        if req.department_code:
            dept = db.query(Department).filter(Department.code == req.department_code).first()
        if not dept:
            dept = db.query(Department).filter(Department.is_production_floor == True).first()
            
        # Employee requires Admin/CTO verification
        is_active = False
        requires_approval = True
        msg = f"Employee registration submitted! Employee ID '{code}' generated. A verification notification has been sent to the Admin/CTO. You will be activated upon approval."
    else:
        # Generate Client VIP ID (e.g. CLI-2026-7812)
        rand_num = random.randint(1000, 9999)
        code = f"CLI-2026-{rand_num}"
        
        role = db.query(Role).filter(Role.code == "CLIENT_USER").first()
        if not role:
            # Fallback to any user role
            role = db.query(Role).filter(Role.code != "SUPER_ADMIN").first()
        dept = None
        
        # Client user is automatically activated
        is_active = True
        requires_approval = False
        msg = f"Client registration successful! Your permanent Client ID is '{code}'. You can now log in immediately."

    if not role:
        raise HTTPException(status_code=500, detail="Could not assign a system role")

    # 4. Create and Save User in PostgreSQL
    hashed_pwd = get_password_hash(req.password)
    new_user = User(
        organization_id=org.id,
        role_id=role.id,
        department_id=dept.id if dept else None,
        employee_code=code,
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        password_hash=hashed_pwd,
        is_active=is_active,
        is_super_admin=False
    )
    db.add(new_user)
    db.flush()

    # If worker/karigar, create draft worker profile
    if is_employee and role.code == "WORKER" and dept:
        worker = Worker(
            user_id=new_user.id,
            organization_id=org.id,
            department_id=dept.id,
            station_no=f"STATION-{random.randint(1, 40)}",
            specialty=req.specialty or "Crown & Pavilion Polisher",
            wage_type="PIECE_RATE_CARAT",
            base_rate_per_carat=90.00,
            skill_level="EXPERT"
        )
        db.add(worker)

    db.commit()
    db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "user_id_code": code,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "account_type": req.account_type.upper(),
        "is_active": new_user.is_active,
        "requires_approval": requires_approval,
        "message": msg
    }

@router.get("/pending-employees", response_model=List[PendingEmployeeResponse])
def list_pending_employees(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns pending employee registrations awaiting verification by Admin/CTO.
    """
    pending = db.query(User).filter(
        User.is_active == False,
        User.employee_code.like("EMP-%")
    ).order_by(User.created_at.desc()).all()

    results = []
    for u in pending:
        results.append({
            "id": str(u.id),
            "employee_code": u.employee_code,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "department_name": u.department.name if u.department else "General Manufacturing Floor",
            "role_name": u.role.name if u.role else "Worker / Operator",
            "created_at": u.created_at
        })
    return results

@router.post("/approve-employee/{user_id}")
def approve_employee(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Admin verifies and activates an employee.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")

    user.is_active = True
    db.commit()
    return {
        "status": "success",
        "message": f"Employee {user.full_name} ({user.employee_code}) has been verified and activated!"
    }

@router.post("/reject-employee/{user_id}")
def reject_employee(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Admin rejects and removes a pending employee application.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp_name = user.full_name
    db.delete(user)
    db.commit()
    return {
        "status": "success",
        "message": f"Employee application for {emp_name} has been rejected and removed."
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
