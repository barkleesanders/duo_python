from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings


@override_settings(DUO_IKEY='DI' + 'X' * 18, DUO_SKEY='0' * 40,
                   DUO_AKEY='1' * 40, DUO_HOST='api.example.invalid')
class AuthenticationCompatibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('synthetic-user', password='fixture-password')

    def primary_login(self):
        response = self.client.post('/accounts/login', {
            'username': 'synthetic-user', 'password': 'fixture-password'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get('/private/').status_code, 200)

    def test_anonymous_private_routes_require_primary_login(self):
        self.assertContains(self.client.get('/public/'), 'Public content.')
        for route in ['/private/', '/duo_private/', '/duo_private_manual/']:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/accounts/login'))

    def test_primary_login_keeps_secondary_challenge_and_renders_real_form(self):
        self.primary_login()
        response = self.client.get('/duo_private/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/duo_login'))
        response = self.client.get('/accounts/duo_login')
        self.assertContains(response, 'data-sig-request=')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_invalid_or_other_user_duo_response_never_grants_access(self):
        self.primary_login()
        for verified in [None, 'different-synthetic-user']:
            with patch('duo_web.verify_response', return_value=verified):
                response = self.client.post('/accounts/duo_login', {'sig_response': 'synthetic'})
            self.assertEqual(response.status_code, 302)
            self.assertNotIn('duo_authenticated', self.client.session)
            self.assertEqual(self.client.get('/duo_private/').status_code, 302)

    def test_matching_duo_user_and_local_redirect_then_logout(self):
        self.primary_login()
        with patch('duo_web.verify_response', return_value='synthetic-user'):
            response = self.client.post('/accounts/duo_login', {
                'sig_response': 'synthetic', 'next': '/duo_private/'})
        self.assertRedirects(response, '/duo_private/')
        self.assertContains(self.client.get('/duo_private/'), 'method="post"')
        self.assertEqual(self.client.get('/accounts/duo_logout/').status_code, 405)
        self.assertEqual(self.client.post('/accounts/duo_logout/').status_code, 200)
        self.assertNotIn('duo_authenticated', self.client.session)
        self.assertEqual(self.client.get('/duo_private/').status_code, 302)
        self.assertEqual(self.client.get('/accounts/logout/').status_code, 405)
        self.assertEqual(self.client.post('/accounts/logout/').status_code, 200)
        self.assertEqual(self.client.get('/private/').status_code, 302)

    def test_external_next_is_rejected(self):
        self.primary_login()
        with patch('duo_web.verify_response', return_value='synthetic-user'):
            response = self.client.post('/accounts/duo_login', {
                'sig_response': 'synthetic', 'next': 'https://example.invalid/external'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.url.startswith('http'))

    def test_secondary_login_and_logout_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/accounts/duo_login', {'sig_response': 'synthetic'}).status_code, 403)
        self.assertEqual(client.post('/accounts/duo_logout/').status_code, 403)
