"""Hosting category endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, csrf_protect
from app.database import get_db
from app.exceptions import Conflict, NotFound
from app.logging import setup_logging
from app.models.category import Category
from app.schemas.common import Message

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.categories")

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list)
def list_categories(db: Session = Depends(get_db), active_only: bool = False):
    q = db.query(Category)
    if active_only:
        q = q.filter_by(active=True)
    return [c.to_dict() for c in q.order_by(Category.sort_order.asc(), Category.name.asc()).all()]


@router.post("", status_code=201)
def create_category(
    payload: dict,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    name = payload.get("name")
    slug = payload.get("slug") or name.lower().replace(" ", "-")
    if db.query(Category).filter_by(slug=slug).first():
        raise Conflict(message="Category slug already exists", code="slug_exists")
    cat = Category(name=name, slug=slug, description=payload.get("description"), icon=payload.get("icon"), active=payload.get("active", True), sort_order=payload.get("sort_order", 0))
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat.to_dict()


@router.patch("/{category_id}")
def update_category(
    category_id: int,
    payload: dict,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    cat = db.get(Category, category_id)
    if not cat:
        raise NotFound(message="Category not found")
    for key in ("name", "slug", "description", "icon", "active", "sort_order"):
        if key in payload:
            setattr(cat, key, payload[key])
    db.commit()
    db.refresh(cat)
    return cat.to_dict()


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    current_user=Depends(AdminOnly),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    cat = db.get(Category, category_id)
    if not cat:
        raise NotFound(message="Category not found")
    db.delete(cat)
    db.commit()
    return None
