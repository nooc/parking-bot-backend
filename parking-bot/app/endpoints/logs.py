from typing import Any, List

from fastapi import APIRouter, Body, Depends, Path, Query, status

import app.util.http_error as err
from app.dependencies import get_db, get_log_manager, get_superuser, get_user
from app.models.history import HistoryItem, HistoryItemCreate
from app.models.user import User
from app.services.datastore import Database
from app.services.history_manager import ParkingHistoryManager

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
def log_operation(
    current_user: User = Depends(get_user),
    log_mgr: ParkingHistoryManager = Depends(get_log_manager),
    info: HistoryItemCreate = Body(title="Parking operation info."),
) -> HistoryItem:
    return log_mgr.log(current_user, **info.model_dump())


@router.get("", status_code=status.HTTP_200_OK)
def list_parking_operations(
    log_mgr: ParkingHistoryManager = Depends(get_log_manager),
    current_user: User = Depends(get_user),
    from_time: int = Query(0, title="From timestamp."),
    offset: int = Query(0, title="List offset.", ge=0),
    limit: int = Query(20, title="Max Number of results.", gt=0),
) -> List[HistoryItem]:
    return log_mgr.list(current_user, from_time=from_time, offset=offset, limit=limit)
