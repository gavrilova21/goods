import json
import os

from aiohttp import web
import sqlalchemy as sa
from aiohttp_swagger import swagger_path
from sqlalchemy import exists, select, literal_column

from user_service.models import row_to_dict, Users
from user_service.services.serializers import serialize_body, id_validator


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/create_user.yaml"
    )
)
@serialize_body("user_schema")
async def create_user(request: web.Request, body) -> web.Response:
    user_table = Users.__table__
    login = body["login"]
    with request.app["pg"].connect() as conn:
        exist = conn.execute(
            select([exists().where(user_table.c.login == login)])
        ).fetchone()[0]
    if exist:
        return web.HTTPConflict(
            body=json.dumps({"error": f'User with login "{login}" already exist'}),
            content_type="application/json",
        )
    with request.app["pg"].connect() as conn:
        data = conn.execute(
            sa.insert(Users).values(**body).returning(literal_column("*"))
        ).fetchone()
    body["user_id"] = data[0]
    del body["password"]

    return web.Response(
        status=201, content_type="application/json", body=json.dumps(body)
    )


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/get_all_users.yaml"
    )
)
async def get_all_users(request: web.Request) -> web.Response:
    user_table = Users.__table__
    with request.app["pg"].connect() as conn:
        users = conn.execute(user_table.select()).fetchall()

    result = [row_to_dict(user_table, user) for user in users]

    return web.Response(
        status=200, content_type="application/json", body=json.dumps(result)
    )


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/get_user.yaml"
    )
)
async def get_user(request: web.Request) -> web.Response:
    user_id = id_validator(request.match_info["user_id"], "user")
    user_table = Users.__table__

    if user_id != request.auth_user["user_id"]:
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Access denied for this user"}),
            content_type="application/json",
        )

    with request.app["pg"].connect() as conn:
        user_exists = conn.execute(
            select([exists().where(user_table.c.user_id == user_id)])
        ).fetchone()[0]

    if not user_exists:
        raise web.HTTPNotFound(
            body=json.dumps({"error": f"User with id={user_id} not found"}),
            content_type="application/json",
        )

    with request.app["pg"].connect() as conn:
        user = conn.execute(
            user_table.select().where(user_table.c.user_id == user_id)
        ).fetchone()

    return web.Response(
        status=200,
        content_type="application/json",
        body=json.dumps(row_to_dict(user_table, user)),
    )


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/patch_user.yaml"
    )
)
@serialize_body("patch_user_schema")
async def patch_user(request: web.Request, body) -> web.Response:
    user_id = id_validator(request.match_info["user_id"], "user")
    user_table = Users.__table__
    if user_id != request.auth_user["user_id"]:
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Access denied for this user"}),
            content_type="application/json",
        )

    with request.app["pg"].connect() as conn:
        user_exists = conn.execute(
            select([exists().where(user_table.c.user_id == user_id)])
        ).fetchone()[0]

    if not user_exists:
        raise web.HTTPNotFound(
            body=json.dumps({"error": f"User with id={user_id} not found"}),
            content_type="application/json",
        )

    if not body:
        return web.Response(
            status=200, content_type="application/json", body=json.dumps({})
        )
    params = []
    for param in body:
        params.append("{}='{}'".format(param, body[param]))

    with request.app["pg"].connect() as conn:
        user = conn.execute(
            user_table.update()
            .where(user_table.c.user_id == user_id)
            .values(**body)
            .returning(literal_column("*"))
        ).fetchone()

    result = row_to_dict(user_table, user)

    return web.Response(
        status=200, content_type="application/json", body=json.dumps(result)
    )
