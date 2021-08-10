from rest_framework.viewsets import ModelViewSet
from . models import Employee
from . serializers import EmployeeSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class EmployeeCrudCBV(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializers
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]
