"""
primitives: STRING, INTEGER, BOOLEAN, DECIMAL

NESTED: LIST

Child {
  __identifier__: "Child"


}
Thing {
  __identifier__: "Thing"
  name: {
    __type__: "string"
    optional: false
  }
  children: {
    __type__: Array
    __type_args__: Child
  }
}

"""
import re
from typing import Type


class FieldType:
    def __init__(self, *__type_args__) -> None:
        self.__type_args__ = list(__type_args__)

    def to_dict(self) -> dict:
        raise NotImplementedError()


class Primitive(FieldType):
    def to_dict(self) -> dict:
        return {"__type__": self.__class__.__name__}


class Composite(FieldType):
    def to_dict(self) -> dict:
        raise NotImplementedError()


class String(Primitive):
    pass


class Integer(Primitive):
    pass


class Boolean(Primitive):
    pass


class Decimal(Primitive):
    pass


class Array(Composite):
    def __init__(self, element_type_string: str) -> None:
        super().__init__(element_type_string)
        self.element_type_string = element_type_string

    def to_dict(self) -> dict:
        return {"__type__": f"{self.__class__.__name__}<{self.element_type_string}>"}


def get_type_class_by_name(type_name: str) -> Type[FieldType]:
    lookup = {k.__name__: k for k in [String, Integer, Boolean, Decimal, Array]}
    return lookup[type_name]


def parse_type(field_type_string: str) -> FieldType:
    match = re.match(r"(\w+)(<.+>)?", field_type_string)
    if not match:
        raise Exception(f"Invalid type: {field_type_string}")
    type_name, type_args = match.groups()
    return get_type_class_by_name(type_name)(type_args[1:-1] if type_args else [])


class Shape:
    def __init__(self, identifier: str, fields: dict) -> None:
        self.identifier = identifier
        self.fields = fields

    @classmethod
    def load_from_dict(cls, identifier: str, fields_dict: dict) -> "Shape":
        defined_shapes = {}
        fields = {}
        for field_name, field in fields_dict.items():
            # Either a primitive or a defined shape
            field_type_string = field["__type__"]
            fields[field_name] = parse_type(field_type_string)
            # type_args = field.get("__type_args__", [])
            # assert isinstance(type_args, list)
            # field_type = (
            #     get_type_class_by_name(field_type_string)
            #     or defined_shapes[field_type_string]
            # )
            # fields[field_name] = field_type(*type_args)

        return Shape(identifier=identifier, fields=fields)

    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "fields": {name: field.to_dict() for name, field in self.fields.items()},
        }
