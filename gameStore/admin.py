from django.contrib import admin

from .models import Game, HighScore, GameCategory, Transaction

admin.site.register(Game)
admin.site.register(GameCategory)
admin.site.register(Transaction)
admin.site.register(HighScore)
