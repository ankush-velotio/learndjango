import json
import logging

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jwt_utils import generate_jwt_access_token
from common.jwt_utils import blacklist_jwt_token
from common.messages import (
    USER_NOT_FOUND,
    INCORRECT_PASSWORD,
    AUTHENTICATION_SUCCESSFUL,
    LOGOUT_SUCCESSFUL,
    OPERATION_NOT_ALLOWED,
    OPERATION_NOT_FOUND_ERROR,
    TODO_REMOVED,
    TODO_NOT_FOUND,
)
from users.models import User, Todo
from users.serializers import UserSerializer, TodoSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    # Using @ensure_csrf_cookie decorator for forcing Django to send the CSRF cookie in the response if the login success
    ensure_csrf_cookie_method = method_decorator(ensure_csrf_cookie)

    @ensure_csrf_cookie_method
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        # find the user with the input email
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed(USER_NOT_FOUND)

        if not user.check_password(password):
            raise AuthenticationFailed(INCORRECT_PASSWORD)

        # Create JWT token
        access_token = generate_jwt_access_token(user)

        # Set JWT token as cookie. Set it as HTTP only so that no frontend can access the JWT token
        response = Response()
        response.set_cookie(key="jwt", value=access_token, httponly=True)

        response.data = {"message": AUTHENTICATION_SUCCESSFUL}

        return response


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        user = User.objects.filter(email=self.request.user.email).first()
        return user


class LogoutView(APIView):
    @staticmethod
    def post(request):
        response = Response()
        blacklist_jwt_token(request.COOKIES.get("jwt"))
        response.delete_cookie("jwt")
        response.delete_cookie("csrftoken")
        response.data = {"message": LOGOUT_SUCCESSFUL}
        return response


class TodoView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(Q(owner=user.id) | Q(editors__email__contains=user.email)).distinct()

    # Create to'do
    @staticmethod
    def post(request, **kwargs):
        serializer = TodoSerializer(
            data=request.data,
            context={"owner": request.user, "created_by": request.user.name},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # Update to'do
    @staticmethod
    def put(request, **kwargs):
        user = request.user
        todo_id = request.data["todo_id"]

        # Get the to'do that user want to update from database and check if to'do in our database has current user as a editor
        todo = Todo.objects.filter(id=todo_id).first()
        editors = todo.editors.all()

        # If current user is not an owner or editor for the to'do then don't process the request
        if user != todo.owner and user not in editors:
            return Response(OPERATION_NOT_ALLOWED)

        serializer = TodoSerializer(todo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user.name)

        return Response(serializer.data)

    # Delete to'do
    @staticmethod
    def delete(request, **kwargs):
        todo_id: int = request.GET["todo-id"]
        user = request.user

        try:
            # Get the to'do that user want to update from database and check if to'do in our database has current user as a editor
            todo = Todo.objects.filter(id=todo_id).first()
            editors = todo.editors.all()

            # If current user is not an owner or editor for the to'do then don't process the request
            if user != todo.owner and user not in editors:
                return Response(OPERATION_NOT_ALLOWED)

            todo.delete()

            return Response(TODO_REMOVED)
        except AttributeError:
            logging.exception(TODO_NOT_FOUND, exc_info=False)

        return Response(TODO_NOT_FOUND)


class TodoUtils:
    @staticmethod
    def list_of_todos(request) -> list:
        todos = TodoView.get(request)
        todos = json.dumps(todos.data)
        todos = json.loads(todos)
        return todos


class SearchTodo(generics.RetrieveAPIView, TodoUtils):
    @classmethod
    def get(cls, request, **kwargs):
        # Pass title as a query parameter in the request URL
        title: str = request.GET.get("title")
        todos = cls.list_of_todos(request)
        todos = [todo for todo in todos if todo["title"] == title]

        return Response(todos)


class SortTodo(generics.ListAPIView):
    serializer_class = TodoSerializer
    ordering_fields = ['id', 'date']
    ordering = ['date']

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(Q(owner=user.id) | Q(editors__email__exact=user.email)).distinct()
