# Generated by Django 5.1.4 on 2025-01-07 22:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Escola',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('endereco', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='professor',
            name='email',
        ),
        migrations.RemoveField(
            model_name='professor',
            name='especialidades',
        ),
        migrations.RemoveField(
            model_name='professor',
            name='senha',
        ),
        migrations.AddField(
            model_name='professor',
            name='anos_preferidos',
            field=models.JSONField(default=[]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='professor',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='professor',
            name='escolas_preferidas',
            field=models.ManyToManyField(blank=True, to='core.escola'),
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serie', models.CharField(max_length=2)),
                ('periodo', models.CharField(choices=[('Matutino', 'Matutino'), ('Vespertino', 'Vespertino')], max_length=20)),
                ('status', models.CharField(default='disponível', max_length=20)),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.disciplina')),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.escola')),
                ('professor_atribuido', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.professor')),
            ],
        ),
        migrations.AddField(
            model_name='professor',
            name='turmas_preferidas',
            field=models.ManyToManyField(blank=True, to='core.turma'),
        ),
        migrations.DeleteModel(
            name='Aula',
        ),
    ]
