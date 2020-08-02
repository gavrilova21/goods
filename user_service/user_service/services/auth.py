from datetime import timedelta, datetime
import jwt


PUBLIC_RESOURCES = (
    ("/api/auth/login", "POST"),
    ("/api/auth/refresh", "GET"),
    ("/api/users/", "POST"),
    ("/api/doc", "GET"),
)


def fix(url):
    url_fix = url
    if not (url.endswith("/")):
        url_fix += "/"
    return url_fix


def check_public_resources(path: str, method: str) -> bool:
    for resource, allowed_methods in PUBLIC_RESOURCES:
        if (
            fix(resource) in fix(path)
            and fix(resource) == "/api/doc/"
            or fix(resource) == fix(path)
        ) and method in allowed_methods:
            return True
    return False


async def create_tokens(user, access_lifetime, refresh_lifetime, secret_key: str):
    refresh_exp = str(datetime.now() + timedelta(hours=access_lifetime))
    payload = {"user_id": user["user_id"], "exp_date": refresh_exp}
    access_token = jwt.encode(payload=payload, key=secret_key).decode("utf-8")
    payload = {
        "user_id": user["user_id"],
        "exp_date": str(datetime.now() + timedelta(hours=refresh_lifetime)),
    }
    refresh_token = jwt.encode(payload=payload, key=secret_key).decode("utf-8")

    return access_token, refresh_token, refresh_exp
