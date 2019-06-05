from dataclasses import MISSING, Field, asdict, dataclass, is_dataclass
import datetime
import decimal
from decimal import Decimal
from enum import Enum, auto
import json
from typing import Any, Callable, ClassVar, Dict, List, Type, TypeVar, Union
from typing import ForwardRef  # type: ignore

from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse as DjangoJsonResponse
from django.views import View

from pytypegen.exceptions import BadResolver, MissingField, UnknowFieldType

T = TypeVar("T", bound="Contract")


class Undefined:
    pass


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, *args, **kwargs) -> None:
        self.data = data
        super().__init__(data, *args, **kwargs)


class InstructorView(View):
    permission_classes: list = []
    routes: Dict[str, Type["RequestResolver"]]

    def get(self, request: Any, endpoint: str = None) -> JsonResponse:
        return JsonResponse({})

    def post(self, request: Any, endpoint: str, *args, **kwargs) -> JsonResponse:
        """If mustate_state returns HttpResponse, return it."""
        with transaction.atomic():
            request.data = json.loads(request.body)
            resolver = self.routes[endpoint](request=request, data=request.data)

            resolver.authenticate()
            response = resolver.resolve()

            if isinstance(response, HttpResponse):
                return response
            elif isinstance(response, dict):
                return JsonResponse(response)
            elif hasattr(response, "serialize"):
                return JsonResponse(response.serialize())
            else:
                raise AssertionError("Unknow type: {}".format(type(response)))


class Verbs(Enum):
    DELETE = auto()
    MERGE_APPEND = auto()
    MERGE_PREPEND = auto()
    OVERWRITE = auto()


def is_subclass(obj, cls):
    try:
        return issubclass(obj, cls)
    except TypeError:
        return None


@dataclass
class Contract:
    def asdict(self) -> dict:
        return asdict(self)

    @classmethod
    def get_fields(cls: Type["Contract"]) -> Dict[str, Field]:
        return getattr(cls, "__dataclass_fields__")

    @classmethod
    def to_typescript_interface(cls: Type["Contract"]) -> str:
        interface_body = "\n".join(
            [
                f"  {field.name}: {field_to_typescript(field)}"
                if is_field_required(field)
                else f"  {field.name}?: {field_to_typescript(field)}"
                for name, field in cls.get_fields().items()
            ]
        )
        return "export interface {} {{\n{}\n}}".format(cls.__name__, interface_body)

    @classmethod
    def load_from_dict(cls: Type[T], data: dict) -> T:
        kwargs = {}
        annotation = cls.__init__.__annotations__
        PRIMITIVES = list(TYPE_MAP.keys())

        def convert_value(value, value_type):
            if value_type in PRIMITIVES:
                return value
            elif is_subclass(value_type, Enum):
                return value_type[value if isinstance(value, str) else value.name]
            elif is_dataclass(value_type):
                return value_type.load_from_dict(value)
            elif getattr(value_type, "__origin__", None) == Union:
                args = getattr(value_type, "__args__")
                # TODO: natively chose first type in Union
                return convert_value(value, args[0])
            elif value_type.__origin__ == list:
                nested_type = value_type.__args__[0]
                return [convert_value(item, nested_type) for item in value]
            else:
                raise Exception(f"not sure what to do with {value_type}: {value}")

        for key in data:
            if key in cls.get_fields():
                arg_type = annotation[key]
                kwargs[key] = convert_value(data[key], arg_type)

        for name, field in cls.get_fields().items():
            if is_field_required(field) and name not in data:
                raise MissingField(field)

        return cls(**kwargs)  # type: ignore


@dataclass
class Operation(Contract):
    verb: Verbs
    entity_type: Enum
    target_value: Any

    @classmethod
    def MERGE_APPEND(cls, entity_type: Enum, target_value) -> "Operation":
        assert isinstance(target_value, list), f"'{target_value}' is not a list"
        return Operation(Verbs.MERGE_APPEND, entity_type, target_value)

    @classmethod
    def MERGE_PREPEND(cls, entity_type: Enum, target_value) -> "Operation":
        assert isinstance(target_value, list), f"'{target_value}' is not a list"
        return Operation(Verbs.MERGE_PREPEND, entity_type, target_value)

    @classmethod
    def DELETE(cls, entity_type: Enum, target_value) -> "Operation":
        return Operation(Verbs.DELETE, entity_type, target_value)

    @classmethod
    def OVERWRITE(cls, entity_type: Enum, target_value) -> "Operation":
        return Operation(Verbs.OVERWRITE, entity_type, target_value)


