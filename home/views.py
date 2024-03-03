from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.apps import apps


# Create your views here.
class Home(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            request.resolver_match.url_name = 'login'
            return render(request, "auth/login-register.html", None)
        
        else:
            return render(request, "index.html", None)


class Login(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "auth/login-register.html", None)
        
        else:
            return redirect(reverse('home'))
    
    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username = username, password = password)
        if not user:
            context = dict (
                error = "Username sau parola gresita!"
            )
            return render(request, "auth/login-register.html", context)

        else:
            login(request, user)
            return redirect(reverse('home'))


class Logout(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            request.resolver_match.url_name = 'login'
            context = dict (
                message = "Te-ai delogat cu succes!"
            )
            return render(request, "auth/login-register.html", context)


class CreateAccount(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            context = dict (
                register = True
            )
            return render(request, "auth/login-register.html", context)
        
        else:
            return redirect(reverse('home'))
        
    def post(self, request):
        username = request.data.get('email')
        first_name = request.data.get('nume')
        last_name = request.data.get('prenume')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        user_data = dict(
            first_name = first_name,
            last_name = last_name,
            email = username
        )
        
        if password != confirm_password:
            context = dict (
                error = "Parolele nu coincid!"
            )

        else:

            if apps.get_model('home.User').objects.filter(email=username).exists():
                context = dict (
                    error = "Exista deja un cont inregistrat \
                            pe aceasta adresa de email!"
                )
            
            else:
                user_obj = apps.get_model('home.User').objects.create(**user_data)
                user_obj.set_password(password)
                user_obj.save()

                context = dict (
                    success = "Felicitari, te-ai inregistrat cu succes.\
                        Acum te poti autentifica in cont."
                )

            request.resolver_match.url_name = 'login'
            return render(request, "auth/login-register.html", context)