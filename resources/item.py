from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    jwt_required,
    fresh_jwt_required,
)

from models.item import ItemModel
from schemas.item import ItemSchema

BLANK_ERROR = "'{}' CANNOT BE BLANK"
ITEM_NOT_FOUND = "Item not found."
ITEM_ALREADY_EXIST_ERROR = "An item with name '{}' already exists."
INSERT_ERROR = "An error occurred while inserting the item."
ITEM_DELETED = "Item deleted."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


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
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {"message": ITEM_ALREADY_EXIST_ERROR.format(name)}, 400

        item_json = request.get_json()
        item_json["name"] = name
        item = item_schema.load(item_json)
        print(item.name, item.price, item.store_id)
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
        data = request.get_json()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    def get(self):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
