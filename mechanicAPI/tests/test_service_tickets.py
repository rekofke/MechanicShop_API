from app import create_app
from app.models import db, Service_Ticket
from app.utils import encode_token
from marshmallow.exceptions import ValidationError
import unittest


class TestService_Tickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.service_ticket = Service_Ticket(
            part_name="test_part",
            brand="test_brand",
            price=100.0
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.service_ticket)
            db.session.commit()
        self.token = encode_token({"user_id": 1})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_service_ticket(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand",
            "price": 100.0
        }

        response = self.client.post('/service_tickets/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_create_service_ticket_invalid(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand"
        }

        response = self.client.post('/service_tickets/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_service_ticket_not_found(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'No part descriptions found')

    def test_get_service_ticket(self):
        response = self.client.get(f'/service_tickets/{self.service_ticket.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_update_service_ticket(self):
        update_payload = {
            "id": self.service_ticket.id,
            "part_name": "updated_part",
            "brand": "updated_brand",
            "price": 150.0
        }

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'updated_part')

    def test_delete_service_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.delete(f'/service_tickets/{self.service_ticket.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    
    def add_part_to_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/{self.serialized_part.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'updated_part')

    def remove_part_from_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/{self.serialized_part.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def invalid_part(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Invalid part or ticket')

    def add_mechanic_to_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/{self.mechanic.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'up')

    def remove_mechanic_from_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/{self.mechanic.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def invalid_mechanic(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Invalid mechanic or ticket')

    def add_unused_part_to_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/{self.mechanic.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'updateupdated_name')