from dataclasses import asdict, dataclass, is_dataclass
import datetime
from enum import Enum
from typing import List, Optional
from unittest import TestCase

from slotomania.contrib.contracts import AuthenticateUserRequest
from slotomania.core import (
    Contract,
    EntityTypes,
    Instruction,
    Operation,
    ReduxAction,
    contracts_to_typescript,
)


class Gender(Enum):
    male = 1
    female = 2


@dataclass
class Address(Contract):
    street: str


@dataclass
class Person(Contract):
    name: str
    gender: Gender
    birth_date: datetime.datetime
    addresses: Optional[List[Address]] = None


class DataclassConverterTestCase(TestCase):
    def test_dataclass_converter(self) -> None:
        assert is_dataclass(Person)
        man = Person(
            "Bond", Gender.male, datetime.datetime.utcnow(), [Address("easy street")]
        )
        woman = Person("Girl", Gender.female, datetime.datetime.utcnow())
        assert is_dataclass(man) and is_dataclass(woman)
        assert (
            contracts_to_typescript(
                dataclasses=[Gender, Person],
                redux_actions=[ReduxAction(name="CreatePerson", contract=Person)],
                import_plugins=False,
            )
            == """export enum Gender {
  male = 'male',
  female = 'female'
}

export interface Person {
  name: string
  gender: Gender
  birth_date: string
  addresses?: Array<Address>|null
}

export function CreatePerson(requestBody: Person): any {
        return (dispatch) => {
            return dispatch(
                plugins.callEndpoint("CreatePerson", requestBody, )
            )
        }
    }

export const SLOTO_ACTION_CREATORS = { CreatePerson }"""
        )

        assert man == man.load_from_dict(asdict(man))


class InstructorTestCase(TestCase):
    def test_instruction_serialize(self) -> None:
        instruction = Instruction(
            [
                Operation.OVERWRITE(
                    EntityTypes.jwt_auth_token,
                    target_value=[AuthenticateUserRequest("user", "pass")],
                )
            ]
        )
        assert instruction.serialize() == {
            "errors": None,
            "redirect": "",
            "operations": [
                {
                    "verb": "OVERWRITE",
                    "entity_type": "jwt_auth_token",
                    "target_value": [{"username": "user", "password": "pass"}],
                }
            ],
        }
