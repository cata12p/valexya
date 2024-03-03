from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_plate_number(value):
    if ' ' in value or not value.isalnum():
        raise ValidationError(
            _('Numarul de înmatriculare nu poate contine spatii sau caractere speciale.'), code='invalid_plate_number'
        )


class User(AbstractUser):
    '''Aceasta e clasa custom a Userului, aici adaugam campuri noi'''
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        self.username = self.email
        
        super(User, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    

class Driver(models.Model):
    '''Aceasta este clasa Soferilor, aici adaugam campuri noi'''
    first_name = models.CharField(max_length=255, default=None, help_text='Numele soferului')
    last_name = models.CharField(max_length=255, default=None, help_text='Prenumele soferului')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.full_name


class Car(models.Model):
    '''Aceasta este clasa Masinilor, aici adaugam campuri noi'''
    plate_number = models.CharField(max_length=255, default=None, 
        validators=[validate_plate_number], help_text='Numarul de inmatriculare')
    drivers = models.ManyToManyField(Driver, help_text='Soferul / soferii de pe masina')

    def __str__(self):
        return self.plate_number


class Client(models.Model):
    '''Aceasta este clasa Clientului, aici adaugam campuri noi'''
    name = models.CharField(max_length=255, default=None, help_text='Numele clientului')

    def __str__(self):
        return self.name


class Invoice(models.Model):
    '''Aceasta este clasa Facturilor, aici adaugam campuri noi'''
    CURRENCY_CHOICES = [
        ('RON', 'RON'),
        ('EUR', 'EUR')
    ]

    SERIES_CHOICES = [
        ('VAL', 'VAL'),
        ('VIC', 'VIC'),
        ('VLX', 'VLX')
    ]

    STATUS_CHOICES = [
        ('EMISA', 'EMISA'),
        ('INCASATA', 'INCASATA'),
        ('DEPASITA', 'DEPASITA')
    ]

    CATEGORY_CHOICES = [
        ('INCOMING', 'VENIT'),
        ('OUTCOMING', 'CHELTUIALA')
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None,
        blank=True, help_text='Clientul de pe factura')
    series = models.CharField(max_length=3, choices=SERIES_CHOICES, help_text='Seria facturii')
    number = models.IntegerField(default=0, help_text='Numarul facturii')
    emit_date = models.DateTimeField(default=None, null=True, help_text='Data emitere factura')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=None, null=True, help_text='Statusul facturii')
    value = models.DecimalField(default=.0, max_digits=9, decimal_places=2, help_text='Valoarea facturata')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, help_text='Valuta de pe factura')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, help_text='Tipul facturii')
    description = models.CharField(max_length=255, default=None, null=True, blank=True, 
        help_text='Descriere optionala(ex: cursa BH - IF / revizie placute)')
    
    def __str__(self):
        return f'{self.series}{self.number}'


class ExpenseCategory(models.Model):
    '''Aceasta este clasa Categorie Cheltuiala, aici adaugam campuri noi'''
    name = models.CharField(max_length=255, default=None, help_text='Numele categoriei de cheltuiala')

    def __str__(self):
        return self.name


class InvoiceCar(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, help_text='Factura masinii')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, help_text='Masina de pe factura')
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, null=True, blank=True, default=None,
        help_text='Categoria cheltuielii, NULL inseamna ca e venit')
    value = models.DecimalField(default=.0, max_digits=9, decimal_places=2, help_text='Valoarea facturata')