from ninja import Schema


class UserSchema(Schema):
    id: str
    login_id: str

    @classmethod
    def from_instance(cls, user):
        return cls(id=user.id, login_id=user.login_id)


class UserSignupParams(Schema):
    login_id: str
    password: str


class UserAuthDTO(Schema):
    user: UserSchema
    token: str

    @classmethod
    def from_instance(cls, user, token: str):
        return cls(user=user, token=token)
