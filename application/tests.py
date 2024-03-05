from django.test import TestCase
from rest_framework.test import APIClient  # Import this for API testing

class Testsignup(TestCase):
    def setUp(self):
        self.client = APIClient()  # Create a test client instance

    ############ Sign Up tests ######################
    def test_signup_success(self):
        """
        For successful sign up
        """
        data = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "password1!D"
        }
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 201)  # Expect HTTP 201 status code

    def test_dublicate_user(self):
        """
        Unsucessful user creation - Dublicate user
        """
        data = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "password1!D"
        }
        response = self.client.post('/application/signup/', data)
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 409) # 409 - conflict

    def test_weak_password(self):
        """
        Test for user creationg with weak passwords
        """

        # Only lowercase
        data = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "password"
        }

        # Just with 1 digit
        data1 = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "password1"
        }

        # Still missing uppercase
        data2 = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "password1!"
        }

        # Too short
        data3 = {
            "first_name": "Test", 
            "last_name": "User",
            "email": "test@test.com",
            "password": "Pa!2"
        }
        response = self.client.post('/application/signup/', data)
        response1 = self.client.post('/application/signup/', data1)
        response2 = self.client.post('/application/signup/', data2)
        response3 = self.client.post('/application/signup/', data3)
        self.assertEqual(response.status_code, 409) # 409 - conflict
        self.assertEqual(response1.status_code, 409)
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response3.status_code, 409)

    def test_signup_missing_fields(self):
        """
        Should no tbe let to create an account if a password, email or any of the names is missing
        """
        data = {"first_name": "Test", "last_name": "User", "password": "password1!D"} # Missing email
        data1 = {"email": "test@test.com", "last_name": "User1", "password": "password1!D"} # First name
        data2 = {"email": "test@test.com","first_name": "Test2",  "password": "password1!D"} # last name
        data3 = {"email": "test@test.com","first_name": "Test3", "last_name": "User3"} # Password
        
        response = self.client.post('/application/signup/', data)
        response1 = self.client.post('/application/signup/', data1)
        response2 = self.client.post('/application/signup/', data2)
        response3 = self.client.post('/application/signup/', data3)
        self.assertEqual(response.status_code, 409) # 409 - conflict
        self.assertEqual(response1.status_code, 409)
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response3.status_code, 409)


    def test_invalid_email(self):
        """
        Check if the email is valid
        """
        data1 = {"email": "invalid", "first_name":"Test", "last_name": "User1", "password": "password1!D"} 
        data2 = {"email": "inv@lid@gmail.com", "first_name":"Test", "last_name": "User1", "password": "password1!D"} 
        data3 = {"email": "invalid@gmail", "first_name":"Test", "last_name": "User1", "password": "password1!D"} 
        data4 = {"email": "invalid.com", "first_name":"Test", "last_name": "User1", "password": "password1!D"} 
        data5 = {"email": "invalid@.com", "first_name":"Test", "last_name": "User1", "password": "password1!D"} 
   
        response1 = self.client.post('/application/signup/', data1)
        response2 = self.client.post('/application/signup/', data2)
        response3 = self.client.post('/application/signup/', data3)
        response4 = self.client.post('/application/signup/', data4)
        response5 = self.client.post('/application/signup/', data5)
        self.assertEqual(response1.status_code, 409) # 409 - Bad request
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response3.status_code, 409)
        self.assertEqual(response4.status_code, 409)
        self.assertEqual(response5.status_code, 409)


    ############ Sign In tests #####################
    def test_successful_sign_in(self):
        """
        Sucessful sign in
        """
        data = {"email":"test@gmail.com","first_name": "Test", "last_name": "User", "password": "password1!D"}
        data_signin = {"email":"test@gmail.com", "password":"password1!D"}
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 201) # Created user
        response2 = self.client.post('/application/signin/', data_signin)
        self.assertEqual(response2.status_code, 200) # Signed in successfuly

    def test_unsuccesful_sign_in(self):
        """
        Unsuccesful sign in - wrong credentials
        """
        data = {"email":"test@gmail.com","first_name": "Test", "last_name": "User", "password": "password1!D"}
        data_signin = {"email":"tesst@gmail.com", "password":"password1!D"} # wrong email
        data_signin2 = {"email":"test@gmail.com", "password":"passwdord1!D"} # wrong password
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 201) # Created user
        response2 = self.client.post('/application/signin/', data_signin)
        self.assertEqual(response2.status_code, 401) # UNsuccessful sign in
        response3 = self.client.post('/application/signin/', data_signin2)
        self.assertEqual(response3.status_code, 401) # UNsuccessful sign in

    def test_non_existent_user(self):
        """
        Nonexistent user should not be able to sign in
        """
        data_signin = {"email":"tesst@gmail.com", "password":"password1!D"}
        response = self.client.post('/application/signin/', data_signin)
        self.assertEqual(response.status_code, 401) # Did not log in
    
    ############# Log Out tests ###################
    def test_sign_out_success(self):
        """
        Successful sign out
        """    
        data = {"email":"test@gmail.com","first_name": "Test", "last_name": "User", "password": "password1!D"}
        data_signin = {"email":"test@gmail.com", "password":"password1!D"}
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 201) # Created user
        response2 = self.client.post('/application/signin/', data_signin)
        sign_in_response = self.client.post('/application/signin/', data_signin) # collect token
        self.assertEqual(response2.status_code, 200) # Signed in successfuly

        # Use the token in the Authorization header
        token = sign_in_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response3 = self.client.post('/application/signout/')
        self.assertEqual(response3.status_code, 200) # Signed out

    def test_sifn_out_invalid_token(self):
        """
        Attempt to sign out with an invalid token
        """
        data = {"email":"test@gmail.com","first_name": "Test", "last_name": "User", "password": "password1!D"}
        data_signin = {"email":"test@gmail.com", "password":"password1!D"}
        response = self.client.post('/application/signup/', data)
        self.assertEqual(response.status_code, 201) # Created user
        response2 = self.client.post('/application/signin/', data_signin)
        self.assertEqual(response2.status_code, 200) # Signed in successfuly
        data_refresh = {"refresh_token": "invalid_refresh_token"}
        response3 = self.client.post('/application/signout/', data_refresh)
        self.assertEqual(response3.status_code, 401) # Could not sign out
   
    # def test_signin_success(self):
    #     # Assuming you've created a user in `setUp`
    #     data = {"email": "testsignin@example.com", "password": "strongpassword123"}
    #     response = self.client.post('/application/signin/', data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('access', response.data)
