from app.models import Vehicle
from app.extensions import ma


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)