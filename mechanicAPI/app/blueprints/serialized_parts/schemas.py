from app.models import SerializedPart
from app.extensions import ma
from marshmallow import fields

class SerializedPart_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True

serialized_part_schema = SerializedPart_Schema()
serialized_parts_schema = SerializedPart_Schema(many=True)


class ResponseSerializedPartSchema(ma.SQLAlchemyAutoSchema):
    description = fields.Nested("PartDescriptionSchema")
    class Meta:
        model = SerializedPart

response_schema = ResponseSerializedPartSchema()
responses_schema = ResponseSerializedPartSchema(many=True)
