from app import create_app
from app.models import db, SerializedPart
from app.utils import encode_token
from marshmallow.exceptions import ValidationError
import unittest


class TestSerializedParts(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.serialized_part = SerializedPart(
            part_name="test_part",
            brand="test_brand",
            price=100.0
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.serialized_part)
            db.session.commit()
        self.token = encode_token({"user_id": 1})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_serialized_part(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand",
            "price": 100.0
        }

        response = self.client.post('/serialized_parts/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_create_serialized_part_invalid(self):
        payload = {
            "part_name": "test_part",
            "brand": "test_brand"
        }

        response = self.client.post('/serialized_parts/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_get_serialized_parts(self):
        response = self.client.get('/serialized_parts/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_serialized_part_not_found(self):
        response = self.client.get('/serialized_parts/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'No part descriptions found')

    def test_get_serialized_part(self):
        response = self.client.get(f'/serialized_parts/{self.serialized_part.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_update_serialized_part(self):
        update_payload = {
            "id": self.serialized_part.id,
            "part_name": "updated_part",
            "brand": "updated_brand",
            "price": 150.0
        }

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.put(f'/serialized_parts/{self.serialized_part.id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'updated_part')

    def test_delete_serialized_part(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.delete(f'/serialized_parts/{self.serialized_part.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)