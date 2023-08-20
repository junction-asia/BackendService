import time
from datetime import datetime

import jwt
import orjson
from django.conf import settings
from ninja import NinjaAPI
from ninja.parser import Parser
from ninja.renderers import JSONRenderer
from ninja.security import HttpBearer

from cores.enums import InvalidJwtErrorEnum
from cores.exceptions import CustomException


class CustomJwtTokenAuth:
    JWT_ALGORITHM = "HS256"
    EXP_TIME = 60 * 60 * 24 * 365

    def __init__(self):
        pass

    def encode_jwt(self, user):
        payload = {
            "id": user.id,
            "login_id": user.login_id,
            "exp_time": int(time.mktime(datetime.now().timetuple())) + self.EXP_TIME
        }
        token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=self.JWT_ALGORITHM
        )
        return token

    def decode_jwt_to_user(self, token: str):
        from users.models import User

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[self.JWT_ALGORITHM]
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError) as e:
            raise CustomException(error_code=InvalidJwtErrorEnum.invalid_jwt, status_code=401)

        user_id = payload.get("id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CustomException(error_code=InvalidJwtErrorEnum.invalid_jwt, status_code=401)
        return user


class CustomAuth(HttpBearer):
    def authenticate(self, request, token):
        user = CustomJwtTokenAuth().decode_jwt_to_user(token)

        request.user = user

        return token


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


api = NinjaAPI(
    version="1.0.0",
    parser=ORJSONParser(),
    renderer=JSONRenderer(),
    auth=CustomAuth(),
    docs_url="/docs"
)


@api.exception_handler(CustomException)
def custom_exception(request, exc):
    return api.create_response(
        request,
        {"error_code": exc.error_code, "payload": exc.payload},
        status=exc.status_code,
    )
