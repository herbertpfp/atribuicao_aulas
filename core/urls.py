# /core/urls.py
# Este arquivo define as rotas (URLs) do sistema e conecta cada rota às views correspondentes.

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView  # Views genéricas de login/logout do Django
from . import views  # Importa as views criadas no arquivo views.py
from .views import atribuir_professor


urlpatterns = [
    path('', views.index, name='index'),  # Rota para a página inicial
    path('professor/', views.pagina_professor, name='pagina_professor'),  # Página do professor
    path('gestor/', views.pagina_gestor, name='pagina_gestor'),  # Página do gestor
    path('coletiva/', views.pagina_coletiva, name='pagina_coletiva'),  # Página coletiva
    path('cpf_invalido/', views.cpf_invalido, name='cpf_invalido'), #CPF inválido
    path('gestor/salvar_atribuicao/', views.salvar_atribuicao, name='salvar_atribuicao'), #Salvar atribuição
    path('gestor/deletar_atribuicao/', views.deletar_atribuicao, name='deletar_atribuicao'), #Deletar atribuição




    # URL para login
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),  # Tela de login
    # URL para logout
    path('logout/', views.custom_logout, name='logout'),  # Logout personalizado, Sair do sistema

    # Redirecionar /accounts/profile/ para /
    path('accounts/profile/', views.redirecionar_para_index),  # Redireciona para /
    
    #Atualizar dados
    path('professor/atualizar/', views.atualizar_professor, name='atualizar_professor'),  # Rota para salvar dados do professor
    
    #Atribuir desejo
    path('professor/atribuir/', atribuir_professor, name='atribuir_professor'),
    
    #Excluir desejo atribuição escola
     path('professor/remover_escolha/', views.remover_escolha, name='remover_escolha'),
     
     #URL página gestor
     path('gestor/', views.pagina_gestor, name='pagina_gestor'),


     
]

# Fim do arquivo urls.py

