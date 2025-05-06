from app.models import PartDescription
from app.extensions import ma

class PartDescription_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription
        include_relationships = True  # Optional, includes relationships if needed

part_description_schema = PartDescription_Schema()
part_descriptions_schema = PartDescription_Schema(many=True)
