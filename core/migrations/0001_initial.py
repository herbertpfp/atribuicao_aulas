# Generated by Django 5.1.4 on 2025-01-06 21:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('especialidades', models.CharField(max_length=255)),
                ('pontuacao', models.IntegerField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('senha', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materia', models.CharField(max_length=100)),
                ('horario', models.DateTimeField()),
                ('requisitos', models.CharField(max_length=255)),
                ('status', models.CharField(default='disponível', max_length=20)),
                ('professor_atribuido', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.professor')),
            ],
        ),
    ]
