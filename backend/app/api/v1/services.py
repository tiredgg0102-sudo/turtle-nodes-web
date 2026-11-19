"""Customer service endpoints."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import AdminOnly, CustomerOrStaff, StaffOnly, csrf_protect
from app.config import settings
from app.database import get_db
from app.exceptions import Forbidden, NotFound
from app.logging import setup_logging
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceOut, ServicePowerAction

logger = setup_logging() if False else __import__("logging").getLogger("hosting.api.services")

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
):
    q = db.query(Service)
    if not current_user.is_staff:
        q = q.filter_by(user_id=current_user.id)
    return q.order_by(Service.created_at.desc()).all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, current_user=Depends(CustomerOrStaff), db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if not service:
        raise NotFound(message="Service not found")
    if not current_user.is_staff and service.user_id != current_user.id:
        raise Forbidden(message="Cannot view this service")
    return service


@router.post("/{service_id}/power", response_model=dict)
def service_power(
    service_id: int,
    payload: ServicePowerAction,
    current_user=Depends(CustomerOrStaff),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    service = db.get(Service, service_id)
    if not service:
        raise NotFound(message="Service not found")
    if not current_user.is_staff and service.user_id != current_user.id:
        raise Forbidden(message="Cannot control this service")
    if not service.pterodactyl_server_id:
        return {"success": False, "message": "No Pterodactyl server linked"}
    # Real action performed via Pterodactyl Client API after customer connects their key.
    return {
        "success": True,
        "message": f"{payload.action} requested for server {service.pterodactyl_server_id}",
        "server_id": service.pterodactyl_server_id,
    }
