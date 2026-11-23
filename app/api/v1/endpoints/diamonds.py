from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.auth import User
from app.models.inventory import Diamond, DiamondGenealogy
from app.schemas.diamonds import DiamondCreate, DiamondResponse, DiamondSplitRequest
from app.middleware.rbac import get_current_user, get_optional_current_user, require_roles

router = APIRouter()

@router.get("/", response_model=List[DiamondResponse])
def list_diamonds(
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    query = db.query(Diamond)
    if current_user:
        query = query.filter(Diamond.organization_id == current_user.organization_id)
    if stage:
        query = query.filter(Diamond.stage == stage)
    if status:
        query = query.filter(Diamond.status == status)
    if department_id:
        query = query.filter(Diamond.current_department_id == department_id)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=DiamondResponse, status_code=status.HTTP_201_CREATED)
def create_diamond(
    diamond_in: DiamondCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "CTO", "PURCHASE_MANAGER", "PRODUCTION_MANAGER"]))
):
    existing = db.query(Diamond).filter(
        Diamond.organization_id == diamond_in.organization_id,
        Diamond.diamond_id == diamond_in.diamond_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Diamond serial '{diamond_in.diamond_id}' already exists")

    new_diamond = Diamond(**diamond_in.model_dump())
    db.add(new_diamond)
    db.commit()
    db.refresh(new_diamond)
    return new_diamond

@router.get("/{diamond_id}", response_model=DiamondResponse)
def get_diamond(
    diamond_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diamond = db.query(Diamond).filter(
        Diamond.id == diamond_id,
        Diamond.organization_id == current_user.organization_id
    ).first()
    if not diamond:
        raise HTTPException(status_code=404, detail="Diamond not found")
    return diamond

@router.post("/split", response_model=List[DiamondResponse])
def split_diamond(
    split_req: DiamondSplitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "CTO", "PRODUCTION_MANAGER"]))
):
    """
    Splits a single rough or semi-polished parent diamond into 2 or more child stones.
    Maintains complete provenance tree in diamond_genealogy table.
    """
    parent = db.query(Diamond).filter(
        Diamond.id == split_req.parent_diamond_id,
        Diamond.organization_id == current_user.organization_id
    ).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent diamond not found")

    total_allocated = sum(child.allocated_weight_carat for child in split_req.children)
    if total_allocated > parent.current_weight_carat:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot allocate {total_allocated} ct: exceeds parent stone weight of {parent.current_weight_carat} ct"
        )

    created_children = []
    for child_spec in split_req.children:
        child_diamond = Diamond(
            organization_id=parent.organization_id,
            branch_id=parent.branch_id,
            lot_id=parent.lot_id,
            parent_diamond_id=parent.id,
            diamond_id=child_spec.diamond_id,
            tracking_mode=parent.tracking_mode,
            stage="SAWING_4P",
            status="AVAILABLE",
            current_department_id=parent.current_department_id,
            rough_weight_carat=child_spec.allocated_weight_carat,
            current_weight_carat=child_spec.allocated_weight_carat,
            shape=child_spec.expected_shape
        )
        db.add(child_diamond)
        db.flush()

        genealogy = DiamondGenealogy(
            organization_id=parent.organization_id,
            parent_diamond_id=parent.id,
            child_diamond_id=child_diamond.id,
            operation_type="SPLIT_SAWING",
            carat_weight_allocated=child_spec.allocated_weight_carat,
            performed_by=current_user.id,
            notes=split_req.notes
        )
        db.add(genealogy)
        created_children.append(child_diamond)

    # Parent is now marked as split / transformed
    parent.status = "SCRAPPED"
    db.commit()
    for child in created_children:
        db.refresh(child)
    return created_children
