# Generated by Django 2.2.6 on 2019-11-13 19:55
from django.contrib.auth.models import User, UserManager

from django.db import migrations


def populate_ldap_cred_default(apps, schema_editor):

    user = User.objects.filter(is_superuser=True)
    if user.exists():
        user = user.first()
    else:
        user = User.objects.create(
            username='soc_su', email='soc_su@phsa.ca',
            password='soc_su_password', is_active=True, is_staff=True,
            is_superuser=True)
        user.set_password('soc_su_password')
        user.save()

    default_cred_dict = {
        'domain': 'VCH',
        'username': 'LoginPI01',
        'password': 'LoginPI1!',
        'is_default': True,
        'created_by_id': user.id,
        'updated_by_id': user.id,
    }

    ldap_cred_model = apps.get_model('ldap_probe', 'LDAPBindCred')

    if ldap_cred_model.objects.filter(
            domain__iexact=default_cred_dict.get('domain'),
            username__iexact=default_cred_dict.get('username')).exists():
        return

    default_ldap_cred = ldap_cred_model(**default_cred_dict)
    default_ldap_cred.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_probe', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_ldap_cred_default,
                             reverse_code=migrations.RunPython.noop)
    ]
