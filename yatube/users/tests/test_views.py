# users/tests/test_views.py
from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore


User = get_user_model()


class UsersPagesTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()

    def test_user_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages = {
            reverse('users:logout'):
                'users/logged_out.html',
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': 'uid', 'token': 'token'
                }
            ):
                'users/password_reset_confirm.html',
            reverse('password_reset_complete'):
                'users/password_reset_complete.html',

        }

        user = self.authorized_client
        for reverse_name, template in templates_pages.items():
            self.authorized_client.force_login(self.user)
            with self.subTest(reverse_name=reverse_name):
                response = user.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.authorized_client.logout()

    def test_signup_show_correct_context(self):
        """На страницу signup в контексте передаётся правильная форма."""
        response = self.authorized_client.get(reverse('users:signup'))
        object = response.context[0]
        self.assertIn('CreationForm', str(object))
