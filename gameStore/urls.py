"""gameStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^allauth/', include('allauth.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^games/$', views.browse_games, name="browse_games"),
    url(r'^games/my$', views.my_games, name="my_games"),
    url(r'^games/create/$', views.create_game, name="create_game"),
    url(r'^games/save/$', views.save_game, name="save_game"),
    url(r'^games/load/$', views.load_game, name="load_game"),
    url(r'^games/(?P<game_id>[0-9]+)/$', views.game, name="game"),
    url(r'^games/(?P<game_id>[0-9]+)/edit/$', views.edit_game, name="edit_game"),
    url(r'^games/(?P<game_id>[0-9]+)/delete/$', views.delete_game, name="delete_game"),
    url(r'^games/(?P<game_id>[0-9]+)/buy/$', views.payment_form, name="payment_form"),
    url(r'^games/(?P<game_id>[0-9]+)/r/$', views.payment_redirect, name="payment_redirect"),
    url(r'^games/(?P<category>[a-zA-Z]+)/$', views.browse_game_category, name='browse_game_category'),
    url(r'^highscores/$', views.browse_high_scores, name="high_scores"),
    url(r'^highscores/(?P<game_id>[0-9]+)/$', views.high_scores_for_game, name="high_scores_for_game"),
    url(r'^highscores/newScore/$', views.new_score, name="new_score"),
    url(r'^dashboard/$', views.developer_dashboard),
    url(r'^payment/$', views.payment_result, name="payment_result"),
    url(r'^', include('django.contrib.auth.urls')),
]
