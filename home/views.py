from django.shortcuts import render, redirect
from django.urls import reverse, resolve
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from django.http import JsonResponse, HttpResponse
import requests
from requests.exceptions import ConnectTimeout, RequestException, Timeout
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# def get_page_name(request):
#     resolver_match = resolve(request.path)
#     return resolver_match.url_name
# new_page = get_page_name(request) # asta e paginarea cu /login de ex


def check_authentication(request):
    if not request.user.is_authenticated:
        request.session['page'] = 'login'
        return render(request, "auth/login-register.html", None)


def get_bnr_exchange_rate(currency_code):
    course_obj = apps.get_model('home.Course').objects.filter(name=currency_code, date__date=datetime.now().date()).first()

    if course_obj is not None:
        return course_obj.value

    else:
        try:
            url = 'https://www.bnr.ro/nbrfxrates.xml'
            response = requests.get(url, timeout = 10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for cube in root.iter('{http://www.bnr.ro/xsd}Cube'):
                    for rate in cube.iter('{http://www.bnr.ro/xsd}Rate'):
                        currency = rate.attrib.get('currency')
                        rate_value = Decimal(rate.text)
                        if currency == currency_code:
                            course_data = dict (
                                name = currency,
                                value = rate_value
                            )
                            course_obj = apps.get_model('home.Course').objects.create(**course_data)
                            course_obj.save()
                            
                            return rate_value
                        
        except (ConnectTimeout, ConnectionError, Timeout, RequestException) as e:
            print(f"O eroare a apărut în timpul cererii către serverul BNR: {e}")

            course_obj = apps.get_model('home.Course').objects.filter(name=currency_code).last()

            if course_obj is not None:
                return course_obj.value
            
            else:
                return Decimal('4.9707')
        
    return None


def get_dates_range(date_type):
    today = datetime.now()

    if date_type == 'weekly':
        day_of_week = today.weekday()
        start_date = today - timedelta(days=day_of_week)
        end_date = start_date + timedelta(days=6)

    elif date_type == 'monthly':
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

    elif date_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

    else:
        raise ValueError("Tip de data invalid")

    return start_date, end_date


class Router(APIView):
    def get(self, request):
        page = request.session.get('page')

        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            if page is None or page == 'raports':
                raports_view = Raports()
                context = raports_view.get_incomings_data(request, request.session.get('type'))
                return render(request, "home/raports.html", context)
            
            elif page == 'cars':
                cars_view = Cars()
                context = cars_view.get_cars_data(request)
                return render(request, "home/cars.html", context)
            
            elif page == 'edit-car':
                cars_view = CarEdit()
                context = cars_view.get_car_data(request, request.session.get('entity'))
                return render(request, "home/edit-car.html", context)
            
            elif page == 'invoices':
                invoices_view = Invoices()
                context = invoices_view.get_invoices_data(request)
                return render(request, "home/invoices.html", context)
            
            elif page == 'drivers':
                drivers_view = Drivers()
                context = drivers_view.get_drivers_data(request, request.session.get('entity'))
                return render(request, "home/drivers.html", context)


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
            request.session.flush()
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
    def get(self, request, type = None):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_incomings_data(request, type)
            return render(request, "home/raports.html", context)

    def get_incomings_data(self, request, type = None):
        request.session['page'] = 'raports'
        request.session['type'] = type
        if type == 'daily':
            # data_incoming_invoices = apps.get_model('home.InvoiceCar').objects.filter(invoice__category='incoming')
            incomings_data = apps.get_model('home.Invoice').objects.filter(category='incoming', emit_date__date=datetime.now().date())
            outgoings_data = apps.get_model('home.Invoice').objects.filter(category='outgoing', emit_date__date=datetime.now().date())

        elif type in ['weekly', 'monthly', 'yearly']:
            # data_incoming_invoices = apps.get_model('home.InvoiceCar').objects.filter(invoice__category='incoming')
            start_date, end_date = get_dates_range(type)
            incomings_data = apps.get_model('home.Invoice').objects.filter(category='incoming', emit_date__range=[start_date.date(), end_date.date()])
            outgoings_data = apps.get_model('home.Invoice').objects.filter(category='outgoing', emit_date__range=[start_date.date(), end_date.date()])

        elif type is None or type == 'general':
            # data_incoming_invoices = apps.get_model('home.InvoiceCar').objects.filter(invoice__category='incoming')
            incomings_data = apps.get_model('home.Invoice').objects.filter(category='incoming')
            outgoings_data = apps.get_model('home.Invoice').objects.filter(category='outgoing')


        raports_data = dict(
            total_outgoings = 0,
            total_balance = 0,
            total_issued = 0,
            total_collected = 0
        )
        for incoming_data in incomings_data:
            value = incoming_data.value / get_bnr_exchange_rate('EUR') if incoming_data.currency == 'ron' and get_bnr_exchange_rate('EUR') else incoming_data.value
            # if incoming_data.status == 'issued':
            raports_data['total_issued'] += value
            if incoming_data.status == 'collected':
                raports_data['total_collected'] += value


        for outgoing_data in outgoings_data:
            raports_data['total_outgoings'] += outgoing_data.value / get_bnr_exchange_rate('EUR') if outgoing_data.currency == 'ron' and get_bnr_exchange_rate('EUR') else outgoing_data.value

        balance = raports_data['total_collected'] - raports_data['total_outgoings']
        profitability = (balance / raports_data['total_collected']) * 100
        raports_data['total_collected'] = "{:,.2f}".format(raports_data['total_collected'])
        raports_data['total_outgoings'] = "{:,.2f}".format(raports_data['total_outgoings'])
        raports_data['total_balance'] = "{:,.2f}".format(balance)
        raports_data['total_profitability'] = "{:,.2f}".format(profitability)

        context = dict (
            incomings = incomings_data,
            outgoings = outgoings_data,
            raports = raports_data
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
            incoming_value, outgoing_value = 0, 0
            if invoice_car.invoice.category == 'incoming':
                incoming_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'ron' and get_bnr_exchange_rate('EUR') else invoice_car.value
            else:
                outgoing_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'ron' and get_bnr_exchange_rate('EUR') else invoice_car.value

            if car_id not in cars_invoice_values:
                cars_invoice_values[car_id] = {'incoming': 0, 'outgoing': 0}

            cars_invoice_values[car_id]['incoming'] += incoming_value
            cars_invoice_values[car_id]['outgoing'] += outgoing_value

        # Adaugă suma valorilor facturate fiecărei mașini în context
        for car in cars_data:
            car_invoice_values = cars_invoice_values.get(car.id, {'incoming': 0, 'outgoing': 0})
            car.total_incoming_value = "{:,.2f}".format(car_invoice_values['incoming'])
            car.total_outgoing_value = "{:,.2f}".format(car_invoice_values['outgoing'])
            car.total_profit_value = "{:,.2f}".format(car_invoice_values['incoming'] - car_invoice_values['outgoing'])
            # car.currency = "EUR"

        # print(cars_data)

        context = dict(
            cars = cars_data,
            drivers = drivers_data
        )
        return context


class CarEdit(APIView):
    def get(self, request, id = None):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_car_data(request, id)
            return render(request, "home/edit-car.html", context)
        
    def post(self, request, id = None):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            invoice_data = dict (
                client = apps.get_model('home.Client').objects.get(pk=request.data.get('client')) if request.data.get('client') else None,
                series = request.data.get('series'),
                number = request.data.get('number'),
                emit_date = request.data.get('emit_date'),
                due_date = request.data.get('due_date'),
                category = request.data.get('category'),
                status = request.data.get('status'),
                value = request.data.get('value'),
                currency = request.data.get('currency'),
                description = request.data.get('description')
            )
            
            invoice_obj = apps.get_model('home.Invoice').objects.create(**invoice_data)
            invoice_obj.save()

            invoice_car_data = dict (
                invoice = invoice_obj,
                car = apps.get_model('home.Car').objects.get(pk=request.session.get('entity')),
                expense_category = apps.get_model('home.ExpenseCategory').objects.get(pk=request.data.get('expense_category')) if request.data.get('expense_category') else None,
                value = invoice_obj.value
            )
            invoice_car_obj = apps.get_model('home.InvoiceCar').objects.create(**invoice_car_data)
            invoice_car_obj.save()

            context = self.get_car_data(request, id)
            context['message'] = "Factura a fost adaugata cu succes!"
            return render(request, "home/edit-car.html", context)
        
    def get_car_data(self, request, id = None):
        request.session['page'] = 'edit-car'
        request.session['entity'] = id
        car_data = apps.get_model('home.Car').objects.get(pk=id)
        clients_data = apps.get_model('home.Client').objects.all()
        expense_categories_data = apps.get_model('home.ExpenseCategory').objects.all()

        invoice_cars = apps.get_model('home.InvoiceCar').objects.select_related('invoice').filter(car__id=id)
        # print(invoice_cars)

        # Calculează suma valorilor facturate pentru fiecare mașină
        cars_invoice_values = dict()
        for invoice_car in invoice_cars:
            car_id = invoice_car.car_id
            incoming_value, outgoing_value = 0, 0
            if invoice_car.invoice.category == 'incoming':
                incoming_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'ron' and get_bnr_exchange_rate('EUR') else invoice_car.value
            else:
                outgoing_value = invoice_car.value / get_bnr_exchange_rate('EUR') if invoice_car.invoice.currency == 'ron' and get_bnr_exchange_rate('EUR') else invoice_car.value

            if car_id not in cars_invoice_values:
                cars_invoice_values[car_id] = {'incoming': 0, 'outgoing': 0}

            cars_invoice_values[car_id]['incoming'] += incoming_value
            cars_invoice_values[car_id]['outgoing'] += outgoing_value

        # Adaugă suma valorilor facturate fiecărei mașini în context
        car_invoice_values = cars_invoice_values.get(id, {'incoming': 0, 'outgoing': 0})
        car_data.total_incoming_value = "{:,.2f}".format(car_invoice_values['incoming'])
        car_data.total_outgoing_value = "{:,.2f}".format(car_invoice_values['outgoing'])
        car_data.total_profit_value = "{:,.2f}".format(car_invoice_values['incoming'] - car_invoice_values['outgoing'])
        # car.currency = "EUR"

        context = dict(
            car = car_data,
            clients = clients_data,
            expense_categories = expense_categories_data,
            emit_date = datetime.now().date(),
            due_date = datetime.now().date() + relativedelta(months=1),
            invoices_car = invoice_cars
        )
        return context
    

class Invoices(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_invoices_data(request)
            return render(request, "home/invoices.html", context)

    def get_invoices_data(self, request):
        request.session['page'] = 'invoices'
        incomings_data = apps.get_model('home.Invoice').objects.filter(category='incoming')
        context = dict (
            invoices = incomings_data
        )
        return context



class Drivers(APIView):
    def get(self, request, id = None):
        if not request.user.is_authenticated:
            return check_authentication(request)
        
        else:
            context = self.get_drivers_data(request, id)
            return render(request, "home/drivers.html", context)

    def get_drivers_data(self, request, id = None):
        request.session['page'] = 'drivers'
        drivers_data = apps.get_model('home.Driver').objects.all()
        context = dict (
            drivers = drivers_data
        )
        return context