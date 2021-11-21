from django.urls import path
from app_user import views

app_name = 'app_user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('me/logout', views.UserLogout.as_view(), name='me-logout'),
]
