from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    jwt_required,
    fresh_jwt_required,
)
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema

BLANK_ERROR = "'{}' CANNOT BE BLANK"
ITEM_NOT_FOUND = "Item not found."
ITEM_ALREADY_EXIST_ERROR = "An item with name '{}' already exists."
INSERT_ERROR = "An error occurred while inserting the item."
ITEM_DELETED = "Item deleted."

item_schema = ItemSchema()


class Item(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument(
    #     "price", type=float, required=True, help=BLANK_ERROR.format("price")
    # )
    # parser.add_argument(
    #     "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    # )

    @jwt_required  # No longer needs brackets
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return (
                {"message": ITEM_ALREADY_EXIST_ERROR.format(name)},
                400,
            )

        try:
            item_data = item_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        item = ItemModel(name, **item_data)

        try:
            item.save_to_db()
        except:
            return {"message": INSERT_ERROR}, 500

        return item_schema.dump(item), 201

    @jwt_required
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    def get(self):
        items = [item_schema.dump(item) for item in ItemModel.find_all()]
        return {"items": items}, 200
