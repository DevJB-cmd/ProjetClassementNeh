from django.db import models

class Groupe(models.Model):
    GENRE_CHOICES = [
        ('G', 'Garçon'),
        ('F', 'Fille'),
    ]
    nom = models.CharField(max_length=50, unique=True)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    taille_groupe = models.IntegerField()

    def __str__(self):
        return f"{self.nom} ({self.get_genre_display()}) - Taille: {self.taille_groupe}"

    @property
    def tailleactuelle(self):
        return self.etudiants.count()

class Etudiant(models.Model):
    GENRE_CHOICES = [
        ('G', 'Garçon'),
        ('F', 'Fille'),
    ]
    COHORTE_CHOICES = [
        ('1', '1ère cohorte'),
        ('2', '2ème cohorte'),
        ('3', '3ème cohorte'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    universite = models.CharField(max_length=100)
    cohorte = models.CharField(max_length=1, choices=COHORTE_CHOICES)

    # Lien vers le groupe (assignation automatique ou manuelle)
    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etudiants'
    )

    class Meta:
        unique_together = ('nom', 'prenom')

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.universite})"
