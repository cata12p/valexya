from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.Home.as_view(), name='home')
]