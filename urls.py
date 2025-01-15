from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Painel administrativo do Django
    path('', include('core.urls')),  # Inclui as rotas definidas em /core/urls.py
]

