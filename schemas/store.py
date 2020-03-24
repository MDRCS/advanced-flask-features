from ma import ma
from models.store import StoreModel  # The order of import is important
from models.item import ItemModel


class StoreSchema(ma.ModelSchema):
    items = ma.Nested(ItemModel, many=True)

    class Meta:
        model = StoreModel
        dump_only = ("id",)
        include_fk = True
