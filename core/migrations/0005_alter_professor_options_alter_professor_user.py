# Generated by Django 5.1.4 on 2025-01-07 22:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_merge_20250107_1920'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='professor',
            options={'verbose_name': 'Professor', 'verbose_name_plural': 'Professores'},
        ),
        migrations.AlterField(
            model_name='professor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
