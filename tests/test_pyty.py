from unittest import TestCase

from slotomania.pyty import Array, Shape, String, parse_type


class PytyTestCase(TestCase):
    def test_pyty(self) -> None:
        actual = Shape.load_from_dict(
            "MyShape",
            {
                "name": {"__type__": "String"},
                "aliases": {"__type__": "Array<string>"},
                # "listOfLists": {"__type__": "Array", "__type_args__": ["Array"]},
            },
        ).to_dict()
        expected = Shape(
            identifier="MyShape", fields={"name": String(), "aliases": Array("String")}
        ).to_dict()

        assert actual == expected, actual

    def test_parse_type(self):
        assert parse_type("Array<String>").to_dict() == {"__type__": "Array<String>"}
        assert parse_type("Array<Array<String>>").to_dict() == {
            "__type__": "Array<Array<String>>"
        }
