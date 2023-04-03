from http import HTTPStatus

from django.test import TestCase, Client  # type: ignore
from django.urls import reverse  # type: ignore


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница "Об авторе" не доступна любому пользователю.'
        )

        response = self.guest_client.get('/about/tech/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница "Технологии" не доступна любому пользователю.'
        )

    def test_about_templates(self):
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')


class AboutPagesTests(TestCase):

    def test_user_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages = {
            reverse('about:author'):
                'about/author.html',
            reverse('about:tech'):
                'about/tech.html',
        }

        for reverse_name, template in templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = Client().get(reverse_name)
                self.assertTemplateUsed(response, template)
