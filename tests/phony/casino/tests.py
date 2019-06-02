import json
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pytypegen.exceptions import MissingField, NotAuthenticated


class LoginTestCase(TestCase):
    def POST(self, url: str, data: dict) -> Any:
        return self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

    def test_missing_username(self) -> None:
        url = reverse("api", args=["LoginApp"])
        assert self.client.get(url).data == {}
        with self.assertRaises(MissingField):
            self.POST(url, data={})

    def test_login_success(self) -> None:
        url = reverse("api", args=["LoginApp"])
        response = self.POST(url, data={"username": "abc", "password": "abc"})
        assert response.status_code == 200
        assert response.data["errors"] == "bad credential"


class ViewTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.jwt_auth_token = ""
        self.user = get_user_model().objects.create_user(
            username="tester", password="tester"
        )
        res = self.POST(
            reverse("api", kwargs={"endpoint": "LoginApp"}),
            data={"username": "tester", "password": "tester"},
        )
        assert res.status_code == 200
        self.jwt_auth_token = next(
            op for op in res.data["operations"] if op["entity_type"] == "jwt_auth_token"
        )["target_value"]

    def POST(self, url: str, data: dict) -> Any:
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"JWT {self.jwt_auth_token}",
        )

    def test_not_authenticated(self) -> None:
        self.jwt_auth_token = "badtoken"
        url = reverse("api", args=["ReturnInstruction"])
        with self.assertRaises(NotAuthenticated):
            self.POST(url, {})

        # emtpy token
        self.jwt_auth_token = ""
        with self.assertRaises(NotAuthenticated):
            self.POST(url, {})

        self.jwt_auth_token = ""
        with self.assertRaises(NotAuthenticated):
            self.client.post(
                url,
                data=json.dumps({}),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"JWT",
            )

    def test_return_http_response(self) -> None:
        url = reverse("api", args=["ReturnHttpResponse"])
        response = self.POST(url, {})
        assert response.content == b"hello"

    def test_return_instruction(self) -> None:
        url = reverse("api", args=["ReturnInstruction"])
        response = self.POST(url, {})
        assert response.data["operations"][0] == {
            "verb": "MERGE_APPEND",
            "entity_type": "CARD",
            "target_value": [
                {"rank": 10, "width": "1.111", "played_at": "2000-01-01T00:00:00"}
            ],
        }
