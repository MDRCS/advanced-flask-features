from marshmallow import Schema, fields


class ItemSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    store_id = fields.Int(required=True)


