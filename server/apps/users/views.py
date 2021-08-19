from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jwt_utils import generate_jwt_access_token, generate_jwt_refresh_token
from common.jwt_utils import verify_jwt_token, verify_jwt_refresh_token
from users.models import User, Todo
from users.serializers import UserSerializer, TodoSerializer


class RegisterView(APIView):
    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    # Using @ensure_csrf_cookie decorator for forcing Django to send the CSRF cookie in the response if the login success
    ensure_csrf_cookie_method = method_decorator(ensure_csrf_cookie)

    @ensure_csrf_cookie_method
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        # find the user with the input email
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Create JWT token
        access_token = generate_jwt_access_token(user)

        # Set JWT token as cookie. Set it as HTTP only so that no frontend can access the JWT token
        response = Response()
        response.set_cookie(key='jwt', value=access_token, httponly=True)

        # Generate JWT refresh token
        refresh_token = generate_jwt_refresh_token(user)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

        response.data = {
            'message': 'Authentication successful'
        }

        return response


class RefreshTokenView(APIView):
    # Using @csrf_protect decorator for making sure that the cookie (refresh token) is not compromised
    csrf_protect_method = method_decorator(csrf_protect)

    @csrf_protect_method
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        payload = verify_jwt_refresh_token(refresh_token)

        user = User.objects.filter(id=payload['id']).first()

        # Create JWT access token
        access_token = generate_jwt_access_token(user)

        # Set JWT token as cookie. Set it as HTTP only so that no frontend can access the JWT token
        response = Response()
        response.set_cookie(key='jwt', value=access_token, httponly=True)

        response.data = {
            'message': 'New access token generated'
        }

        return response


class UserView(APIView):
    @staticmethod
    def get(request):
        token = request.COOKIES.get('jwt')

        payload = verify_jwt_token(token)

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    @staticmethod
    def post(request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class TodoListView(APIView):
    @staticmethod
    def get(request):
        token = request.COOKIES.get('jwt')

        payload = verify_jwt_token(token)

        user = User.objects.filter(id=payload['id']).get()
        # Get all of the To`do ids for which the current user is an editor
        editors = Todo.editors.through.objects.filter(user_id=user.id).all()
        todo_ids = [editor.todo_id for editor in editors]

        # Get the todos if current user is the owner or current user is the editor
        todos = Todo.objects.filter(Q(owner=user.name) | Q(id__in=todo_ids)).all()

        serializer = TodoSerializer(todos, many=True)

        return Response(serializer.data)
