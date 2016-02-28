from django.test import TestCase, Client
from django.contrib.auth.models import Group, User

class DashboardTestCase(TestCase):

    def setUp(self):

        self.client = Client()
        self.developer_group = Group.objects.create(name='Developer')

        self.first_developer = User.objects.create_user('first_developer')
        self.first_developer.groups.add(self.developer_group)

        self.first_normal_user = User.objects.create_user('first_normal_user')

    def test_access_to_dashboard_as_developer(self):
        """
        Developers should be able to access the dashboard.
        Should return HTTP 200 - OK.
        """

        self.client.force_login(self.first_developer)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_access_to_dashboard_as_normal_user(self):
        """
        Normal users should not be able to access the the dashboard.
        Should return HTTP 403 - Forbidden.
        """

        self.client.force_login(self.first_normal_user)
        response = self.client.post('/dashboard/')
        self.assertEqual(response.status_code, 403)
