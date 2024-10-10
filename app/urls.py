# cadastro_pessoas/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pessoas.urls')),  # Incluindo as rotas do app 'cadastros'
]
