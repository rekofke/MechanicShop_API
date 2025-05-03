from app.models import SerializedPart
from app.extensions import ma

class SerializedPart_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True

serialized_part_schema = SerializedPart_Schema()
serialized_parts_schema = SerializedPart_Schema(many=True)
