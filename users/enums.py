from cores.enums import CustomEnum


class UserAuthEnum(CustomEnum):
    user_exists = 'user_exists'
    user_not_exists = 'user_not_exists'
    password_not_valid = 'password_not_valid'
