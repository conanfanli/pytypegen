from unittest import TestCase

from slotomania.pyty import Shape, String


class PytyTestCase(TestCase):
    def test_pyty(self) -> None:
        assert (
            Shape.load_from_dict("MyShape", {"name": {"__type__": "String"}}).to_dict()
            == Shape(identifier="MyShape", fields={"name": String()}).to_dict()
        )
