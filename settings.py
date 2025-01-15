# settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Aponta para o diretório global de templates
        'APP_DIRS': True,  # Permite buscar templates dentro das pastas de apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Redireciona após o login para a página index
LOGIN_REDIRECT_URL = '/'  # Certifique-se de que esta linha está presente

