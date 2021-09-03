import datetime
import json

import rest_framework.exceptions
from django.http.request import HttpRequest
from django.test import TestCase

from common.messages import AUTHENTICATION_SUCCESSFUL, LOGOUT_SUCCESSFUL, OPERATION_NOT_ALLOWED, TODO_REMOVED, TODO_NOT_FOUND
from users.models import User
from users.views import RegisterView, LoginView, UserView, LogoutView, TodoView


class UserTest(TestCase):
    jwt_token: str = ""

    @classmethod
    def setUpClass(cls):
        super(UserTest, cls).setUpClass()
        user_data: dict = {
            "name": "demo user",
            "email": "demo@gmail.com",
            "password": "pass",
        }
        request = HttpRequest()
        request.data = user_data
        RegisterView.post(request)

    def test_register(self):
        user_data: dict = {
            "name": "ankush",
            "email": "ankush@gmail.com",
            "password": "pass",
        }
        request = HttpRequest()
        request.data = user_data
        response = RegisterView.post(request)
        self.assertEqual(user_data["email"], response.data["email"])
        self.assertEqual(user_data["name"], response.data["name"])

    def test_user_view(self):
        required_result = {"id": 3, "name": "demo user", "email": "demo@gmail.com"}
        request = HttpRequest()
        request.user = User.objects.filter(email="demo@gmail.com").first()
        response = UserView.get(request=request)
        self.assertJSONEqual(json.dumps(required_result), response.data)

    def login_view(self):
        user_data = {"email": "demo@gmail.com", "password": "pass"}
        request = HttpRequest()
        request.data = user_data
        response = LoginView.post(self, request=request)
        self.jwt_token = (
            response.cookies.get("jwt")
            .__str__()
            .split(";")[0]
            .split("Set-Cookie: jwt=")[1]
        )
        self.assertEqual(AUTHENTICATION_SUCCESSFUL, response.data["message"])

    def logout_view(self):
        request = HttpRequest()
        request.COOKIES.setdefault("jwt", self.jwt_token)
        response = LogoutView.post(request=request)
        self.assertEqual(LOGOUT_SUCCESSFUL, response.data["message"])

    def test_login_then_logout(self):
        self.login_view()
        self.logout_view()


class TodoTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TodoTest, cls).setUpClass()
        cls.create_user("todo-user", "todo@gmail.com", "pass")
        cls.create_user("todo-user2", "todo2@gmail.com", "pass")

        cls.create_todo(
            status="inprogress",
            title="new todo",
            desc="From insomnia1",
            is_bookmarked=False,
            editors=[2],
            user_id=1,
        )

        cls.create_todo(
            status="completed",
            title="test todo",
            desc="Test todo",
            is_bookmarked=True,
            editors=[],
            user_id=2,
        )

    @staticmethod
    def create_user(name, email, password):
        user_data: dict = {"name": name, "email": email, "password": password}
        request = HttpRequest()
        request.data = user_data
        RegisterView.post(request)

    @staticmethod
    def create_todo(**kwargs):
        todo_data = {
            "status": kwargs["status"],
            "title": kwargs["title"],
            "description": kwargs["desc"],
            "is_bookmarked": kwargs["is_bookmarked"],
            "editors": kwargs["editors"],
        }
        request = HttpRequest()
        request.user = User.objects.filter(id=kwargs["user_id"]).first()
        request.data = todo_data
        response = TodoView.post(request)
        return response

    def test_create_todo(self):
        response1 = self.create_todo(
            status="inprogress",
            title="new todo",
            desc="Test todo",
            is_bookmarked=False,
            editors=[2],
            user_id=1,
        )
        # Converting datetime to float with milliseconds precision and then checking if the creation time is nearly
        # equals to the current time
        self.assertAlmostEqual(
            datetime.datetime.strptime(
                response1.data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).timestamp(),
            datetime.datetime.now().timestamp(),
            places=2,
        )
        self.assertEqual(response1.data["is_bookmarked"], False)
        self.assertEqual(response1.data["owner"], 1)
        self.assertEqual(response1.data["created_by"], "todo-user")

        response2 = self.create_todo(
            status="completed",
            title="test todo",
            desc="Test todo",
            is_bookmarked=True,
            editors=[],
            user_id=2,
        )
        self.assertAlmostEqual(
            datetime.datetime.strptime(
                response2.data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).timestamp(),
            datetime.datetime.now().timestamp(),
            places=2,
        )
        self.assertEqual(response2.data["is_bookmarked"], True)

        try:
            self.create_todo(
                status="", title="", desc="", is_bookmarked=False, editors=[], user_id=2
            )
        except rest_framework.exceptions.ValidationError as exc:
            self.assertEqual(rest_framework.exceptions.ValidationError, exc.__class__)

    def test_list_todo(self):
        id_ = 2
        request = HttpRequest()
        request.user = User
        request.user.id = id_
        response = TodoView.get(request)
        data = json.dumps(response.data)
        data = json.loads(data)
        flag = True
        for todo in data:
            editors = todo["editors"]
            if todo["owner"] != id_ and id_ not in editors:
                flag = False
            break
        self.assertTrue(flag)

    def test_update_todo(self):
        id_ = 1
        request = HttpRequest()
        request.user = User.objects.filter(id=id_).first()
        # update title
        request.data = self.update_todo_data(
            todo_id=1,
            created_by="todo-user",
            status="inprogress",
            title="title updated",
            desc="Test todo",
            is_bookmarked=False,
            owner=1,
            editors=[2],
        )
        response = TodoView.put(request)
        self.assertEqual(request.data["todo_id"], response.data["id"])
        self.assertEqual(request.data["owner"], response.data["owner"])
        self.assertEqual(request.user.name, response.data["updated_by"])

        # Test if it does not allow the operation if the user is not owner or editor of the to'do
        # Original owner of this to'do is the user with id 2. User with id 1 is not a owner nor editor of below to'do
        # See if the below update request throws error message when requested by user with id 1
        request.user = User.objects.filter(id=id_).first()
        request.data = self.update_todo_data(
            todo_id=2,
            created_by="todo-user",
            status="completed",
            title="test todo",
            desc="Test todo",
            is_bookmarked=True,
            owner=1,
            editors=[],
        )
        response = TodoView.put(request)
        self.assertEqual(OPERATION_NOT_ALLOWED, response.data)

    @staticmethod
    def update_todo_data(**kwargs):
        return {
            "todo_id": kwargs["todo_id"],
            "created_by": kwargs["created_by"],
            "status": kwargs["status"],
            "title": kwargs["title"],
            "description": kwargs["desc"],
            "is_bookmarked": kwargs["is_bookmarked"],
            "owner": kwargs["owner"],
            "editors": kwargs["editors"],
        }

    def test_delete_todo(self):
        id_ = 1
        todo_id = 1
        request = HttpRequest()
        request.user = User.objects.filter(id=id_).first()
        request.GET['todo-id'] = todo_id
        response = TodoView.delete(request)
        self.assertEqual(response.data, TODO_REMOVED)
        # Trying to delete already delete to'do
        response = TodoView.delete(request)
        self.assertEqual(response.data, TODO_NOT_FOUND)

        # Trying to delete the to'do for which current user is not a owner and nor an editor
        id_ = 1
        todo_id = 2
        request.user = User.objects.filter(id=id_).first()
        request.GET['todo-id'] = todo_id
        response = TodoView.delete(request)
        self.assertEqual(response.data, OPERATION_NOT_ALLOWED)
