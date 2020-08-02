import datetime
import json
import os

from aiohttp import web
from aiohttp_swagger import swagger_path
from aiohttp_session import get_session, new_session
import jwt
from sqlalchemy import select, exists, insert

from user_service.models import Users, Tokens
from user_service.services.serializers import serialize_body
from user_service.services.auth import create_tokens

auth_routes = web.RouteTableDef()


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/login.yaml"
    )
)
@auth_routes.post("/api/auth/login")
@serialize_body("login_schema", custom_exc=web.HTTPUnauthorized)
async def login(request: web.Request, body) -> web.Response:
    user_table = Users.__table__

    with request.app["pg"].connect() as conn:
        user = conn.execute(
            user_table.select().where(user_table.c.login == body["login"])
        ).fetchone()
    if not user:
        raise web.HTTPUnauthorized(
            body=json.dumps({"error": "Invalid username / password combination"}),
            content_type="application/json",
        )

    if body["password"] == user["password"]:
        session = await new_session(request)
        access_token, refresh_token, exp_in = await create_tokens(
            user,
            request.app["config"]["ACCESS_LIFETIME"],
            request.app["config"]["REFRESH_LIFETIME"],
            secret_key=request.app["config"]["SECRET_KEY"],
        )
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token
        session["exp_in"] = exp_in

        with request.app["pg"].connect() as conn:
            conn.execute(
                insert(Tokens).values(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "exp_date": exp_in,
                    }
                )
            )

        return web.Response(
            content_type="application/json",
            body=json.dumps(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "exp_in": exp_in,
                }
            ),
            status=200,
        )

    raise web.HTTPUnauthorized(
        body=json.dumps({"error": "Invalid username / password combination"}),
        content_type="application/json",
    )


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/refresh.yaml"
    )
)
@auth_routes.get("/api/auth/refresh")
async def refresh(request: web.Request) -> web.Response:
    token_table = Tokens.__table__
    user_table = Users.__table__
    token = request.headers["Authorization"]
    session = await get_session(request)
    try:
        refresh_token = session["refresh_token"]
        refresh_expired = session["exp_in"]
    except KeyError:
        with request.app["pg"].connect() as conn:
            refresh_exists = conn.execute(
                select([exists().where(token_table.c.refresh_token == token)])
            ).fetchone()[0]
        if not refresh_exists:
            raise web.HTTPForbidden(
                body=json.dumps({"error": "Invalid refresh token"}),
                content_type="application/json",
            )

        with request.app["pg"].connect() as conn:
            row = conn.execute(
                token_table.select().where(token_table.c.refresh_token == token)
            ).fetchone()
            refresh_token = row[2]
            refresh_expired = row[3]

    if refresh_token != token:
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Invalid refresh token"}),
            content_type="application/json",
        )

    if (
        datetime.datetime.strptime(refresh_expired, "%Y-%m-%d %H:%M:%S.%f")
        < datetime.datetime.now()
    ):
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Access token has expired"}),
            content_type="application/json",
        )

    user_loginned = jwt.decode(token, key=request.app["config"]["SECRET_KEY"])

    with request.app["pg"].connect() as conn:
        user_exists = conn.execute(
            select([exists().where(user_table.c.user_id == user_loginned["user_id"])])
        ).fetchone()[0]

    if not user_exists:
        raise web.HTTPNotFound(
            body=json.dumps({"error": "User not found"}),
            content_type="application/json",
        )

    with request.app["pg"].connect() as conn:
        user = conn.execute(
            user_table.select().where(user_table.c.user_id == user_loginned["user_id"])
        ).fetchone()

    access_token, refresh_token, exp_in = await create_tokens(
        user,
        request.app["config"]["ACCESS_LIFETIME"],
        request.app["config"]["REFRESH_LIFETIME"],
        secret_key=request.app["config"]["SECRET_KEY"],
    )
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    session["exp_in"] = exp_in
    with request.app["pg"].connect() as conn:
        conn.execute(
            insert(Tokens).values(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "exp_date": exp_in,
                }
            )
        )
    return web.Response(
        content_type="application/json",
        body=json.dumps(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "exp_in": exp_in,
            }
        ),
        status=200,
    )


@swagger_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../swagger/logout.yaml"
    )
)
@auth_routes.get("/api/auth/logout")
async def logout(request: web.Request) -> web.Response:
    response = web.json_response({"status": "ok"})
    session = await get_session(request)
    session.invalidate()
    del session
    return response
