
from django.urls import path
from .views import SignupView, LoginView, LogoutView, UserProfileView, PostsView
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('posts/', PostsView.as_view()),
    path('posts/<int:id>/', PostsView.as_view()),
]
