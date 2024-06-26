from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_log_manager, get_user
from app.models.history import HistoryItem
from app.models.user import User
from app.services.history_manager import HistoryManager

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_parking_operations(
    log_mgr: HistoryManager = Depends(get_log_manager),
    current_user: User = Depends(get_user),
    from_time: int = Query(0, title="From timestamp."),
    offset: int = Query(0, title="List offset.", ge=0),
    limit: int = Query(20, title="Max Number of results.", gt=0),
) -> List[HistoryItem]:
    return log_mgr.list(current_user, from_time=from_time, offset=offset, limit=limit)
