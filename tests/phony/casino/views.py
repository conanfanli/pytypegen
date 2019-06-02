from dataclasses import dataclass
import datetime
from decimal import Decimal
from enum import Enum

from django.http import HttpResponse

from pytypegen.contrib import contracts
from pytypegen.contrib.jwt_auth import AuthenticateUser
from pytypegen.core import Contract, Instruction
from pytypegen.core import InstructorView as BaseView
from pytypegen.core import Operation, RequestResolver


@dataclass
class Card(Contract):
    rank: int
    width: Decimal
    played_at: datetime.datetime


class PhonyEntityTypes(Enum):
    CARD = 1


class ReturnHttpResponse(RequestResolver):
    use_jwt_authentication = False
    data: contracts.EmptyBodySchema

    def resolve(self) -> HttpResponse:
        return HttpResponse("hello")


class ReturnInstruction(RequestResolver):
    data: contracts.EmptyBodySchema

    def resolve(self) -> Instruction:
        return Instruction(
            [
                Operation.MERGE_APPEND(
                    PhonyEntityTypes.CARD,
                    target_value=[
                        Card(
                            rank=10,
                            width=Decimal("1.111"),
                            played_at=datetime.datetime(2000, 1, 1, 0, 0, 0),
                        )
                    ],
                )
            ]
        )


class InstructorView(BaseView):
    routes = {
        "LoginApp": AuthenticateUser,
        "ReturnHttpResponse": ReturnHttpResponse,
        "ReturnInstruction": ReturnInstruction,
    }
