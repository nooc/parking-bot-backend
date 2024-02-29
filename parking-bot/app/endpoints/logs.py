from typing import Any, List

from fastapi import APIRouter, Depends, Path, Query, status

import app.util.http_error as err
from app.dependencies import get_db, get_superuser, get_user
from app.models.logs import ParkingOperationLog
from app.models.user import User
from app.services.datastore import Database

router = APIRouter()


@router.get(
    "/list", response_model=List[ParkingOperationLog], status_code=status.HTTP_200_OK
)
def list_parking_operations(
    db: Database = Depends(get_db),
    current_user: User = Depends(get_user),
    from_time: int = Query(0, title="From timestamp."),
    offset: int = Query(0, title="List offset.", ge=0),
    limit: int = Query(20, title="Max Number of results.", gt=0),
) -> Any:
    return db.get_objects_by_query(
        ParkingOperationLog,
        filters=[("UserId", "=", current_user.Id), ("Timestamp", ">=", from_time)],
        offset=offset,
        limit=limit,
    )


@router.get(
    "/list/{id}",
    response_model=List[ParkingOperationLog],
    status_code=status.HTTP_200_OK,
)
def list_parking_operations(
    db: Database = Depends(get_db),
    current_user: User = Depends(get_superuser),
    id: str = Path(title="User id"),
    from_time: int = Query(0, title="From timestamp."),
    offset: int = Query(0, title="List offset.", ge=0),
    limit: int = Query(20, title="Max Number of results.", gt=0),
) -> Any:
    return db.get_objects_by_query(
        ParkingOperationLog,
        filters=[("UserId", "=", id), ("Timestamp", ">=", from_time)],
        offset=offset,
        limit=limit,
    )


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_parking_operations(
    db: Database = Depends(get_db),
    id: int = Path(title="ParkingOperationLog id."),
    _: User = Depends(get_superuser),
) -> Any:
    count = db.delete_objects(id)
    if count == 0:
        err.not_found("Trying to delete non existent ParkingOperationLog")
