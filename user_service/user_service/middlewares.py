import datetime
import json

import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidAudienceError
from aiohttp import web

from user_service.services.serializers import InvalidParameterException
from user_service.services.auth import check_public_resources


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except InvalidParameterException as exc:
        raise web.HTTPUnprocessableEntity(
            body=json.dumps({"error": str(exc)}), content_type="application/json"
        )


@web.middleware
async def auth_middleware(request, handler):
    if check_public_resources(request.path, request.method):
        return await handler(request)

    token = request.headers["Authorization"]

    if not token:
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Access denied for requested resource"}),
            content_type="application/json",
        )

    try:
        data = jwt.decode(token, key=request.app["config"]["SECRET_KEY"])
    except ExpiredSignatureError:
        raise web.HTTPUnauthorized(
            body=json.dumps({"error": "Token expired"}), content_type="application/json"
        )
    except (InvalidAudienceError, DecodeError):
        raise web.HTTPUnauthorized(
            body=json.dumps({"error": "Invalid token"}), content_type="application/json"
        )

    if (
        datetime.datetime.strptime(data["exp_date"], "%Y-%m-%d %H:%M:%S.%f")
        < datetime.datetime.now()
    ):
        raise web.HTTPForbidden(
            body=json.dumps({"error": "Access token has expired"}),
            content_type="application/json",
        )
    request.auth_user = {"user_id": data["user_id"]}

    return await handler(request)
