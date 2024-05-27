from typing import Optional
from fastapi_users import schemas
import pydantic_core
from pydantic import ConfigDict
from datetime import datetime


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str    
    role_id: int    
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    registered_at: datetime

    if pydantic_core:  # pragma: no cover
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:  # pragma: no cover

        class Config:
            orm_mode = True

class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

