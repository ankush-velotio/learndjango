from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from common.jwt_utils import generate_jwt_access_token
from common.jwt_utils import blacklist_jwt_token
from common.messages import (
    USER_NOT_FOUND,
    INCORRECT_PASSWORD,
    AUTHENTICATION_SUCCESSFUL,
    LOGOUT_SUCCESSFUL,
    OPERATION_NOT_ALLOWED,
    TODO_REMOVED
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


class UserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]

    @staticmethod
    def get(request, **kwargs):
        user = request.user
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]

    # Create to'do
    @staticmethod
    def post(request, **kwargs):
        user = request.user

        # Set current user as a owner and creator of the to'do
        request.data['owner'] = user.id
        request.data['created_by'] = user.name

        serializer = TodoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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

        # Set current user as updated by
        request.data['updated_by'] = user.name

        serializer = TodoSerializer(todo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # Delete to'do
    @staticmethod
    def delete(request, **kwargs):
        todo_id: int = request.GET['todo-id']
        user = request.user

        # Get the to'do that user want to update from database and check if to'do in our database has current user as a editor
        todo = Todo.objects.filter(id=todo_id).first()
        editors = todo.editors.all()

        # If current user is not an owner or editor for the to'do then don't process the request
        if user != todo.owner and user not in editors:
            return Response(OPERATION_NOT_ALLOWED)

        todo.delete()

        return Response(TODO_REMOVED)
