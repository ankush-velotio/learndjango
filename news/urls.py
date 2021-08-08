from django.urls import path

from . import views

urlpatterns = [
    # Setting dynamic url
    # Accept name of the reporter through URL and store it in reporter_name variable. Type of the variable is string.
    path('<str:reporter_name>/', views.reporter),
]
