from django.test import TestCase
from rest_framework.test import APIClient  # Import this for API testing

class SignUpTest(TestCase):
    def setUp(self):
        self.client = APIClient()  # Create a test client instance

    def test_signup_success(self):
        data = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@example.com",
            "password": "strongpassword123"
        }
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 200)  # Expect HTTP 200 status code
        # You can add more assertions to check the response data if needed