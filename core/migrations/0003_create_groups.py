# -*- coding: utf-8 -*-
from django.db import migrations

def create_groups_and_permissions(apps, schema_editor):
    from django.contrib.auth.models import Group, Permission
    from django.db.models import Q
    from django.contrib.contenttypes.models import ContentType
    from core.models import Escola, Professor, Turma  # Ajuste se necessário

    # Criando o grupo 'Dono' e atribuindo permissões
    dono_group, created = Group.objects.get_or_create(name='Dono')
    if created:
        permissions = Permission.objects.all()  # Todos as permissões
        dono_group.permissions.set(permissions)

    # Criando o grupo 'Gestor' e atribuindo permissões
    gestor_group, created = Group.objects.get_or_create(name='Gestor')
    if created:
        permissions = Permission.objects.filter(
            Q(content_type=ContentType.objects.get_for_model(Turma)) |
            Q(content_type=ContentType.objects.get_for_model(Professor))
        )
        gestor_group.permissions.set(permissions)

    # Criando o grupo 'Diretor de Escola' e atribuindo permissões
    diretor_group, created = Group.objects.get_or_create(name='Diretor de Escola')
    if created:
        permissions = Permission.objects.filter(
            Q(content_type=ContentType.objects.get_for_model(Escola)) |
            Q(content_type=ContentType.objects.get_for_model(Turma))
        )
        diretor_group.permissions.set(permissions)

    # Criando o grupo 'Professor' e atribuindo permissões
    professor_group, created = Group.objects.get_or_create(name='Professor')
    if created:
        permissions = Permission.objects.filter(
            Q(content_type=ContentType.objects.get_for_model(Professor))
        )
        professor_group.permissions.set(permissions)

class Migration(migrations.Migration):
    dependencies = [
        # Dependência da migração anterior (por exemplo: 'core.0001_initial')
        ('core', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions),
    ]

