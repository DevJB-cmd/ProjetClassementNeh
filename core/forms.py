from django import forms
from .models import Etudiant, Groupe

class EtudiantForm(forms.ModelForm):
    groupe = forms.ModelChoiceField(
        queryset=Groupe.objects.all(),
        required=False,
        empty_label="Assignation automatique",
        help_text="Choisissez un groupe manuellement ou laissez vide pour assignation automatique"
    )

    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'genre', 'universite', 'cohorte', 'groupe']
