# Generated by Django 4.1 on 2022-08-27 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificados', '0006_alter_perfil_turma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='turma',
            field=models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)]),
        ),
    ]
