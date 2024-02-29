from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

import app.endpoints.media_types as mtype
import app.util.http_error as err
from app.dependencies import get_superuser, get_user_manager
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_manager import UserManager

router = APIRouter()


@router.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
def list_users(
    um: UserManager = Depends(get_user_manager),
    offset: int = Query(0, title="List offset."),
    limit: int = Query(50, title="Max Number of results."),
    current_user: User = Depends(get_superuser),
) -> Any:
    return um.list_users(offset=offset, limit=limit)


@router.get("/user/{id}", response_model=User)
def get_user(
    um: UserManager = Depends(get_user_manager),
    id: str = Path(title="User id."),
    current_user: User = Depends(get_superuser),
) -> Any:
    return um.get_user(id)


@router.post("/user", response_model=User)
def create_user(
    user_data: UserCreate = Body(
        title="User data", media_type=mtype.MEDIA_TYPE_CREATE_USER
    ),
    current_user: User = Depends(get_superuser),
) -> Any:
    if not user_data.Id:
        err.bad_request("No user id")
    # TODO Needs valid token to create new user and should except if user exists.
    raise NotImplementedError()


@router.put("/user/{id}", response_model=User, status_code=status.HTTP_200_OK)
def update_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
    user_data: UserUpdate = Body(
        title="User data", media_type=mtype.MEDIA_TYPE_UPDATE_USER
    ),
) -> Any:
    return um.update_user(user=current_user, user_data=update_user)


@router.delete("/user/{id}", status_code=status.HTTP_200_OK)
def delete_user(
    um: UserManager = Depends(get_user_manager),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
) -> Any:
    um.delete_user(current_user)
