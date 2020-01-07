# Generated by Django 2.2.6 on 2020-01-03 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_probe', '0042_auto_20200103_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adnodeperfbucket',
            name='name',
            field=models.CharField(db_index=True, help_text='A descriptive name to help determine which nodes should be included in the bucket.', max_length=253, unique=True, verbose_name='Bucket name'),
        ),
    ]