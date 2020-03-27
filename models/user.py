import os
from typing import Dict, Union
from flask import request, url_for
import requests
from db import db
from .confirmation import ConfirmationModel

userJSON = Dict[str, Union[int, str]]

MAILGUN_API_URL = os.environ.get('MAILGUN_API_URL')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')

FROM = 'Mailgun Sandbox <postmaster@sandbox19504dde8aa64489a091e1e67640c06e.mailgun.org>'


class MailGunException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(80), nullable=False, unique=True)
    # LAZY=DYNAMIC # MEAN THAT IF YOU TRY FOR EXAMPLE TO CREATE THAT OBJECT (User) THE CLASS WITH WHICH YOU HAVE THIS
    # RELATIONSHIP (ConfirmationModel) AND HAVE THIS PROPERTY OF LAZY=DYNAMIC WOULD NOY BE RETREIVED directly.
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    """
    user = UserModel(...)
    confirmation = ConfirmationModel(...)
    confirmation.save_database()
    print(user.confirmation) # is allowed with lazy="dynamic"
    """

    @property
    def most_recent_confirmation(self):
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    # we can do that -> self.most_recent_confirmation.id and get id of the most
    # recent confirmation

    def json(self) -> Dict:
        return {"id": self.id, "username": self.username, "password": self.password}

    def send_confirmation_email(self):
        # http://127.0.0.1:5000/user-confirm/1
        link = request.url_root[0:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )

        if not MAILGUN_API_KEY:
            raise MailGunException("Failed to load MAILGUN API KEY")

        if not MAILGUN_API_URL:
            raise MailGunException("Failed to load MAILGUN API URL")

        response = requests.post(
            MAILGUN_API_URL,
            auth=("api", MAILGUN_API_KEY),
            data={"from": FROM,
                  "to": self.email,
                  "subject": "REGISTRATION CONFIRMATION",
                  "text": f"Please Click the link to confirm your registration: {link}"})

        if response.status_code != 200:
            raise MailGunException("Failed to send registration Email to the user")

        return response

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
