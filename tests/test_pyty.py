from unittest import TestCase

from slotomania.pyty import Shape


class PytyTestCase(TestCase):
    def test_pyty(self) -> None:
        assert Shape.load_from_dict("MyShape", {"name": {"__type__": "String"}}) == 1
