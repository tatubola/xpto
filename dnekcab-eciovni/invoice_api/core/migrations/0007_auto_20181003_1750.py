# Generated by Django 2.0.8 on 2018-10-03 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20180921_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdecompra',
            name='url',
            field=models.CharField(blank=True, error_messages={'invalid': 'Insira uma url válida.'}, max_length=255),
        ),
    ]