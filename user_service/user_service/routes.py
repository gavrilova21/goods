from .views import create_user, auth_routes, get_all_users, get_user, patch_user


def setup_routes(app):
    # Auth
    app.router.add_routes(auth_routes)
    # User
    app.router.add_post("/api/users", create_user)
    app.router.add_get("/api/users", get_all_users)
    app.router.add_get("/api/users/{user_id}", get_user)
    app.router.add_patch("/api/users/{user_id}", patch_user)
