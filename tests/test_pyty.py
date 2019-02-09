from unittest import TestCase

from slotomania.pyty import Array, Shape, String


class PytyTestCase(TestCase):
    def test_pyty(self) -> None:
        assert (
            Shape.load_from_dict(
                "MyShape",
                {
                    "name": {"__type__": "String"},
                    "aliases": {"__type__": "Array", "__type_args__": ["String"]},
                },
            ).to_dict()
            == Shape(
                identifier="MyShape",
                fields={"name": String(), "aliases": Array("String")},
            ).to_dict()
        )
