from app.models import Mechanic
from app.extensions import ma


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=['name', 'address'])
return_mechanic_schema = MechanicSchema()
edit_mechanic_schema = MechanicSchema(partial=True)