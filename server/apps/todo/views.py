import jwt

from django.conf import settings
from django.db.models import Q
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Todo
from .serializer import TodoSerializer
from ..users.models import User


class TodoListView(APIView):
    @staticmethod
    def get(request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise NotAuthenticated('Unauthenticated!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise NotAuthenticated('Authentication failed! Signature Expired!')

        user = User.objects.filter(id=payload['id']).get()
        # Get all of the To`do ids for which the current user is an editor
        editors = Todo.editors.through.objects.filter(user_id=user.id).all()
        todo_ids = [editor.todo_id for editor in editors]

        # Get the todos if current user is the owner or current user is the editor
        todos = Todo.objects.filter(Q(owner=user.name) | Q(id__in=todo_ids)).all()

        serializer = TodoSerializer(todos, many=True)

        return Response(serializer.data)
