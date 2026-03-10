from fastapi import APIRouter
from app.services.template_service import TemplateService

router = APIRouter()
service = TemplateService()


@router.get("")
async def list_templates():
    return service.list_templates()


@router.get("/{template_id}")
async def get_template(template_id: str):
    return service.get_template(template_id)
