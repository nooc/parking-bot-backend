from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

import app.endpoints.media_types as mtype
import app.util.http_error as err
from app.dependencies import get_superuser, get_user_manager
from app.models.user import User, UserRegister, UserUpdate
from app.services.user_manager import UserManager

router = APIRouter()


@router.get("/users", status_code=status.HTTP_200_OK)
def list_users(
    um: UserManager = Depends(get_user_manager),
    offset: int = Query(0, title="List offset."),
    limit: int = Query(50, title="Max Number of results."),
    current_user: User = Depends(get_superuser),
) -> List[User]:
    return um.list_users(offset=offset, limit=limit)


@router.get("/user/{id}")
def get_user(
    um: UserManager = Depends(get_user_manager),
    id: str = Path(title="User id."),
    current_user: User = Depends(get_superuser),
) -> User:
    return um.get_user(id)


@router.post("/user")
def create_user(
    user_data: UserRegister = Body(
        title="User data", media_type=mtype.MEDIA_TYPE_REGISTER_USER
    ),
    current_user: User = Depends(get_superuser),
) -> User:
    if not user_data.Id:
        err.bad_request("No user id")
    # TODO Needs valid token to create new user and should except if user exists.
    raise NotImplementedError()


@router.put("/user/{id}", status_code=status.HTTP_200_OK)
def update_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
    user_data: UserUpdate = Body(
        title="User data", media_type=mtype.MEDIA_TYPE_UPDATE_USER
    ),
) -> User:
    user = um.get_user(id)
    return um.update_user(user, **user_data.model_dump(exclude_unset=True))


@router.delete("/user/{id}", status_code=status.HTTP_200_OK)
def delete_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
) -> Any:
    um.delete_user(current_user)
