from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.Router.as_view(), name='router'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.CreateAccount.as_view(), name='register'),
    path('raports/', views.Raports.as_view(), name='raports'),
    path('cars/', views.Cars.as_view(), name='cars')
]