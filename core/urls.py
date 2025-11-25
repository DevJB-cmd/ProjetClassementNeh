# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... (vos autres URLs)
    path('', views.inscription_etudiant, name='inscription'),
    path('admin-groupes/', views.vue_admin_groupes, name='admin_groupes'),
    path('export/csv/', views.exporter_groupes_csv, name='exporter_csv'),
    path('export/pdf/', views.exporter_groupes_pdf, name='exporter_pdf'),
    path('supprimer-etudiant/<int:etudiant_id>/', views.supprimer_etudiant, name='supprimer_etudiant'),
    path('reassigner_etudiant/<int:etudiant_id>/', views.reassigner_etudiant, name='reassigner_etudiant'),
]