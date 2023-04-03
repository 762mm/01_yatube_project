# users/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase, Client  # type: ignore


User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

        guest = self.guest_client
        authorized = self.authorized_client
        self.test_urls = (
            (
                '/auth/logout/',
                guest,
                HTTPStatus.OK,
                'Страница выхода '
                'не доступна авторизованному пользователю.',
                'users/logged_out.html',
            ),
            (
                '/auth/signup/',
                guest,
                HTTPStatus.OK,
                'Страница входа '
                'не доступна любому пользователю.',
                None,
            ),
            (
                '/auth/login/',
                guest,
                HTTPStatus.OK,
                'Страница логина '
                'не доступна любому пользователю.',
                'users/login.html',
            ),
            (
                '/auth/password_change/',
                authorized,
                HTTPStatus.OK,
                'Страница смены пароля '
                'не доступна авторизованному пользователю.',
                'users/password_change_form.html',
            ),
            (
                '/auth/password_change/done/',
                authorized,
                HTTPStatus.OK,
                'Страница успешной смены пароля '
                'не доступна авторизованному пользователю.',
                'users/password_change_done.html',
            ),
            (
                '/auth/password_reset/',
                guest,
                HTTPStatus.OK,
                'Страница сброса пароля '
                'не доступна доступна любому пользователю.',
                'users/password_reset_form.html',
            ),
            (
                '/auth/password_reset/done/',
                guest,
                HTTPStatus.OK,
                'Cтраница успешного сброса пароля'
                'не доступна любому пользователю.',
                'users/password_reset_done.html',
            ),
            (
                '/auth/reset/<uidb64>/<token>/',
                guest,
                HTTPStatus.OK,
                'Cтраница подтверждения сброса пароля'
                'не доступна любому пользователю.',
                'users/password_reset_confirm.html',
            ),
            (
                '/auth/reset/done/',
                guest,
                HTTPStatus.OK,
                'Cтраница завершения успешного сброса пароля'
                'не доступна любому пользователю.',
                'users/password_reset_complete.html',
            ),
        )

    def test_users_urls_exists_at_desired_location(self):
        """Доступ к страницам аутентификации пользователей."""
        for url, user, exp_status, url_error_text, _ in self.test_urls:
            with self.subTest(url=url):
                self.assertEqual(
                    user.get(url).status_code,
                    exp_status,
                    url_error_text
                )

    def test_users_urls_templates(self):
        """Проверка шаблонов users-страниц."""
        for address, user, _, _, template in self.test_urls:
            if template:
                with self.subTest(address=address):
                    response = user.get(address)
                    self.assertTemplateUsed(response, template)

    def test_users_urls_redirect(self):
        """Проверка редиректа неавторизованного пользователя"""
        response = self.guest_client.get(
            '/auth/password_change/', follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/'
        )
