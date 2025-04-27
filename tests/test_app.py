import unittest
from app import app, db
from models import Client, HealthProgram

class HealthInfoSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_program(self):
        response = self.app.post('/programs', json={'name': 'HIV'})
        self.assertEqual(response.status_code, 201)

    def test_register_client(self):
        response = self.app.post('/clients', json={'name': 'John Doe', 'email': 'john@example.com'})
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
