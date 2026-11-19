"""Hosting plan endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Conflict, NotFound
from app.logging import setup_logging
from app.models.category import Category
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanOut, PlanUpdate

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.plans")

router = APIRouter(prefix="/plans", tags=["plans"])


def _plan_to_out(plan: Plan) -> PlanOut:
    import json

    features = []
    if plan.features:
        try:
            features = json.loads(plan.features)
        except Exception:  # noqa: BLE001
            features = [plan.features]
    return PlanOut(
        id=plan.id,
        category_id=plan.category_id,
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        short_description=plan.short_description,
        price=plan.price,
        currency=plan.currency,
        billing_cycle=plan.billing_cycle,
        ram_mb=plan.ram_mb,
        cpu=plan.cpu,
        storage_mb=plan.storage_mb,
        disk_mb=plan.disk_mb,
        features=features,
        active=plan.active,
        available=plan.available,
        sort_order=plan.sort_order,
        featured=plan.featured,
        popular=plan.popular,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("", response_model=list[PlanOut])
def list_plans(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None),
    active_only: bool = Query(default=False),
):
    q = db.query(Plan)
    if category:
        q = q.join(Category).filter(Category.slug == category)
    if active_only:
        q = q.filter(Plan.active == True, Plan.available == True)  # noqa: E712
    return [_plan_to_out(p) for p in q.order_by(Plan.sort_order.asc(), Plan.name.asc()).all()]


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise NotFound(message="Plan not found")
    return _plan_to_out(plan)


@router.post("", response_model=PlanOut, status_code=201)
def create_plan(
    payload: PlanCreate,
    request: Request,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    if db.query(Plan).filter_by(slug=payload.slug).first():
        raise Conflict(message="Plan slug already exists", code="slug_exists")
    data = payload.model_dump()
    if isinstance(data.get("features"), list):
        import json
        data["features"] = json.dumps(data["features"])
    plan = Plan(**data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_to_out(plan)


@router.patch("/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise NotFound(message="Plan not found")
    data = payload.model_dump(exclude_unset=True)
    if "slug" in data and data["slug"] != plan.slug and db.query(Plan).filter_by(slug=data["slug"]).first():
        raise Conflict(message="Plan slug already exists", code="slug_exists")
    if "features" in data and isinstance(data["features"], list):
        import json
        data["features"] = json.dumps(data["features"])
    for key, value in data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return _plan_to_out(plan)


@router.delete("/{plan_id}", status_code=204)
def delete_plan(
    plan_id: int,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise NotFound(message="Plan not found")
    db.delete(plan)
    db.commit()
    return None
