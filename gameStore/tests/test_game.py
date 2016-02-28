from django.test import TestCase, Client
from gameStore.models import Game, GameCategory
from django.contrib.auth.models import Group, User

class GameTestCase(TestCase):

    def setUp(self):

        self.client = Client()
        self.developer_group = Group.objects.create(name='Developer')

        self.first_developer = User.objects.create_user('first_developer')
        self.first_developer.groups.add(self.developer_group)
        self.second_developer = User.objects.create_user('second_developer')
        self.second_developer.groups.add(self.developer_group)

        self.game_category_action = GameCategory.objects.create(name='action')
        self.existing_game = Game.objects.create(name='Duke Nukem', price=25,
        URL='http://webcourse.cs.hut.fi/example_game.html',
        developer=self.first_developer)
        self.existing_game.categories.add(self.game_category_action)

        self.first_normal_user = User.objects.create_user('first_normal_user')
        self.first_normal_user.owned_games.add(self.existing_game)
        self.second_normal_user = User.objects.create_user('second_normal_user')

    def test_creating_new_game_as_developer(self):
        """
        Developers should be able to add games.
        Should return HTTP 302 - Moved.
        """
        create_game_data = {'name': 'Doom', 'price': 15,
        'URL': 'http://webcourse.cs.hut.fi/example_game.html',
        'description': 'Ya', 'developer': '1', 'categories': ['1'],
        'image': 'http://placehold.it/150x80?text=IMAGE'}

        games_in_database_before = Game.objects.count()
        self.client.force_login(self.first_developer)
        response = self.client.post('/games/create/', create_game_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(games_in_database_before + 1, Game.objects.count())

    def test_creating_new_game_as_normal_user(self):
        """
        Normal user should not be able to create games.
        Should return HTTP 403 - Forbidden.
        """
        create_game_data = {'name': 'Doom', 'price': '15',
        'URL': 'http://webcourse.cs.hut.fi/example_game.html',
        'description': 'Ya', 'developer': '3', 'categories': ['1'],
        'image': 'http://placehold.it/150x80?text=IMAGE'}

        self.client.force_login(self.first_normal_user)
        response = self.client.post('/games/create/', create_game_data)
        games_in_database_before = Game.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(games_in_database_before, Game.objects.count())

    def test_editing_game_as_games_developer(self):
        """
        Developer who created the game should be able to edit it.
        Should return HTTP 302 - Moved.
        """
        edit_game_data = {'name': 'Doom', 'price': '15',
        'URL': 'http://webcourse.cs.hut.fi/example_game.html',
        'description': 'Ya', 'developer': '1',  'categories': ['1'],
        'image': 'http://placehold.it/150x80?text=IMAGE'}

        self.client.force_login(self.first_developer)
        response = self.client.post('/games/1/edit/', edit_game_data)
        self.assertEqual(response.status_code, 302)

    def test_editing_game_as_different_developer(self):
        """
        Developer should not be able to edit different developers games.
        Should return HTTP 403 - Forbidden.
        """
        edit_game_data = {'name': 'Doom', 'price': '15',
        'URL': 'http://webcourse.cs.hut.fi/example_game.html',
        'description': 'Ya', 'developer': '2', 'categories': ['1'],
        'image': 'http://placehold.it/150x80?text=IMAGE',
        'categories': ['action']}

        self.client.force_login(self.second_developer)
        response = self.client.post('/games/1/edit/', edit_game_data)
        self.assertEqual(response.status_code, 403)

    def test_deleting_game_as_games_developer(self):
        """
        Developer should be able to remove a game added by himself.
        Should return HTTP 200 - OK.
        """
        self.client.force_login(self.first_developer)
        games_in_database_before = Game.objects.count()
        response = self.client.post('/games/1/delete/', {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(games_in_database_before - 1, Game.objects.count())

    def test_deleting_game_as_different_developer(self):
        """
        Developer should not be able to remove different developers games.
        Should return HTTP 403 - Forbidden.
        """
        self.client.force_login(self.second_developer)
        response = self.client.post('/games/1/delete/', {})
        self.assertEqual(response.status_code, 403)

    def test_playing_game_when_bought(self):
        """
        Normal user should be able to play games he has bought.´
        """
        self.client.force_login(self.first_normal_user)
        response = self.client.get('/games/1/')
        self.assertEqual(response.context['bought_game'], True)

    def test_playing_game_when_not_bought(self):
        """
        Normal user should not be able to play games he has not bought.
        """
        self.client.force_login(self.second_normal_user)
        response = self.client.get('/games/1/')
        self.assertEqual(response.context['bought_game'], False)

    def test_viewing_game_unauthenticated(self):
        """
        Unauthenticated users should be able to browse games.
        Should return HTTP 200 - OK.
        """
        response = self.client.get('/games/1/')
        self.assertEqual(response.status_code, 200)

    def test_viewing_game_normal_user(self):
        """
        Normal users should be able to browse games.
        Should return HTTP 200 - OK.
        """
        self.client.force_login(self.first_normal_user)
        response = self.client.get('/games/1/')
        self.assertEqual(response.status_code, 200)
