# Generated by Django 5.1.4 on 2025-01-14 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_professor_cargo'),
    ]

    operations = [
        migrations.AddField(
            model_name='escola',
            name='id_escola',
            field=models.CharField(default=[], help_text='Identificação da escola.', max_length=255),
            preserve_default=False,
        ),
    ]
