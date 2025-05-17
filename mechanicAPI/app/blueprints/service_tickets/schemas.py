import re
from app.models import Service_Ticket, Mechanic, SerializedPart
from app.extensions import ma
from marshmallow import fields, schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema



class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanic = fields.Nested("MechanicSchema", many=True)
    vehicle = fields.Nested("VehcicleSchema")

    class Meta:
        model = Service_Ticket
        fields = ("date", "type", "status", "customer_id", "vehicle_id", "mechanic")
        include_fk = True
        

# NOT SURE IF THIS BELONGS BUT WOULD NOT LET ME RUN APP.PY WITHOUT IT SINCE IT IS IMPORTED IN ROUTES.PY
class ReturnMechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        fields = ("id", "name", "address")
        include_fk = True
    
    
class EditServiceTicketSchema(ma.Schema):
    add_mechanic_id = fields.List(fields.Int(), required=True)
    delete_mechanic_id = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ("add_mechanic_id", "delete_mechanic_id")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_tickets_schema = EditServiceTicketSchema()
return_mechanic_schema = ReturnMechanicSchema()
