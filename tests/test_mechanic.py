from app import create_app
from app.models import db, Mechanic
from datetime import datetime
from utils.utils import encode_token, token_required
import unittest

class TestMechanic(unittest.TestCase): # Define a test class inherit from unittest.TestCase
    def setUp(self): # Create a test app instance
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(name='text_user',address='123 test st', email='test@email.com', password='123')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1, 'admin')
        self.clilent = self.app.test_client()

def test_invalid_creation(self):
    mechanic_payload = {
        'name': 'John Doe',
        'address': '123 Main St',
        'password': '123'
    }

    response = self.client.post('/mechanics/', json=mechanic_payload)
    self.assertEqual(response.status.code, 400) # verify that invalid data returns a 400 status code
    self.assertEqual(response.json['email'], ['Missing data for required field.']) 

def test_login_mechanic(self):
    credentials = {
        'email': 'test@email.com',
        'password': '123'
    }

    response = self.client.post('/mechanics/login', json=credentials)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json['status'], 'success')
    return response.json['token']