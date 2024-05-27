from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy

from auth.manager import get_user_manager
from auth.models import User
from config import SECRET_AUTH

cookie_transport = CookieTransport(cookie_name="Authorization",cookie_max_age=10800, cookie_samesite="none", cookie_secure=True)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET_AUTH, 
        lifetime_seconds=10800, 
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)    

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()