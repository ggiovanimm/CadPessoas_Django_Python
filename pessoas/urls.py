from django.urls import path
from . import views
from .views import render_pdf_view, gerar_pdf, export_csv

urlpatterns = [
    path('', views.pessoa_list, name='pessoa_list'),
    path('novo/', views.pessoa_create, name='pessoa_create'),
    path('editar/<int:pk>/', views.pessoa_update, name='pessoa_update'),
    path('deletar/<int:pk>/', views.pessoa_delete, name='pessoa_delete'),
    path('resumo/<int:pk>/', views.pessoa_resumo, name='pessoa_resumo'),
    path('pessoa/<int:pessoa_id>/pdf/', render_pdf_view, name='pessoa_pdf'),
    path('gerar_pdf/', gerar_pdf, name='gerar_pdf'),  # URL para gerar PDF
    path('export/csv/', export_csv, name='export_csv'),  # Nova URL para exportar CSV
]
