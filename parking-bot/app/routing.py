from fastapi import APIRouter

from .endpoints import admin, carpark, history, parking, user, vehicle

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(vehicle.router, prefix="/vehicle", tags=["vehicle"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(carpark.router, prefix="/carpark", tags=["carpark"])
api_router.include_router(parking.router, prefix="/parking", tags=["parking"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
