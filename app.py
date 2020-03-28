import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError

import dotenv

dotenv.load_dotenv(".env")

from marshmallow_model import ma
from db import db
from oauth import oauth
import image_upload

from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout, SetPassword
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarImage
from resources.github_login import GithubLogin, GithubAuthorize
from resources.order import Order,ListOrders

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI', "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["UPLOADED_IMAGES_DEST"] = os.path.join('static', 'images')  # The same as your UploadSet("images", ...)
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
app.secret_key = os.environ.get('secret_key')  # could do app.config['JWT_SECRET_KEY'] if we prefer
patch_request_class(app, 10 * 1024 * 1024)  # 10bit * 1024 = 10kb * 1024 = 10MB
configure_uploads(app, image_upload.IMAGE_SET)

api = Api(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)

db.init_app(app)
ma.init_app(app)
oauth.init_app(app)


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return (
        decrypted_token["jti"] in BLACKLIST
    )  # Here we blacklist particular JWTs that have been created in the past.


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarImage, "/upload/avatar")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorized", endpoint="github.authorize")
api.add_resource(SetPassword, "/user/password")
api.add_resource(Order, "/order")
api.add_resource(ListOrders, "/orders")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    oauth.init_app(app)

    # @app.before_first_request
    # def create_tables():
    #     db.create_all()

    app.run(port=5000, debug=True)
