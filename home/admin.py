from django.contrib import admin
from django import forms
from home import models
from datetime import datetime


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'is_active']


class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'get_value', 'get_date']

    def get_name(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.value
    
    def get_date(self, obj):
        return obj.date.strftime("%d.%m.%Y %H:%M")

    get_name.short_description = 'Valuta'
    get_value.short_description = 'Valoare'
    get_date.short_description = 'Data'

class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_car', 'get_drivers']
    fields = ['plate_number', 'drivers']

    def get_car(self, obj):
        return obj.plate_number

    def get_drivers(self, obj):
        drivers = obj.drivers.all()
        return " / ".join([driver.full_name for driver in drivers])

    get_car.short_description = 'Masina(nr. inmatriculare)'
    get_drivers.short_description = 'Soferi'


class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_first_name', 'get_last_name', 'get_cars']

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name
    
    def get_cars(self, obj):
        cars = obj.car_set.all()
        return ", ".join([car.plate_number for car in cars])

    get_first_name.short_description = 'Nume'
    get_last_name.short_description = 'Prenume'
    get_cars.short_description = 'Masina'


class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name']

    def get_name(self, obj):
        return obj.name

    get_name.short_description = 'Nume'


class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name']

    def get_name(self, obj):
        return obj.name

    get_name.short_description = 'Tip cheltuiala'


class InvoiceCarInline(admin.TabularInline):
    model = models.InvoiceCar
    # exclude = ('expense_category',)
    extra = 1


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceCarInline]
    list_display = ['id', 'client', 'get_name', 'get_emit_date', 'status', 'get_value', 'get_currency', 'get_category', 'get_description', 'get_invoice_cars']

    def get_name(self, obj):
        return f'{obj.series}{obj.number}'
    
    def get_emit_date(self, obj):
        return obj.emit_date

    def get_value(self, obj):
        return obj.value
    
    def get_currency(self, obj):
        return obj.currency
    
    def get_category(self, obj):
        return obj.get_category_display()
    
    def get_description(self, obj):
        return obj.description
    
    def get_invoice_cars(self, obj):
        return " / ".join([f"{car.car.plate_number}({car.value})" for car in obj.invoicecar_set.all()])
    

    get_name.short_description = 'Factura'
    get_emit_date.short_description = 'Data emiterii'
    get_value.short_description = 'Valoare'
    get_currency.short_description = 'Valuta'
    get_category.short_description = 'Tip'
    get_description.short_description = 'Descriere'
    get_invoice_cars.short_description = 'Masini(suma) pe factura'


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Driver, DriverAdmin)
admin.site.register(models.Car, CarAdmin)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.ExpenseCategory, ExpenseCategoryAdmin)
admin.site.register(models.Invoice, InvoiceAdmin)