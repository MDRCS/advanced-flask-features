from time import time
from uuid import uuid4

from db import db

CONFIRMATION_EXPERATION_DELTA = 1800 # 30 min


class ConfirmationModel(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPERATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self):
        return time() > self.expire_at

    def force_to_expire(self):
        if not self.expired:
            self.expire_at = int(time())
            self.save_database()

    def save_database(self):
        db.session.add(self)
        db.session.commit()

    def delete_database(self):
        db.session.remove(self)
        db.session.commit()
