import jwt
from test_fixtures import *


def test_token_verification(settings):
    # test_token generated using https://jwt.io/ and settings.FERNET_KEY as HS256 key
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.ejg7Byw5Fy7CQsdnf6Bm9ZaN5OfM0yrjy3QZXVhXRC0"
    jwt_payload: dict = jwt.decode(
        jwt=test_token,
        key=settings.TEST_HS256_KEY,
        algorithms=["HS256"],
        verify=True,
    )
    assert "sub" in jwt_payload
