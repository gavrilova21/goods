from functools import wraps
import re
import json

from aiohttp import web
from webargs.aiohttpparser import parser
from marshmallow import fields, Schema


def id_validator(request_id, model_name):
    valid_id = re.match("^[0-9]+$", request_id)
    if valid_id is None:
        raise web.HTTPNotFound(
            body=json.dumps(
                {"error": f"{model_name.capitalize()} with id={request_id} not found"}
            ),
            content_type="application/json",
        )

    return int(valid_id.string)


def serialize_body(schema_name, custom_exc=None):
    if schema_name not in schemas:
        raise SchemaNotFound(schema_name)

    def _serialize_body(handler):
        @wraps(handler)
        async def _wrapper(arg):
            try:
                schema = schemas[schema_name]

                if isinstance(arg, web.Request):

                    body = await parser.parse(schema(), arg)
                else:
                    body = await parser.parse(schema(), arg.request)

            except web.HTTPBadRequest as exc:
                if custom_exc:
                    raise custom_exc
                else:
                    raise exc
            response = await handler(arg, body)

            return response

        return _wrapper

    return _serialize_body


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    login = fields.String(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)

    class Meta:
        strict = True


class AuthSchema(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)

    class Meta:
        strict = True


class PatchUserSchema(Schema):
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)

    class Meta:
        strict = True


class SchemaNotFound(Exception):
    pass


class InvalidParameterException(Exception):
    pass


schemas = {
    "user_schema": UserSchema,
    "login_schema": AuthSchema,
    "patch_user_schema": PatchUserSchema,
}
