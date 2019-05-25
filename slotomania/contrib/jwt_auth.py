import datetime
from typing import Any, ClassVar, Mapping
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
import jwt

from pytypegen.contrib.contracts import AuthenticateUserRequest
from pytypegen.core import EntityTypes, Instruction, Operation, RequestResolver
from pytypegen.exceptions import NotAuthenticated


def authenticate_request(request) -> None:
    header = request.META.get("HTTP_AUTHORIZATION")
    try:
        prefix, token = header.split(" ")
    except (ValueError, AttributeError) as e:
        raise NotAuthenticated(f"Invalid header causing {e}: {header}")

    if not token:
        raise NotAuthenticated()

    try:
        payload = jwt_decode_handler(token)
    except jwt.ExpiredSignature as e:
        raise NotAuthenticated(str(e))
    except jwt.DecodeError as e:
        raise NotAuthenticated(str(e))
    except jwt.InvalidTokenError as e:
        raise NotAuthenticated(str(e))

    user = authenticate_credentials(payload)
    request.user = user


def authenticate_credentials(payload) -> Any:
    username = payload.get("username")

    if not username:
        raise NotAuthenticated("Invalid payload")

    User = get_user_model()

    try:
        user = User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        raise NotAuthenticated("Invalid signature")

    if not user.is_active:
        raise NotAuthenticated("User account is disabled")

    return user


def jwt_decode_handler(token) -> Mapping[str, Any]:
    options = {"verify_exp": True}
    secret_key = settings.SECRET_KEY
    return jwt.decode(
        token,
        secret_key,
        True,
        options=options,
        leeway=0,
        audience=None,
        issuer=None,
        algorithms=["HS256"],
    )


def jwt_encode_handler(payload) -> str:
    key = settings.SECRET_KEY
    return jwt.encode(payload, key, "HS256").decode("utf-8")


def jwt_payload_handler(user) -> dict:
    username = user.username

    payload = {
        "user_id": user.pk,
        "username": username,
        "exp": datetime.datetime.utcnow()
        + getattr(settings, "JWT_EXPIRATION_DELTA", datetime.timedelta(seconds=300)),
    }
    if hasattr(user, "email"):
        payload["email"] = user.email
    if isinstance(user.pk, uuid.UUID):
        payload["user_id"] = str(user.pk)

    payload["username"] = username
    return payload


class AuthenticateUser(RequestResolver):
    """Login and InitApp."""

    data: AuthenticateUserRequest
    use_jwt_authentication: ClassVar[bool] = False

    def resolve(self) -> Instruction:
        username = self.data.username
        password = self.data.password
        user = authenticate(username=username, password=password)

        if user:
            login(self.request, user)

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Instruction([Operation.OVERWRITE(EntityTypes.jwt_auth_token, token)])

        return Instruction(operations=[], errors="bad credential")
