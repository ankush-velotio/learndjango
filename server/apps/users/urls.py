from django.urls import path
from rest_framework_jwt import views as jwt_views
from users import views


urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("user/", views.UserView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("refresh-access-token/", jwt_views.RefreshJSONWebToken.as_view()),
    # to'do app views
    path("todo/", views.TodoView.as_view()),
    # to'do functions
    path("search/", views.SearchTodo.as_view()),
    path("sort/", views.SortTodo.as_view()),
]
