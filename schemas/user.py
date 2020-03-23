from marshmallow import Schema, fields


class UserSchema(Schema):
    class Meta:
        load_only = ("password",)  # the data structure is a Tuple, don't forget the comma
        dump_only = ("id",)
    id = fields.Int(required=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True)



