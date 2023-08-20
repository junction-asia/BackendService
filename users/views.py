from django.shortcuts import render

from cores.apis import api, CustomJwtTokenAuth
from cores.enums import ApiTagEnum
from cores.exceptions import CustomException
from users.enums import UserAuthEnum
from users.models import User
from users.schemas import UserSignupParams, UserSchema, UserAuthDTO


# Create your views here.


@api.get(
    path="user/",
    response={200: UserSchema},
    tags=[ApiTagEnum.users]
)
def get_user(request):
    user = request.user

    return UserSchema.from_instance(user)


@api.post(
    path='user/',
    auth=None,
    response={200: UserAuthDTO},
    tags=[ApiTagEnum.users]
)
def signup_user(request, params: UserSignupParams):
    login_id = params.login_id
    password = params.password

    try:
        User.objects.get(login_id=login_id)

        raise CustomException(status_code=400, error_code=UserAuthEnum.user_exists)
    except User.DoesNotExist:
        user = User.objects.create(login_id=login_id)
        user.set_password(password)
        user.save()

        token = CustomJwtTokenAuth().encode_jwt(user)

        return UserAuthDTO.from_instance(user, token)


@api.post(
    path='user/login/',
    response={200: UserAuthDTO},
    auth=None,
    tags=[ApiTagEnum.users]
)
def login_user(request, params: UserSignupParams):
    login_id = params.login_id
    password = params.password

    try:
        user = User.objects.get(login_id=login_id)

        is_valid_password = user.check_password(password)

        if is_valid_password:
            token = CustomJwtTokenAuth().encode_jwt(user)

            return UserAuthDTO.from_instance(user, token)
        else:
            raise CustomException(status_code=400, error_code=UserAuthEnum.password_not_valid)
    except User.DoesNotExist:
        raise CustomException(status_code=400, error_code=UserAuthEnum.user_not_exists)
