# Generated by Django 4.1 on 2022-08-25 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificados', '0002_certificado_observacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificado',
            name='observacao',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]