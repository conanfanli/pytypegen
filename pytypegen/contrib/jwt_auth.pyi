# Stubs for pytypegen.contrib.jwt_auth (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from pytypegen.contrib.contracts import AuthenticateUserRequest
from pytypegen.core import Instruction, RequestResolver
from typing import Any, ClassVar, Mapping

def authenticate_request(request: Any) -> None: ...
def authenticate_credentials(payload: Any) -> Any: ...
def jwt_decode_handler(token: Any) -> Mapping[str, Any]: ...
def jwt_encode_handler(payload: Any) -> str: ...
def jwt_payload_handler(user: Any) -> dict: ...

class AuthenticateUser(RequestResolver):
    data: AuthenticateUserRequest
    use_jwt_authentication: ClassVar[bool] = ...
    def resolve(self) -> Instruction: ...
