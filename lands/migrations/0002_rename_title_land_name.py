# Generated by Django 4.2.4 on 2023-08-19 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='land',
            old_name='title',
            new_name='name',
        ),
    ]
