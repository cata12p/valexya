from django.shortcuts import render
from rest_framework.views import APIView


# Create your views here.
class Home(APIView):
    def get(self, request):
        return render(request, "index.html", None)
    
class Login(APIView):
    def get(self, request):
        return render(request, "auth/login.html", None)