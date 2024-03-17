from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.apps import apps
import random

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        print('Seeding invoices ...')

        count = 0
        nr = 10
        while count < nr:
            obj_data = dict (
                client = apps.get_model('home.Client').objects.first(),
                series = 'VAL',
                number = random.randint(1, 100),
                emit_date = datetime.now(),
                status = 'EMISA',
                value = random.randint(100, 10000),
                currency = 'EUR',
                category = 'OUTGOING'
            )
            invoice_obj = apps.get_model('home.Invoice').objects.create(**obj_data)
            invoice_obj.save()
            count += 1

        print('Successfully seeded!')