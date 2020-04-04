# Generated by Django 3.0.5 on 2020-04-02 23:08

import django.db.models.deletion
from django.db import migrations, models

import netbox_vcenter.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('virtualization', '0014_standardize_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterVCenter',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False
                )),
                ('server', models.CharField(
                    max_length=64,
                    validators=[netbox_vcenter.validators.HostnameAddressValidator()]
                )),
                ('validate_certificate', models.BooleanField(
                    default=True
                )),
                ('username', models.CharField(
                    max_length=64
                )),
                ('password', models.CharField(
                    max_length=64
                )),
                ('cluster', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='vcenter',
                    to='virtualization.Cluster'
                )),
            ],
        ),
    ]
