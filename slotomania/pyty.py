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
    __of__: Child
  }
}

"""
import typing


class Primitive:
    pass


class String(Primitive):
    pass


class Integer(Primitive):
    pass


class Boolean(Primitive):
    pass


class Decimal(Primitive):
    pass


class Array:
    pass


def get_primitive_type(type_name: str) -> typing.Type[Primitive]:
    lookup = {k.__name__: k for k in [String, Integer, Boolean, Decimal]}
    return lookup[type_name]


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
            field_type = (
                get_primitive_type(field_type_string)
                or defined_shapes[field_type_string]
            )
            fields[field_name] = field_type()

        return Shape(identifier=identifier, fields=fields)

    def to_dict(self) -> dict:
        return {"identifier": self.identifier, "fields": self.fields}
