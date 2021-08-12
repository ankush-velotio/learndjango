from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('jwtauth.urls')),
    # Complete authentication using custom JWT token
    path('api/', include('users.urls')),
]
