# Generated by Django 5.1.4 on 2025-01-13 15:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_atribuicao_gestor_responsavel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professor',
            name='deletado',
        ),
        migrations.RemoveField(
            model_name='professor',
            name='retificado',
        ),
        migrations.AddField(
            model_name='professor',
            name='id_sede',
            field=models.ForeignKey(blank=True, help_text='Escola sede do professor, caso aplicável.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='professores_sede', to='core.escola'),
        ),
    ]
