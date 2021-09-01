import json

from django.http.request import HttpRequest
from django.test import TestCase

from common.messages import AUTHENTICATION_SUCCESSFUL, LOGOUT_SUCCESSFUL
from users.models import User
from users.views import RegisterView, LoginView, UserView, LogoutView


class UserTest(TestCase):
    jwt_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFua3VzaEBnbWFpbC5jb20iLCJleHAiOjE2MzA1MTA3NzMsImVtYWlsIjoiYW5rdXNoQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjMwNDk4NzczfQ.o-LF1qwuV2TEoEKzkgX4WTv-I8CybgT9xM9StKaGPnA"

    @classmethod
    def setUpClass(cls):
        super(UserTest, cls).setUpClass()
        user_data: dict = {
            "name": "demo user",
            "email": "demo@gmail.com",
            "password": "pass"
        }
        request = HttpRequest()
        request.data = user_data
        RegisterView.post(request)

    def test_register(self):
        user_data: dict = {
            "name": "ankush",
            "email": "ankush@gmail.com",
            "password": "pass"
        }
        request = HttpRequest()
        request.data = user_data
        response = RegisterView.post(request)
        self.assertEqual(user_data['email'], response.data['email'])
        self.assertEqual(user_data['name'], response.data['name'])

    def test_login_view(self):
        user_data = {
          "email": "demo@gmail.com",
          "password": "pass"
        }
        request = HttpRequest()
        request.data = user_data
        response = LoginView.post(self, request=request)
        self.jwt_token = response.cookies.get('jwt')
        self.assertEqual(AUTHENTICATION_SUCCESSFUL, response.data["message"])

    def test_user_view(self):
        required_result = {
          "id": 1,
          "name": "demo user",
          "email": "demo@gmail.com"
        }
        request = HttpRequest()
        request.user = User.objects.filter(email="demo@gmail.com").first()
        response = UserView.get(request=request)
        self.assertJSONEqual(json.dumps(required_result), response.data)

    def test_logout_view(self):
        request = HttpRequest()
        request.COOKIES.setdefault('jwt', self.jwt_token)
        response = LogoutView.post(request=request)
        self.assertEqual(LOGOUT_SUCCESSFUL, response.data['message'])
