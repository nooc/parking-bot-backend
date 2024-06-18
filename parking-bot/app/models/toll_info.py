from pydantic import BaseModel


class TollInfo(BaseModel):
    Id: str
    Name: str
    Owner: str
    ParkingSpaces: int
    PhoneParkingCode: str
    ParkingCost: str
    CurrentParkingCost: int
    Lat: float
    Long: float
    WKT: str
