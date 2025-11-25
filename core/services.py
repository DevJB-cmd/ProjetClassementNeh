import re
from django.db import transaction, IntegrityError
from .models import Etudiant, Groupe

MAX_GROUPES_GARCONS = 13
MAX_GROUPES_FILLES = 12

def assigner_etudiant_a_groupe(etudiant_instance: Etudiant):
    """
    Assigne un étudiant à un groupe automatiquement en respectant :
    - max 13 groupes garçons, 12 groupes filles
    - max 2 étudiants de la même université et cohorte par groupe
    - parcours des groupes par ordre croissant
    - création d'un nouveau groupe si nécessaire
    """

    # 1️⃣ Vérifier doublon
    if Etudiant.objects.filter(
        nom__iexact=etudiant_instance.nom,
        prenom__iexact=etudiant_instance.prenom,
        universite__iexact=etudiant_instance.universite,
        cohorte=etudiant_instance.cohorte
    ).exclude(id=etudiant_instance.id).exists():
        raise ValueError("Cet étudiant est déjà classé dans un groupe.")

    genre = etudiant_instance.genre
    cohorte = etudiant_instance.cohorte
    universite = etudiant_instance.universite

    if genre == 'G':
        prefix = 'G'
        max_groupes = MAX_GROUPES_GARCONS
        taille_groupe = 30
    else:
        prefix = 'F'
        max_groupes = MAX_GROUPES_FILLES
        taille_groupe = 20

    # 2️⃣ Récupérer tous les groupes existants du genre et trier par numéro
    groupes_existants = list(Groupe.objects.filter(genre=genre))
    groupes_existants.sort(key=lambda g: int(re.search(r'_(\d+)$', g.nom).group(1)))

    # 3️⃣ Chercher un groupe compatible
    groupe_choisi = None
    for groupe in groupes_existants:
        # compter les étudiants même université + cohorte
        count_same = Etudiant.objects.filter(
            groupe=groupe,
            universite=universite,
            cohorte=cohorte
        ).count()

        if count_same >= 2:
            continue  # pas compatible

        # vérifier la taille totale
        if groupe.tailleactuelle >= taille_groupe:
            continue  # groupe plein

        # groupe compatible trouvé
        groupe_choisi = groupe
        break

    # 4️⃣ Si aucun groupe compatible, créer un nouveau groupe si possible
    if not groupe_choisi:
        # lister les numéros déjà utilisés
        numeros_existants = []
        for g in groupes_existants:
            m = re.search(r'_(\d+)$', g.nom)
            if m:
                numeros_existants.append(int(m.group(1)))

        # chercher le premier numéro libre
        for i in range(1, max_groupes + 1):
            if i not in numeros_existants:
                nouveau_nom = f"{prefix}_Groupe_{i}"
                try:
                    with transaction.atomic():
                        groupe_choisi = Groupe.objects.create(
                            nom=nouveau_nom,
                            genre=genre,
                            taille_groupe=taille_groupe
                        )
                        break
                except IntegrityError:
                    continue
        else:
            raise ValueError(
                f"Tous les groupes {prefix} sont remplis ou incompatibles pour cet étudiant."
            )

    # 5️⃣ Assigner l'étudiant
    etudiant_instance.groupe = groupe_choisi
    etudiant_instance.save()

    return groupe_choisi
