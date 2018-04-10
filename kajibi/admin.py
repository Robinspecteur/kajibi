from django.contrib import admin
from django.utils.text import Truncator

from kajibi.models import Game, Location


class GameAdmin(admin.ModelAdmin):
    list_display   = ('name', 'nb_rented')
    list_filter    = ('name',)
    date_hierarchy = 'date'
    ordering       = ('date', )
    search_fields  = ('name', )

    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('Général', {
            'classes': ['collapse', ],
            'fields': ('name', 'players_min', 'players_max', 'duration_min', 'duration_max', 'nb_rented', 'picture')
        }),
        # Fieldset 2 : game description
        ('Description du jeu', {
            'fields': ('description',)
        }),
        # Fieldset 3 : game comments
        ('Commentaire divers', {
            'description': 'Commentaires concernant l\'état du jeu, les pièces manquantes, etc.',
            'fields': ('comments',)
        }),
    )


admin.site.register(Game, GameAdmin)
admin.site.register(Location)
