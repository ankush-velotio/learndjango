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
    TODO_NOT_FOUND
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
        email = request.data['email']
        password = request.data['password']

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
        response.set_cookie(key='jwt', value=access_token, httponly=True)

        response.data = {
            'message': AUTHENTICATION_SUCCESSFUL
        }

        return response


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    @staticmethod
    def get(request, **kwargs):
        user = request.user
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    @staticmethod
    def post(request):
        response = Response()
        blacklist_jwt_token(request.COOKIES.get('jwt'))
        response.delete_cookie('jwt')
        response.delete_cookie('csrftoken')
        response.data = {
            'message': LOGOUT_SUCCESSFUL
        }
        return response


class TodoView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    # Create to'do
    @staticmethod
    def post(request, **kwargs):
        serializer = TodoSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user, created_by=request.user.name)

        return Response(serializer.data)

    # List to'do
    @staticmethod
    def get(request, **kwargs):
        user = request.user

        # Get all of the To`do ids for which the current user is an editor
        editors = Todo.editors.through.objects.filter(user_id=user.id).all()
        todo_ids = [editor.todo_id for editor in editors]

        # Get the todos if current user is the owner or current user is the editor
        todos = Todo.objects.filter(Q(owner=user.id) | Q(id__in=todo_ids)).all()

        serializer = TodoSerializer(todos, many=True)

        return Response(serializer.data)

    # Update to'do
    @staticmethod
    def put(request, **kwargs):
        user = request.user
        todo_id = request.data['todo_id']

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
        todo_id: int = request.GET['todo-id']
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
        title: str = request.GET.get('title')
        todos = cls.list_of_todos(request)
        todos = [
            todo
            for todo in todos if todo['title'] == title
        ]

        return Response(todos)


class SortTodo(generics.ListAPIView, TodoUtils):
    @classmethod
    def get(cls, request, **kwargs):
        # Pass sort_type as a query parameter in the request URL
        sort_type: str = request.GET.get('sort_type').lower()
        if sort_type == "id":
            todos = cls.sort_by_id(request)
        elif sort_type == "date":
            todos = cls.sort_by_date(request)
        else:
            return Response(OPERATION_NOT_FOUND_ERROR)

        return Response(todos)

    @classmethod
    def sort_by_id(cls, request):
        todos = cls.list_of_todos(request)
        result = sorted(todos, key=lambda todo: todo['id'], reverse=True)
        return result

    @classmethod
    def sort_by_date(cls, request):
        todos = cls.list_of_todos(request)
        result = sorted(todos, key=lambda todo: todo['date'], reverse=True)
        return result
