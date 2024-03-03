import jwt
from test_fixtures import *


def test_token_verification(settings):
    bkey = base64.standard_b64decode(settings.FERNET_KEY)
    # test_token generated using https://jwt.io/ and settings.FERNET_KEY as HS256 key
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.cDt029smKXRpY74tLSdr46yoslFcj4LSOnyAwWROUiU"
    jwt_payload: dict = jwt.decode(
        jwt=test_token,
        key=bkey,
        algorithms=["HS256"],
        verify=True,
    )
    assert "sub" in jwt_payload
