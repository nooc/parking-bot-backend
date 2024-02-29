from fastapi import APIRouter

from .endpoints import admin, carpark, logs, user, vehicle

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(vehicle.router, prefix="/vehicle", tags=["vehicle"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(carpark.router, prefix="/carpark", tags=["carpark"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
