from django.contrib import admin
from .models import Groupe, Etudiant

class EtudiantInline(admin.TabularInline):
    model = Etudiant
    extra = 0
    fields = ('prenom', 'nom', 'genre', 'universite', 'cohorte', 'groupe')
    readonly_fields = ('prenom', 'nom')

@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'genre', 'taille_groupe', 'tailleactuelle')
    list_filter = ('genre',)
    search_fields = ('nom',)
    inlines = [EtudiantInline]

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'genre', 'universite', 'cohorte', 'groupe')
    list_filter = ('genre', 'cohorte', 'groupe')
    search_fields = ('nom', 'prenom', 'universite')
    # Permettre l'édition directe du groupe
    autocomplete_fields = ['groupe']
