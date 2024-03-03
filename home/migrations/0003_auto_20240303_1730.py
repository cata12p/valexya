# Generated by Django 3.2.8 on 2024-03-03 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20240303_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='cars',
        ),
        migrations.AlterField(
            model_name='expensecategory',
            name='name',
            field=models.CharField(default=None, help_text='Numele categoriei de cheltuiala', max_length=255),
        ),
        migrations.CreateModel(
            name='InvoiceCar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, default=0.0, help_text='Valoarea facturata', max_digits=9)),
                ('car', models.ForeignKey(help_text='Masina de pe factura', on_delete=django.db.models.deletion.CASCADE, to='home.car')),
                ('expense_category', models.ForeignKey(blank=True, default=None, help_text='Categoria cheltuielii, NULL inseamna ca e venit', on_delete=django.db.models.deletion.CASCADE, to='home.expensecategory')),
                ('invoice', models.ForeignKey(help_text='Factura masinii', on_delete=django.db.models.deletion.CASCADE, to='home.invoice')),
            ],
        ),
    ]
