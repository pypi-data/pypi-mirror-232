from random import randint

import pytest
from pydantic import BaseModel

from pycommon.auth.jwt.jwt_bearer import JWTBearer


class TokenData(BaseModel):
    user_id: int


@pytest.fixture(name="auth")
def get_authenticator():
    return JWTBearer(jwt_token_secret="supersecret", token_data=TokenData)


@pytest.fixture(name="mock_payload")
def get_mock_payload():
    return {"user_id": randint(0, 1000)}


class TestJWTBearer:
    def test_encode_and_then_decode_token(self, auth, mock_payload):
        assert (
            auth.decode_jwt_token(auth.encode_jwt_token(mock_payload)).data.user_id
            == mock_payload["user_id"]
        )
        assert isinstance(
            auth.decode_jwt_token(auth.encode_jwt_token(mock_payload)).data,
            TokenData,
        )
