from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

router = DefaultRouter()
router.register('employee_details', views.EmployeeCrudCBV)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'get_jwt_token/', obtain_jwt_token),
    url(r'refresh_jwt_token/', refresh_jwt_token),
    url(r'verify_jwt_token/', verify_jwt_token),
]
