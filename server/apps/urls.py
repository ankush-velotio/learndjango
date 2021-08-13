from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # Complete authentication using custom JWT token
    path('api/', include('apps.users.urls')),
]
