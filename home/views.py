from django.shortcuts import render, redirect
from django.urls import reverse, resolve
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from django.http import JsonResponse
import requests
import xml.etree.ElementTree as ET
from decimal import Decimal


# def get_page_name(request):
#     resolver_match = resolve(request.path)
#     return resolver_match.url_name
# new_page = get_page_name(request) # asta e paginarea cu /login de ex

# views.py

def get_bnr_exchange_rate(currency_code):
    url = 'https://www.bnr.ro/nbrfxrates.xml'
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for cube in root.iter('{http://www.bnr.ro/xsd}Cube'):
            for rate in cube.iter('{http://www.bnr.ro/xsd}Rate'):
                currency = rate.attrib.get('currency')
                rate_value = Decimal(rate.text)
                if currency == currency_code:
                    return rate_value
    
    return None


# Create your views here.
def check_authentication(request):
    if not request.user.is_authenticated:
        request.session['page'] = 'login'
        return render(request, "auth/login-register.html", None)


class Router(APIView):
    def get(self, request):
        page = request.session.get('page')

        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            if page == 'cars':
                cars_view = Cars()
                context = cars_view.get_cars_data(request)
                return render(request, "home/cars.html", context)

            elif page == 'raports':
                raports_view = Raports()
                context = raports_view.get_incomings_data(request)
                return render(request, "home/raports.html", context)


class Login(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            raports_view = Raports()
            context = raports_view.get_incomings_data(request)
            return render(request, "home/raports.html", context)
    
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
            raports_view = Raports()
            context = raports_view.get_incomings_data(request)
            return render(request, "home/raports.html", context)


class Logout(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            request.session['page'] = 'login'
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
            raports_view = Raports()
            context = raports_view.get_incomings_data(request)
            return render(request, "home/raports.html", context)
        
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

            request.session['page'] = 'login'
            return render(request, "auth/login-register.html", context)


class Raports(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_incomings_data(request)
            return render(request, "home/raports.html", context)

    def get_incomings_data(self, request):
        request.session['page'] = 'raports'
        # data_incoming_invoices = apps.get_model('home.InvoiceCar').objects.filter(invoice__category='INCOMING')
        incomings_data = apps.get_model('home.Invoice').objects.filter(category='INCOMING')
        outcomings_data = apps.get_model('home.Invoice').objects.filter(category='OUTCOMING')
        context = dict (
            incomings = incomings_data,
            outcomings = outcomings_data
        )
        return context


class Cars(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_cars_data(request)
            return render(request, "home/cars.html", context)
        
    def post(self, request):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            car_data = dict (
                plate_number = request.data.get('plate_number')
            )
            drivers = request.data.getlist('drivers')
            cars_obj = apps.get_model('home.Car').objects.create(**car_data)
            cars_obj.drivers.add(*drivers)
            cars_obj.save()

            context = self.get_cars_data(request)
            context['message'] = "Masina a fost adaugata cu succes!"
            
            return render(request, "home/cars.html", context)
        
    def get_cars_data(self, request):
        request.session['page'] = 'cars'
        cars_data = apps.get_model('home.Car').objects.all().order_by('id')
        drivers_data = apps.get_model('home.Driver').objects.all()

        invoice_cars = apps.get_model('home.InvoiceCar').objects.select_related('invoice').filter(car__in=cars_data)

        # Calculează suma valorilor facturate pentru fiecare mașină
        cars_invoice_values = dict()
        for invoice_car in invoice_cars:
            car_id = invoice_car.car_id
            incoming_value, outcoming_value = 0, 0
            if invoice_car.invoice.category == 'INCOMING':
                incoming_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'RON' and get_bnr_exchange_rate('EUR') else invoice_car.value
            else:
                outcoming_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'RON' and get_bnr_exchange_rate('EUR') else invoice_car.value

            if car_id not in cars_invoice_values:
                cars_invoice_values[car_id] = {'incoming': 0, 'outcoming': 0}

            cars_invoice_values[car_id]['incoming'] += incoming_value
            cars_invoice_values[car_id]['outcoming'] += outcoming_value

        # Adaugă suma valorilor facturate fiecărei mașini în context
        for car in cars_data:
            car_invoice_values = cars_invoice_values.get(car.id, {'incoming': 0, 'outcoming': 0})
            car.total_incoming_value = "{:,.2f}".format(car_invoice_values['incoming'])
            car.total_outcoming_value = "{:,.2f}".format(car_invoice_values['outcoming'])
            car.total_profit_value = "{:,.2f}".format(car_invoice_values['incoming'] - car_invoice_values['outcoming'])
            # car.currency = "EUR"

        print(cars_data)

        context = dict(
            cars = cars_data,
            drivers = drivers_data
        )
        return context