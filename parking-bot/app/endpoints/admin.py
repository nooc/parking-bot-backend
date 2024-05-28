from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

import app.util.http_error as err
from app.dependencies import get_superuser, get_user_manager
from app.endpoints.media_types import MEDIA_TYPE_JSON
from app.models.user import User, UserUpdate
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
    identifier: str = Query(title="Identifier"),
    current_user: User = Depends(get_superuser),
) -> User:
    if not identifier:
        err.bad_request("No user id")
    raise NotImplementedError()


@router.put("/user/{id}", status_code=status.HTTP_200_OK)
def update_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
    user_data: UserUpdate = Body(title="User data", media_type=MEDIA_TYPE_JSON),
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
