# Generated by Django 2.1 on 2018-08-23 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestCertsData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_value', models.CharField(blank=True, max_length=100, null=True)),
                ('valid_start', models.DateTimeField(blank=True, null=True)),
                ('valid_end', models.DateTimeField(blank=True, null=True)),
                ('xmldata', models.TextField(null=True, verbose_name='??')),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('hostname', models.CharField(blank=True, max_length=100, null=True)),
                ('commonName', models.CharField(blank=True, max_length=100, null=True)),
                ('organizationName', models.CharField(blank=True, max_length=100, null=True)),
                ('countryName', models.CharField(blank=True, max_length=100, null=True)),
                ('sig_algo', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('bits', models.CharField(blank=True, max_length=100, null=True)),
                ('md5', models.CharField(blank=True, max_length=100, null=True)),
                ('sha1', models.CharField(blank=True, max_length=100, null=True)),
                ('orion_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