class InstructionEncoder(json.JSONEncoder):
    def default(self, obj) -> Any:
        if isinstance(obj, Enum):
            return obj.name
        elif is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, "isoformat"):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


@dataclass
class Instruction(Contract):
    operations: List[Operation]
    errors: Any = None
    redirect: str = ""

    def serialize(self) -> dict:
        return json.loads(json.dumps(self, cls=InstructionEncoder))


class RequestResolver:
    # data: MyDataType
    resolve: Callable
    pre_action: ClassVar[str] = ""
    callback: ClassVar[str] = ""
    use_jwt_authentication: ClassVar[bool] = True

    def __init__(self, request, data: dict) -> None:
        self.request = request
        self._data = data
        self.clean_request_data()

    def clean_request_data(self) -> None:
        contract_class = self.__class__.__annotations__["data"]
        if issubclass(contract_class, Contract):
            self.data = contract_class.load_from_dict(self._data)
        else:
            raise Exception(f"Unknown type for `data` f{contract_class}")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "resolve"):
            assert cls.__annotations__.get(
                "data"
            ), f"{cls} cannot define 'resovle' without annotating 'data'"
            if not cls.resolve.__annotations__:
                raise BadResolver(f"{cls} must annotate resolve method if defined")

    def authenticate(self) -> None:
        if not self.use_jwt_authentication:
            return

        from .contrib.jwt_auth import authenticate_request

        authenticate_request(self.request)


class EntityTypes(Enum):
    jwt_auth_token = auto()


def is_field_required(field: Field) -> bool:
    return field.default is MISSING


TYPE_MAP = {
    str: "string",
    bool: "boolean",
    int: "number",
    Decimal: "string",
    float: "number",
    datetime.datetime: "string",
    dict: "{}",
    Any: "any",
    list: "Array<any>",
}


def python_type_to_typescript(python_type: type) -> str:
    if python_type in TYPE_MAP:
        return TYPE_MAP[python_type]

    if python_type is Undefined:
        return "undefined"

    if is_dataclass(python_type):
        return python_type.__name__

    if getattr(python_type, "__name__", None) == "NoneType":
        return "null"

    if getattr(python_type, "__origin__", None) in [list, List]:
        args = getattr(python_type, "__args__")
        return "Array<{}>".format(python_type_to_typescript(args[0]))

    if getattr(python_type, "__origin__", None) == Union:
        args = getattr(python_type, "__args__")
        return "|".join(python_type_to_typescript(arg) for arg in args)

    if isinstance(python_type, ForwardRef):
        return python_type.__forward_arg__

    if isinstance(python_type, type) and issubclass(python_type, Enum):
        return python_type.__name__

    raise UnknowFieldType(f"Unknow type {python_type}")


def field_to_typescript(field: Field) -> str:
    try:
        return python_type_to_typescript(field.type)
    except UnknowFieldType as e:
        raise UnknowFieldType(f"{field.name}: {e}")


@dataclass
class ReduxAction(Contract):
    name: str
    contract: Type[Contract]
    pre_action: str = ""
    callback: str = ""

    def to_typescript_function(self):
        return f"""export function {self.name}(requestBody: {self.contract.__name__}): any {{
        return (dispatch) => {{{self.pre_action}
            return dispatch(
                plugins.callEndpoint("{self.name}", requestBody, {self.callback})
            )
        }}
    }}"""  # NOQA


def contract_to_redux_action_creator(
    *, contract: Type[Contract], function_name: str, callback="", pre_action=""
) -> str:
    return f"""export function {function_name}(requestBody: {contract.__name__}): any {{
    return (dispatch) => {{{pre_action}
        return dispatch(
            plugins.callEndpoint("{function_name}", requestBody, {callback})
        )
    }}
}}"""


def enum_to_typescript(enum_class: Type[Enum]) -> str:
    body = ",\n".join(f"  {member.name} = '{member.name}'" for member in enum_class)
    return "export enum {} {{\n{}\n}}".format(enum_class.__name__, body)


def contracts_to_typescript(contracts: List[Union[Type[Contract], Type[Enum]]]) -> str:
    """
    Args:
        contracts: A list of Contract sub classes to be converted to typescript
    interfaces.
    """
    blocks = []
    for index, contract in enumerate(contracts):
        if issubclass(contract, Contract):
            blocks.append(contract.to_typescript_interface())
        else:
            assert issubclass(contract, Enum)
            blocks.append(enum_to_typescript(contract))

    return "\n\n".join(blocks)
