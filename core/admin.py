# /core/admin.py
# Este arquivo registra os modelos no Django Admin para que possam ser gerenciados pela interface administrativa do Django.

from django.contrib import admin
from .models import Professor, Escola, Atribuicao, EscolhaProfessor

# Configuração da interface administrativa para o modelo Professor.
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id_sede', 'nome', 'cpf', 'cargo', 'pontuacao_peb', 'pontuacao_paeb')  # Colunas exibidas na lista de professores.
    search_fields = ('nome', 'cpf', 'id_sede__nome')  # Campos de busca para facilitar a localização de professores.
    list_filter = ('cargo',)  # Filtros laterais para organizar os professores.

# Configuração da interface administrativa para o modelo Escola.
@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('id_escola', 'nome', 'endereco', 'turmas_matutino', 'turmas_vespertino')  # Colunas exibidas na lista de escolas.
    search_fields = ('id_escola', 'nome', 'endereco')  # Campos de busca para localizar escolas rapidamente.
    # Removido list_filter para evitar erros com campos TextField.

# Configuração da interface administrativa para o modelo Atribuicao.
@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ('professor', 'escola', 'turma', 'disciplina', 'fora_de_campo')  # Colunas exibidas na lista de atribuições.
    search_fields = ('professor__nome', 'escola__nome', 'turma', 'disciplina')  # Campos de busca para localizar atribuições.
    list_filter = ('fora_de_campo',)  # Filtro para atribuições fora de campo.

# Configuração da interface administrativa para o modelo EscolhaProfessor.
@admin.register(EscolhaProfessor)
class EscolhaProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'escola', 'prioridade', 'periodo', 'data_escolha')  # Colunas exibidas na lista de escolhas.
    search_fields = ('professor__nome', 'escola__nome')  # Campos de busca.
    list_filter = ('periodo',)  # Filtros baseados no período.

# Fim do arquivo admin.py

