from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.Router.as_view(), name='router'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.CreateAccount.as_view(), name='register'),
    path('raports/<str:type>', views.Raports.as_view(), name='raports'),
    path('cars/', views.Cars.as_view(), name='cars'),
    path('cars/<int:id>', views.CarEdit.as_view(), name='edit-car'),
    path('invoices/', views.Invoices.as_view(), name='invoices'),
    path('drivers', views.Drivers.as_view(), name='drivers')
]