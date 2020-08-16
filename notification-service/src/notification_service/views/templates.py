import json

from aio_pika import connect, Message
from fastapi import APIRouter
from fastapi.responses import JSONResponse
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


@router.post("/send")
async def send_message(template, text, recipient, subject=""):
    try:
        message = template.format(text)
    except ValueError:
        return JSONResponse(content="Wrong template format")
    data = {"text": message, "recipient": recipient, "sunjiect": subject}
    connection = await connect("amqp://guest:guest@rabbit/")

    channel = await connection.channel()
    await channel.default_exchange.publish(
        Message(json.dumps(data).encode("utf-8")), routing_key="mail"
    )

    await connection.close()
    return JSONResponse(content="Success")


def init_app(app):
    app.include_router(router)
