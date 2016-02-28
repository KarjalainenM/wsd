from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, UserManager
import logging

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()


class GameCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    URL = models.URLField()
    image = models.URLField(default='http://placehold.it/150x80?text=IMAGE')
    description = models.CharField(max_length=2000, default="No description.")
    categories = models.ManyToManyField(GameCategory, related_name="games")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    developer = models.ForeignKey('auth.User', related_name="developed_games")
    users = models.ManyToManyField(User, related_name="owned_games", default=None, blank=True)

    def __str__(self):
        return self.name


class Save(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="saves", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="saves", on_delete=models.CASCADE)
    game_state = models.CharField(max_length=255)


class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()
    game = models.ForeignKey(Game)
    payer = models.ForeignKey(User, related_name="bought_transactions", on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name="sold_transactions", on_delete=models.CASCADE)

    class Meta:
        get_latest_by = 'created_at'

    def calculate_payment_checksum(self):
        checksum_string = "pid={}&sid={}&amount={}&token={}".format(self.pk,
            settings.PAYMENT_SERVICE_SELLER_ID, self.price,
            settings.PAYMENT_SERVICE_SECRET_KEY)

        from hashlib import md5
        m = md5(checksum_string.encode("ascii"))
        return m.hexdigest()


class HighScore(models.Model):
    score = models.IntegerField()
    user = models.ForeignKey(User, related_name="scores", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="scores", on_delete=models.CASCADE)

    def __str__(self):
        return self.game.name
