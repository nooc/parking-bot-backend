from test_fixtures import *


def test_get_free_parking(parking_data):
    id = "1480 2007-00933"

    parking = parking_data.get_free_parking(id)
    assert parking.Id == id


def test_get_nearby_free_parking(parking_data):
    id = "1480 2007-00933"

    parkings = parking_data.get_nearby_free_parking(
        57.70097712135818, 11.993808746337892, 500
    )
    assert [p for p in parkings if p.Id == id] != []


def test_get_toll_parking(parking_data):
    id = "1480 2007-03282"

    parking = parking_data.get_toll_parking(id)
    assert parking.Id == id


def test_get_nearby_toll_parkings_for_pos_and_check_known_exists_with_success(
    parking_data,
):
    id = "1480 2007-03282"
    parkings = parking_data.get_nearby_toll_parking(
        57.70097712135818, 11.993808746337892, 500
    )
    assert [p for p in parkings if p.Id == id] != []
