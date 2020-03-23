from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from flask import request
from marshmallow import ValidationError
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

BLANK_ERROR = "'{}' CANNOT BE BLANK"
USER_ALREADY_EXIST = "A user with that username already exists."
INSERT_SUCCESS = "User created successfully."
USER_NOT_FOUND_ERROR = "User not found."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
LOGOUT_SUCCESS = "User <id={}> successfully logged out."

user_schema = UserSchema()


# _user_parser = reqparse.RequestParser()
# _user_parser.add_argument(
#     "username", type=str, required=True, help=BLANK_ERROR.format("username")
# )
# _user_parser.add_argument(
#     "password", type=str, required=True, help=BLANK_ERROR.format("password")
# )
#

class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user_data["username"]):
            return {"message": USER_ALREADY_EXIST}, 400

        user = UserModel(**user_data)
        user.save_to_db()

        return {"message": INSERT_SUCCESS}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND_ERROR}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND_ERROR}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data["username"])

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, user_data["password"]):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": LOGOUT_SUCCESS.format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
