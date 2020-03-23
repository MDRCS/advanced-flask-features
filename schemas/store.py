from marshmallow import schema, fields


class StoreSchema(schema):
    id = fields.Int()
    name = fields.Str(required=True)
