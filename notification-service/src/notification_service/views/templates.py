from fastapi import APIRouter
from pydantic import BaseModel

from ..models.templates import Template

router = APIRouter()


@router.get("/templates/{uid}")
async def get_template(uid: int):
    template = await Template.get_or_404(uid)
    return template.to_dict()


class TemplateModel(BaseModel):
    name: str


@router.post("/templates")
async def add_template(user: TemplateModel):
    rv = await Template.create(nickname=user.name)
    return rv.to_dict()


@router.delete("/templates/{uid}")
async def delete_template(uid: int):
    template = await Template.get_or_404(uid)
    await template.delete()
    return dict(id=uid)


def init_app(app):
    app.include_router(router)
