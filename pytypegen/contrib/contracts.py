from dataclasses import dataclass
from pytypegen.core import Contract


@dataclass
class AuthenticateUserRequest(Contract):
    username: str
    password: str


@dataclass
class EmptyBodySchema(Contract):
    pass
