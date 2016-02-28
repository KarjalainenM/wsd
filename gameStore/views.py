
from .models import Game, GameCategory, Transaction, HighScore, Save
from .forms import PaymentForm, GameForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
import json
from django.conf import settings
import logging

def game(request, game_id):
    """
    View for a specific game. Description is accessible to all users, but
    only users who have bought the game and the developer should be able to
    access the actual game.
    """
    game = get_object_or_404(Game, pk=game_id)
    bought_game = False
    is_developer = False
    developed_game = False
    if request.user.is_authenticated():
        bought_game = request.user.owned_games.filter(pk=game.pk).exists()
        developed_game = request.user.developed_games.filter(pk=game.pk).exists()
        is_developer = request.user.groups.filter(name='Developer').exists()

    return render(request, 'game.html', {'user': request.user, 'game': game,
    'developed_game': developed_game, 'bought_game': bought_game,
    'is_developer': is_developer})


@login_required
def new_score(request):
    current_user = request.user
    current_game = Game.objects.get(name=request.POST.get('game'))
    if request.is_ajax():
        score = HighScore.objects.create(score=request.POST.get('score'), user=current_user, game=current_game)
        return HttpResponse("Success")


@login_required
def save_game(request):
    current_user = request.user
    current_game = Game.objects.get(name=request.POST.get('game'))
    if request.is_ajax():
        save = Save.objects.create(game_state=request.POST.get('state'), user=current_user, game=current_game)
        return HttpResponse("Success")


@login_required
def load_game(request):
    current_user = request.user
    current_game = Game.objects.get(name=request.GET['game'])
    if request.is_ajax():
        saves = Save.objects.filter(user=current_user, game=current_game).order_by('-created_at')
        if saves:
            data = {'found': 1, 'state': saves.first().game_state}
            json_data = json.dumps(data)
            return HttpResponse(json_data)
        else:
            data = {'found': 0}
            json_data = json.dumps(data)
            return HttpResponse(json_data)


@login_required
def create_game(request):
    """
    View for adding new games to the service. Either renders a form for adding
    a new game or processes a submitted one. Accessible only to users within
    the developer group.
    """
    is_developer = request.user.groups.filter(name='Developer').exists()
    # if this is a POST request we need to process the form data
    if is_developer:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            # check whether it's valid:
            form = GameForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/games/')
            else:
                return HttpResponse(status=400)

        # if a GET (or any other method) we'll create a blank form
        else:
            form = GameForm(initial={'developer': request.user})

        return render(request, 'create_game.html', {'form': form, 'is_developer': is_developer})
    else:
        return HttpResponseForbidden()

@login_required
def edit_game(request, game_id):
    """
    View for editing a given game after adding. Only accessible for the developer
    that originally created the game.
    """

    game = get_object_or_404(Game, pk=game_id)
    user_developed_this_game = request.user == game.developer

    if user_developed_this_game:
        if request.method == 'POST':
            form = GameForm(request.POST, instance=game)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/games/')
            else:
                return HttpResponse(status=400)

        else:
            form = GameForm(initial={'developer': game.developer, 'name': game.name,
                'price': game.price, 'URL': game.URL,
                'description': game.description, 'image': game.image})

        return render(request, 'edit_game.html', {'form': form,
            'user_developed_this_game': user_developed_this_game, 'game': game})
    else:
        return HttpResponseForbidden()

@login_required
def delete_game(request, game_id):
    """
    Deletes a specific game. Only accessible to developer that originally
    created the game.
    """
    game = get_object_or_404(Game, pk=game_id)
    user_developed_this_game = request.user == game.developer

    if user_developed_this_game:
        if request.method == 'POST':
            game.delete()
            return HttpResponseRedirect('/games/')
        else:
            return render(request, 'game_confirm_delete.html')
    else:
        return HttpResponseForbidden()

def browse_games(request):
    """
    Listing of all available games. Accessible also to unauthenticated users.
    """

    categories = GameCategory.objects.all()
    cheapest = Game.objects.all().order_by('-price').first()
    is_developer = request.user.groups.filter(name='Developer').exists()
    games = Game.objects.all()
    recent_games = Game.objects.all().order_by('-created')[:4]

    return render(request, 'browse_games.html', {'games': games,
                                                 'categories': categories, 'recent': recent_games, 'cheapest': cheapest})


