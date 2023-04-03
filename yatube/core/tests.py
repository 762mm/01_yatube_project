from http import HTTPStatus

from django.test import TestCase  # type:ignore


class ViewTestClass(TestCase):

    def test_error_404_page(self):
        """Страница 404 отдаёт кастомный шаблон"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
