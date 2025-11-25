import csv
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.http import HttpResponse
from datetime import datetime

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import EtudiantForm
from .services import assigner_etudiant_a_groupe
from .models import Groupe, Etudiant
from django.db.models import Count

# ==================== INSCRIPTION ====================
def inscription_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST)

        if form.is_valid():
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']

            # Vérifier si l’étudiant existe déjà
            if Etudiant.objects.filter(nom__iexact=nom, prenom__iexact=prenom).exists():
                messages.error(request, "Cet étudiant existe déjà dans le système.")
                return render(request, 'core/inscription_form.html', {'form': form})

            # Enregistrer l'étudiant avant assignation
            etudiant = form.save(commit=False)
            etudiant.save()

            # Assignation automatique au groupe
            groupe_final = assigner_etudiant_a_groupe(etudiant)

            messages.success(
                request,
                f"Inscription réussie ! Vous avez été automatiquement assigné au groupe : {groupe_final.nom}."
            )
            return redirect('inscription')

    else:
        form = EtudiantForm()

    return render(request, 'core/inscription_form.html', {'form': form})


# ==================== SUPPRESSION ÉTUDIANT ====================
def supprimer_etudiant(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    etudiant.delete()
    messages.success(request, "L'étudiant a été supprimé avec succès.")
    return redirect('admin_groupes')


# ==================== ADMIN GROUPES ====================
def vue_admin_groupes(request):
    groupes_avec_stats = Groupe.objects.annotate(
        count_etudiants=Count('etudiants')
    ).order_by('genre', 'nom')

    donnees_groupes = []
    for groupe in groupes_avec_stats:
        etudiants_du_groupe = Etudiant.objects.filter(groupe=groupe).order_by('universite')

        donnees_groupes.append({
            'groupe': groupe,
            'etudiants': etudiants_du_groupe,
            'taille_actuelle': groupe.etudiants.count(),
            'taille_max': groupe.taille_groupe,
            'pourcentage_rempli': (groupe.etudiants.count() / groupe.taille_groupe) * 100 if groupe.taille_groupe else 0,
        })

    return render(request, 'core/admin_groups.html', {'groupes': donnees_groupes})


# ==================== EXPORT CSV ====================
def exporter_groupes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="groupes_etudiants.csv"'

    writer = csv.writer(response)

    # En-têtes du fichier CSV
    writer.writerow(['Groupe', 'Nom', 'Prenom', 'Genre', 'Universite', 'Cohorte'])

    # Récupérer les étudiants assignés à un groupe
    etudiants_assignes = Etudiant.objects.filter(
        groupe__isnull=False
    ).select_related('groupe').order_by('groupe__nom')

    for etudiant in etudiants_assignes:
        writer.writerow([
            etudiant.groupe.nom,
            etudiant.nom,
            etudiant.prenom,
            etudiant.get_genre_display(),
            etudiant.universite,
            etudiant.get_cohorte_display(),   # <-- IMPORTANT
        ])

    return response


# ==================== EXPORT PDF ====================
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()

    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return None


def exporter_groupes_pdf(request):
    groupes_avec_stats = Groupe.objects.annotate(
        count_etudiants=Count('etudiants')
    ).order_by('genre', 'nom')

    donnees_groupes = []
    for groupe in groupes_avec_stats:
        etudiants_du_groupe = Etudiant.objects.filter(groupe=groupe).order_by('universite')

        donnees_groupes.append({
            'groupe': groupe,
            'etudiants': etudiants_du_groupe,
            'taille_actuelle': groupe.count_etudiants,
        })

    context = {
        'groupes': donnees_groupes,
        'date': f"Exporté le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    }

    pdf = render_to_pdf('core/export_groupes_pdf.html', context)

    if pdf:
        pdf['Content-Disposition'] = 'attachment; filename="Listes_Groupes_Session.pdf"'
        return pdf

    return HttpResponse("Erreur lors de la génération du PDF.", status=500)




def reassigner_etudiant(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)

    try:
        groupe_final = assigner_etudiant_a_groupe(etudiant)
        messages.success(
            request,
            f"L'étudiant {etudiant.nom} {etudiant.prenom} a été réassigné au groupe : {groupe_final.nom}."
        )
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('admin_groupes')