# Generated by Django 3.0.5 on 2020-04-03 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_vcenter', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clustervcenter',
            options={'verbose_name': 'vCenter configuration', 'verbose_name_plural': 'vCenter configurations'},
        ),
    ]