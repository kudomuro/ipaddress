import os
import sys
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(sys.path[0], 'src'))

from fastapi import FastAPI, Depends

from src.auth.base_config import auth_backend, fastapi_users, current_user
from src.auth.schemas import UserRead, UserCreate

from ipaddresses.router import router as router_ipaddress

app = FastAPI(
    title="Addresses"
)

origins = [
    'http://192.168.11.40:3000',
    'http://192.168.11.40:5137',
    'http://192.168.11.40',
    'http://localhost',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT", "SET"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin", "Authorization"],
    # allow_methods=["*"],
    # allow_headers=["*"],    
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

@app.get(
    "/users/whoami", response_model=UserRead, dependencies=[Depends(current_user)]
)
async def read_users_me(current_user: UserRead = Depends(current_user)):
    return current_user

@app.get("/protected-route")
def protected_route(user = Depends(current_user)):
    return f"Hello, {user.username}, {user.email}"

app.include_router(router_ipaddress)