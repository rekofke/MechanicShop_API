from app import create_app
from app.models import db, Mechanic
from datetime import datetime
from app.utils import encode_token
from werkzeug.security import generate_password_hash
import unittest


class TestMechanic(unittest.TestCase): # Define a test class inherit from unittest.TestCase
    def setUp(self): # Create a test app instance
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(
            name='text_user',
            address='123 test st', 
            email='test@email.com', 
            password=generate_password_hash('123') # create hashed password since creating mechanic outside of route, need to have hash to reference
            )
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

def test_invalid_creation(self):
    mechanics_payload = {
        'name': 'John Doe',
        'address': '123 Main St',
        'password': '123'
    }

    response = self.client.post('/mechanics/', json=mechanics_payload)
    self.assertEqual(response.status_code, 400) # verify that invalid data returns a 400 status code
    self.assertEqual(response.json['email'], ['Missing data for required field.']) 

def test_login_mechanic(self):
    payload = {
        'email': 'test@email.com',
        'password': '123'
    }

    response = self.client.post('/mechanics/login', json=payload)
    self.assertEqual(response.status_code, 200) # ensure correct response code
    self.assertIn('token', response.json)
    self.assertEqual(response.json['status'], 'success')
    return response.json['token']

def test_mechanic_update(self):
    update_payload = {
        'name': 'John Doe',
        'address': '456 Elm St',
        'email': "jd@email.com",
        'password': '123'
    }

    headers = {
        'Authorization': 'Bearer ' + self.token
    }
    response = self.client.put('/mechanics/', json=update_payload, headers=headers)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json['name'], 'John Doe')