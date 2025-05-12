import unittest
from mechanicAPI.app import create_app
from mechanicAPI.app.models import db, Customer
from marshmallow import ValidationError



class TestCustomer(unittest.TestCase):

    def setup(self):
        # define an instance of custer to test
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="Test", email="test@test.com", phone="123-456-7890")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client() # allow us to send test requests to API and make mock requests for testing

    def test_create_customer(self):
        payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "503-555-1212"
        }

        response = self.client.post('/customers/', json=payload) # important in tests to have trailing backslash
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')

    def test_invalid_customer(self):
        payload = {
            "name": "John Doe",
            "phone": "503-555-1212"
        }

        response = self.client.post('/customers/', json=payload) # important in tests to have trailing backslash
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json)

    def test_get_customers(self):

        response = self.client.get('/customers/page=&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')