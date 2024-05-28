import re
from datetime import UTC, datetime, timedelta

import jwt
from test_fixtures import TestSettings  # type: ignore

cfg = TestSettings()

tokens = {}
dt = datetime.now(UTC)

test_token = jwt.encode(
    payload={
        "sub": "0a0a0a0a0a0a0a01",
        "exp": dt + timedelta(days=3000),
        "iss": "parkingbot",
        "iat": dt,
    },
    key=cfg.HS256_KEY,
    algorithm="HS256",
)
test_token_init = jwt.encode(
    payload={
        "identifier": "0a0a0a0a0a0a0a0a",
        "exp": dt + timedelta(days=3000),
        "iss": "parkingbot",
        "iat": dt,
    },
    key=cfg.HS256_KEY,
    algorithm="HS256",
)
test_token_invalid = jwt.encode(
    payload={
        "identifier": "0a0a0a0a0a0a0a0a",
        "exp": dt - timedelta(days=1),
        "iss": "parkingbot",
        "iat": dt,
    },
    key=cfg.HS256_KEY,
    algorithm="HS256",
)
with open("env.test.yml", "r") as f:
    in_data = f.read()

out_data = re.sub("^TEST_TOKEN:.*$", f'TEST_TOKEN: "{test_token}"', in_data, flags=re.M)
out_data = re.sub(
    "^TEST_TOKEN_INIT:.*$",
    f'TEST_TOKEN_INIT: "{test_token_init}"',
    out_data,
    flags=re.M,
)
out_data = re.sub(
    "^TEST_TOKEN_INVALID:.*$",
    f'TEST_TOKEN_INVALID: "{test_token_invalid}"',
    out_data,
    flags=re.M,
)

with open("env.test.yml", "w") as f:
    f.write(out_data)
