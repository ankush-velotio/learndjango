from django.urls import path
from users import views


urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('user/', views.UserView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('refresh-access-token/', views.RefreshTokenView.as_view()),
    # to'do app views
    path('todo-list/', views.TodoListView.as_view()),
]
