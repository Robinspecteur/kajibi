from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='accueil'),
    path('jeux/', views.jeux, name='jeux'),
    path('jeux/<int:page>/', views.jeux, name='jeux'),
    path('fiche/<int:game_id>/', views.fiche, name='fiche'),
    path('new_location/', views.new_location, name='new_location'),
    path('location/<int:location_id>/', views.location, name='location'),
    path('location/', views.location_list, name='location_list'),
    path('location/old/', views.old_location_list, name='old_location_list'),
    path('location/old/<int:page>/', views.old_location_list, name='old_location_list'),
    re_path(r'^game_autocomplete/$', views.GameAutocomplete.as_view(), name='game_autocomplete'),
    path('location/<int:location_id>/delete/', views.delete_location, name='delete_location'),
    path('location/<int:location_id>/finish/', views.finish_location, name='finish_location'),
    path('login/', views.connect, name='login'),
    path('logout/', views.deconnect, name='logout'),
]
