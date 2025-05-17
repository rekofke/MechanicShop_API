from app import create_app
from app.models import db, Vehicle
from app.utils import encode_token
from marshmallow.exceptions import ValidationError
import unittest


class TestVehicles(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.vehicle = Vehicle(
            part_name="test_part",
            brand="test_brand",
            price=100.0
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.vehicle)
            db.session.commit()
        self.token = encode_token({"user_id": 1})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_vehicle(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand",
            "price": 100.0
        }

        response = self.client.post('/vehicles/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_create_vehicle_invalid(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand"
        }

        response = self.client.post('/vehicles/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_get_vehicles(self):
        response = self.client.get('/vehicles/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_vehicle_not_found(self):
        response = self.client.get('/vehicles/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'No part descriptions found')

    def test_get_vehicle(self):
        response = self.client.get(f'/vehicles/{self.vehicle.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_update_vehicle(self):
        update_payload = {
            "id": self.vehicle.id,
            "part_name": "updated_part",
            "brand": "updated_brand",
            "price": 150.0
        }

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/vehicles/{self.vehicle.id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'updated_part')

    def test_delete_vehicle(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.delete(f'/vehicles/{self.vehicle.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)