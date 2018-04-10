from django.db import models
import datetime
from django.utils import timezone

GUARANTEES = (
    ('ID', 'Carte d\'identité'),
    ('ACCESS', 'Carte d\'accès'),
    ('DRIVER', 'Permis de conduire'),
    ('KEY', 'Clés'),
    ('MONEY', 'Cash : voir le montant en commentaire)'),
    ('Autre', 'Autre : voir en commentaire')
)


class Game(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nom du jeux")
    players_min = models.IntegerField(verbose_name="Nombre de joueurs minimum")
    players_max = models.IntegerField(verbose_name="Nombre de joueurs maximum")
    duration_min = models.IntegerField(verbose_name="Durée minimum")
    duration_max = models.IntegerField(verbose_name="Durée maximum")
    picture = models.ImageField(upload_to="photos/", verbose_name="Photo du jeux", null=True, blank=True)
    nb_rented = models.IntegerField(verbose_name="Nombre de fois loué", default=0)
    description = models.TextField(verbose_name="Description du jeu")
    comments = models.TextField(verbose_name="Commentaires", null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, verbose_name="Date d'ajout")
    is_rented = models.BooleanField(default=False, verbose_name="En cours de location", blank=True)

    def __str__(self):
        return self.name

    def duration(self):
        """Generate the duration string"""
        if self.duration_min == self.duration_max:
            return str(self.duration_min) + " minutes"
        else:
            return str(self.duration_min) + " à " + str(self.duration_max) + " minutes"

    def players(self):
        """Generate the number of players string"""
        if self.players_min == self.players_max:
            return str(self.players_min) + " joueurs"
        else:
            return str(self.players_min) + " à " + str(self.players_max) + " joueurs"

    class Meta:
        verbose_name = "Jeu"
        verbose_name_plural = "Jeux"


class Location(models.Model):
    date_begin = models.DateTimeField(default=timezone.now, verbose_name="Début de la location")
    expected_date_end = models.DateField(verbose_name="Fin prévue de la location")
    date_end = models.DateField(blank=True, null=True, verbose_name="Fin de la location")
    renter_first_name = models.CharField(max_length=20, verbose_name="Prénom du locataire")
    renter_last_name = models.CharField(max_length=20, verbose_name="Nom du locataire")
    renter_address = models.CharField(max_length=255, verbose_name="Adresse du locataire")
    renter_email = models.EmailField(verbose_name="E-mail du locataire")
    renter_phone = models.CharField(max_length=13, verbose_name="Numéro de téléphone du locataire")
    renter_guarantee = models.CharField(max_length=255, choices=GUARANTEES, verbose_name="Caution pour la location")
    renter_group = models.CharField(max_length=255, blank=True, null=True,
                                    verbose_name="Organisation du locataire (KAP, Cercle, Régio, etc.)")
    comments = models.TextField(blank=True, null=True, verbose_name="Commentaires")
    rented_games = models.ManyToManyField(Game, limit_choices_to={'is_rented': False})
    price = models.IntegerField(blank=True, null=True, verbose_name="Prix de la location")
    finished = models.BooleanField(default=False, verbose_name="Location finie")
    rentor_first = models.CharField(max_length=30, verbose_name="Reponsable sortie")
    rentor_last = models.CharField(max_length=30, verbose_name="Reponsable retour", null=True, blank=True)

    def finish(self):
        """Ends the location"""
        self.date_end = timezone.now()
        for game in self.rented_games.all():
            game.nb_rented += 1
            game.is_rented = False
            game.save()
        self.price = self.compute_price()
        self.finished = True
        self.save()

    def delete2(self):
        for game in self.rented_games.all():
            game.is_rented = False
            game.save()
        self.delete()

    def compute_price(self):
        """Computes the total price of the location, accounting for the number of games and the weekend"""
        # Removing the hours from the beginning and the end date (for example, a 23h rental should count as a full day)
        begin = datetime.date(self.date_begin.year, self.date_begin.month, self.date_begin.day)

        # Depending on whether the rental is late or not, and whether it is not over, we consider different end dates
        if self.finished:
            end = self.date_end
        elif not self.finished and self.is_late():
            end = datetime.date.today()
        elif not self.finished and not self.is_late():
            end = self.expected_date_end
        day = datetime.timedelta(days=1)
        price = 0
        i = 0
        while begin+i*day < end:
            price += self.rented_games.count()
            # The weekdays count as 1 day, whereas the week-end (friday->monday) counts as 1 day, so we skip it
            if 0 <= (begin+i*day).weekday() <= 3:
                i += 1
            elif (begin+i*day).weekday() == 4:
                i += 3
            elif (begin+i*day).weekday() == 5:
                i += 2
            else:
                i += 1
        return price

    def is_late(self):
        """Retourne vrai si la location est en retard (ou l'était si elle est finie)"""
        if self.finished:
            return self.expected_date_end < self.date_end
        else:
            return datetime.date.today() > self.expected_date_end

    def delay(self):
        """Retourne le nombre de jours de retard, 0 si pas de retard"""
        if not self.is_late:
            return 0
        else:
            if self.finished:
                return (self.date_end-self.expected_date_end).days
            else:
                return (datetime.date.today() - self.expected_date_end).days

    def number_of_games(self):
        """Retourne le nombre de jeux de cette location"""
        return self.rented_games.all().count()

    def __str__(self):
        return "Location n°" + str(self.id)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
