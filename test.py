# Imports
import unittest
from server import app 


class TestApp(unittest.TestCase):

    def test_home(self):
        with app.test_client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)

    def test_login(self):
        with app.test_client() as client:
            response = client.get("/login")
            self.assertIn(response.status_code, range(300, 399))  # Check for redirect

    def test_logout(self):
        with app.test_client() as client:
            response = client.get("/logout")
            self.assertIn(response.status_code, range(300, 399))  # Check for redirect

# Run tests if script is executed directly
if __name__ == "__main__":
    unittest.main()
