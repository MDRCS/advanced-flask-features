from collections import Counter
import stripe
from flask_restful import Resource
from flask import request
from models.item import ItemModel
from models.order import OrderModel, ItemsInOrder
from schemas.order import OrderSchema

order_schema = OrderSchema()
list_orders_schema = OrderSchema(many=True)


class Order(Resource):

    @classmethod
    def post(cls):
        """
        Expect a token and a list of item ids from the request body.
        Construct an order and talk to the Strip API to make a charge.
        """
        data = request.get_json()  # token + list of item ids  [1, 2, 4, 4, 5, 2, 1, 1, 4]
        items = []
        item_id_quantities = Counter(data["item_ids"])

        # Iterate over items and retrieve them from the database
        for _id, count in item_id_quantities.most_common():  # [(1,3),(2,2),(4,3),(5,1)]
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": "Item {} Not Found.".format(_id)}, 404

            items.append(ItemsInOrder(item_id=_id, quantity=count))

        order = OrderModel(items=items, status="pending")
        order.save_database()  # this does not submit to Stripe

        try:
            order.set_status("failed")  # assume the order would fail until it's completed
            order.charge_stripe(data["token"])
            order.set_status("complete")  # charge succeeded
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
            return {"message": e.error.message}, e.http_status

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return {"message": e.error.message}, e.http_status

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return {"message": e.error.message}, e.http_status
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return {"message": e.error.message}, e.http_status
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return {"message": e.error.message}, e.http_status
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return {"message": e.error.message}, e.http_status
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            return {"message": e.error.message}, e.http_status

        return order_schema.dump(order), 200


class ListOrders(Resource):

    @classmethod
    def get(cls):
        return list_orders_schema.dump(OrderModel.find_all()), 200

