from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from kajibi.models import Game, Location
from kajibi.forms import LocationForm, LoginForm, SearchForm

from dal import autocomplete


def home(request):
    """ Index page """
    return render(request, 'kajibi/accueil.html')


def jeux(request, page=1):
    """ Liste de tous les jeux"""
    all_games = Game.objects.order_by('-nb_rented')

    query = request.GET.get("q")
    if query:
        all_games = all_games.filter(name__icontains=query)

    paginator = Paginator(all_games, 5)
    try:
        games = paginator.page(page)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)

    return render(request, 'kajibi/jeux.html', {'games': games})


def fiche(request, game_id):
    """Affiche la fiche d'un jeu"""
    # TODO il faut gérer le cas où le jeu n'existe pas
    game = Game.objects.get(id=game_id)
    return render(request, 'kajibi/fiche.html', {'game': game})


@login_required
def new_location(request):
    """Nouvelle location"""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location_object = form.save()
            location_object.rentor_first = request.user.username
            messages.success(request, 'La location n°' + str(location_object.id) + ' a bien été créée !')
            for game in location_object.rented_games.all():
                game.is_rented = True
                game.save()
            return redirect('location', location_id=location_object.id)
    else:
        form = LocationForm()
    return render(request, 'kajibi/new_location.html', {'form': form})


class GameAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #    return Game.objects.none()
        qs = Game.objects.filter(is_rented=False)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


@login_required
def location(request, location_id):
    """Affiche une location"""
    # TODO Gérer le cas où la location n'existe pas
    location_object = Location.objects.get(id=location_id)
    return render(request, "kajibi/location.html", {'location': location_object})


@login_required
def location_list(request):
    """Affiche toutes les locations en cours"""
    locations = Location.objects.order_by('-date_begin').filter(finished=False)
    return render(request, "kajibi/location_list.html", {'locations': locations})


@login_required
def old_location_list(request, page=1):
    """Affiche toutes les anciennes locations"""
    all_locations = Location.objects.order_by('-date_end').filter(finished=True)
    paginator = Paginator(all_locations, 20)

    try:
        locations = paginator.page(page)
    except EmptyPage:
        locations = paginator.page(paginator.num_pages)

    return render(request, "kajibi/old_location_list2.html", {'locations': locations})


@login_required
def delete_location(request, location_id):
    # TODO checker que user connecté
    location_object = get_object_or_404(Location, id=location_id)
    location_object.delete2()
    messages.success(request, "La location n°" + str(location_object.id) + " a bien été supprimée")
    return redirect('location_list')


@login_required
def finish_location(request, location_id):
    # TODO checker que user connecté
    location_object = get_object_or_404(Location, id=location_id)
    location_object.rentor_last = request.user.username
    location_object.finish()
    messages.success(request, "La location n°" + str(location_object.id) + " est bien finie")
    return redirect('location', location_id=location_id)


def connect(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                messages.success(request, "Bienvenue, " + username + " !")
                login(request, user)
                return redirect('accueil')
            else:
                messages.error(request, "Utilisateur ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'kajibi/login.html', {'form': form})


def deconnect(request):
    logout(request)
    return redirect('accueil')