def browse_game_category(request, category):
    """
    Browse games in a given category. Accessible also to unauthenticated users.
    """
    category = get_object_or_404(GameCategory, name=category.lower())
    games = Game.objects.filter(categories=category)

    return render(request, 'browse_game_category.html', {'games': games,
    'category': category})


@login_required
def my_games(request):
    """
    List games bought by and accessible to a single user.
    """
    is_developer = request.user.groups.filter(name='Developer').exists()
    if is_developer:
        return redirect(developer_dashboard)

    games = request.user.owned_games

    return render(request, 'my_games.html', {'user': request.user, 'games': games})


def browse_high_scores(request):
    """
    Listing of all high scores of all games. Accessible to all users.
    """
    high_scores = HighScore.objects.all()
    games = Game.objects.all()

    return render(request, 'browse_high_scores.html', {'high_scores': high_scores,
    'games': games})

def high_scores_for_game(request, game_id):
    """
    Listing of all high scores for a given game. Accessible to all users.
    """
    current_game = get_object_or_404(Game, pk=game_id)
    high_scores = HighScore.objects.all().filter(game=current_game)

    return render(request, 'high_scores_for_game.html', {'high_scores': high_scores, 'game': current_game})


@login_required
def payment_form(request, game_id):
    """
    Confirmation view for buying a game.
    """
    game = get_object_or_404(Game, pk=game_id)

    return render(request, 'payment_form.html', {'game': game})


@login_required
def payment_redirect(request, game_id):
    """
    Needed to create transaction in our system and to pass values to payment
    service when a user buys a given game.
    """
    game = get_object_or_404(Game, pk=game_id)
    owns_game = request.user.owned_games.filter(pk=game.pk)
    if owns_game:
        return redirect('game', game_id)
    else:
        transaction = Transaction.objects.create(game=game, price=game.price,
            payer=request.user, seller=game.developer)

        checksum = transaction.calculate_payment_checksum()

        form = PaymentForm(initial={'pid': transaction.pk, 'checksum': checksum,
            'amount': game.price, 'sid': settings.PAYMENT_SERVICE_SELLER_ID,
            'success_url': settings.PAYMENT_RESULT_URL,
            'cancel_url': settings.PAYMENT_RESULT_URL,
            'error_url': settings.PAYMENT_RESULT_URL})

        return render(request, 'payment_redirect.html', {'form': form})


def payment_result(request):
    """
    A view for handling user rights to a bought game after redirected from
    payment service.
    """
    result = request.GET['result']
    pid = request.GET['pid']
    ref = request.GET['ref']
    request_checksum = request.GET['checksum']

    #Ensure checksum is correct.
    checksum_string = "pid={}&ref={}&result={}&token={}".format(pid,
        ref, result, settings.PAYMENT_SERVICE_SECRET_KEY)

    from hashlib import md5
    calculated_checksum = md5(checksum_string.encode("ascii")).hexdigest()

    if result == 'success' and calculated_checksum == request_checksum:
        success = True
        transaction = get_object_or_404(Transaction, pk=pid)
        transaction.payer.owned_games.add(transaction.game)
    else:
        Transaction.objects.get(pk=pid).delete()
        success = False

    return render(request, 'payment_result.html', {'success': success})


def index(request):
    is_developer = request.user.groups.filter(name='Developer').exists()
    if is_developer:
        return redirect(developer_dashboard)
    elif request.user.is_authenticated():
        return redirect(my_games)
    else:
        return render(request, 'index.html')


@login_required
def developer_dashboard(request):
    """
    Default view for developers to manage their games.
    """
    is_developer = request.user.groups.filter(name='Developer').exists()

    if is_developer:
        return render(request, 'developer_dashboard.html', {'user': request.user,
                                                            'transactions': request.user.sold_transactions, 'games': request.user.developed_games})
    else:
        return HttpResponseForbidden()
