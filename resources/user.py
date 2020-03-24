import traceback
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
from schemas.user import UserSchema
from models.user import UserModel, MailGunException
from blacklist import BLACKLIST
from models.confirmation import ConfirmationModel

BLANK_ERROR = "'{}' CANNOT BE BLANK"
USER_ALREADY_EXIST = "A user with that username already exists."
EMAIL_ALREADY_EXIST = "A user with that email already exists."
INSERT_SUCCESS = "User created successfully."
FAILED_REGISTER_USER = "The User Failed to Register"
USER_NOT_FOUND_ERROR = "User not found."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
LOGOUT_SUCCESS = "User <id={}> successfully logged out."
NOT_CONFIRMED_ERROR = "Your registration is not confirmed, please complete your registration and check your email <{}> "
USER_CONFIRMED = "User Confirmed"

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
        user = user_schema.load(request.get_json())
        if UserModel.find_by_username(user.username):
            return {"message": USER_ALREADY_EXIST}, 400

        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_ALREADY_EXIST}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user_id=user.id)
            confirmation.save_database()
            user.send_confirmation_email()
            return {"message": INSERT_SUCCESS}, 201
        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": FAILED_REGISTER_USER}, 400


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
        user_data = user_schema.load(request.get_json(), partial=("email",))  # that will ignore email
        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, user_data.password):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            confirmation = user.most_recent_confirmation 
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity =user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400

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

# class UserConfirmation(Resource):
#     @classmethod
#     def get(cls, user_id):
#         user = UserModel.find_by_id(user_id)
#         if not user:
#             return {"message": USER_NOT_FOUND_ERROR}, 400
#
#         user.activated = True
#         user.save_to_db()
#         headers = {"Content-Type": "text/html"}
#         return make_response(render_template("confirmation_page.html", email=user.username), 200, headers)
