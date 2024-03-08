import jwt
from test_fixtures import *


def test_token_verification(settings):
    # Test_token generated using https://jwt.io/ and settings.HS256_KEY
    jwt_payload: dict = jwt.decode(
        jwt=settings.TEST_TOKEN,
        key=settings.HS256_KEY,
        algorithms=["HS256"],
        verify=True,
    )
    assert "sub" in jwt_payload
