# /core/management/commands/import_csv.py

import csv
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from core.models import Professor, Escola

class Command(BaseCommand):
    help = "Importa dados das planilhas professores.csv e escolas.csv para o banco de dados e cria usuários para professores."

    def handle(self, *args, **kwargs):
        # Certifique-se de que o grupo "Professor" existe
        professor_group, created = Group.objects.get_or_create(name="Professor")
        if created:
            self.stdout.write("Grupo 'Professor' criado.")

        # Importar dados dos professores
        try:
            with open('professores.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    id_sede = Escola.objects.filter(id_escola=row.get('id_sede')).first() if row.get('id_sede') else None

                    # Excluir professor se marcado como 'sim' no campo excluir
                    if row.get('excluir', '').strip().lower() == 'sim':
                        Professor.objects.filter(cpf=row['cpf']).delete()
                        User.objects.filter(username=row['cpf']).delete()
                        self.stdout.write(f"Professor removido: {row['nome']}")
                        continue

                    # Criar ou atualizar o professor
                    professor, _ = Professor.objects.update_or_create(
                        cpf=row['cpf'],
                        defaults={
                            'nome': row['nome'],
                            'pontuacao_peb': int(row['pontuacao_peb']) if row['pontuacao_peb'] else None,
                            'pontuacao_paeb': int(row['pontuacao_paeb']) if row['pontuacao_paeb'] else None,
                            'disciplina_peb': row.get('disciplina_peb', None),
                            'disciplina_paeb': row.get('disciplina_paeb', None),
                            'celular': row['celular'],
                            'cargo': row['cargo'],
                            'id_sede': id_sede,
                        },
                    )

                    # Criar ou atualizar o usuário do Django
                    user, user_created = User.objects.update_or_create(
                        username=row['cpf'],
                        defaults={
                            'first_name': row['nome'].split(' ')[0],  # Primeiro nome
                            'last_name': ' '.join(row['nome'].split(' ')[1:]),  # Sobrenome
                            'email': f"{row['cpf']}@exemplo.com",  # E-mail fictício
                            'is_staff': False,  # Não faz parte do staff/admin
                            'is_active': True,  # Ativo para login
                        },
                    )

                    # Se o usuário foi criado pela primeira vez, defina a senha padrão
                    if user_created:
                        user.set_password('123')  # Senha padrão
                        user.groups.add(professor_group)  # Adicionar ao grupo Professor
                        user.save()
                        self.stdout.write(f"Usuário criado para o professor: {professor.nome}")
                    else:
                        self.stdout.write(f"Usuário já existente para o professor: {professor.nome}")
        except FileNotFoundError:
            self.stderr.write("Erro: Arquivo professores.csv não encontrado.")

        # Importar dados das escolas
        try:
            with open('escolas.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    # Garantir valores padrão para status caso estejam ausentes
                    status_matutino = row.get('status_matutino', '').strip() or ', '.join(['L'] * len(row['turmas_matutino'].split(', ')))
                    status_vespertino = row.get('status_vespertino', '').strip() or ', '.join(['L'] * len(row['turmas_vespertino'].split(', ')))

                    escola, created = Escola.objects.update_or_create(
                        id_escola=row['id_escola'],
                        defaults={
                            'nome': row['escola'],
                            'endereco': row['endereco'],
                            'turmas_matutino': row['turmas_matutino'],
                            'turmas_vespertino': row['turmas_vespertino'],
                            'status_matutino': status_matutino,
                            'status_vespertino': status_vespertino,
                        },
                    )
                    if created:
                        self.stdout.write(f"Nova escola adicionada: {escola.nome}")
                    else:
                        self.stdout.write(f"Escola atualizada: {escola.nome}")
        except FileNotFoundError:
            self.stderr.write("Erro: Arquivo escolas.csv não encontrado.")

