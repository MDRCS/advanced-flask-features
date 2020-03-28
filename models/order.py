import stripe
import os
from db import db

CURRENCY = "usd"


class ItemsInOrder(db.Model):
    __tablename__ = "items_in_order"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    quantity = db.Column(db.Integer, default=1)

    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)

    items = db.relationship("ItemsInOrder", back_populates="order")  # back_populates="orders"  means if we changes

    # something in orders it will reflect to others
    @property
    def description(self):
        items_desc = [f"{i.quantity}x {i.item.name}" for i in self.items]
        return ",".join(items_desc)

    @property
    def amount(self):
        return int(sum([items_data.quantity * items_data.item.price for items_data in self.items]) * 100)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def set_status(self, new_status):
        self.status = new_status
        self.save_database()

    def charge_stripe(self, token):

        stripe.api_key = os.getenv("STRIPE_API_KEY")

        data = stripe.Token.create(
                    card={
                    "number": "4242424242424242",
                    "exp_month": 3,
                    "exp_year": 2021,
                    "cvc": "314",
                    },
                )

        token = data["id"]
        return stripe.Charge.create(
            amount=self.amount,  # cents ex: 100 -> USD $1
            currency=CURRENCY,
            description=self.description,
            source=token
        )

    def save_database(self):
        db.session.add(self)
        db.session.commit()

    def delete_database(self):
        db.session.remove(self)
        db.session.commit()
