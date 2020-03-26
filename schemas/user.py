from models.user import UserModel
from marshmallow_model import ma


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)  # the data structure is a Tuple, don't forget the comma
        dump_only = ("id","confirmation")

