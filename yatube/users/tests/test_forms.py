# users/tests/tests_form.py
from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore


User = get_user_model()


class UserCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        """Валидная форма создает нового пользователя."""
        users_count = User.objects.count()

        form_data = {
            'first_name': 'Алексей',
            'last_name': 'Толстой',
            'username': 'red_graf',
            'email': 'red_graf@post.su',
            'password1': 'Rg_8283_AT',
            'password2': 'Rg_8283_AT',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))

        self.assertEqual(User.objects.count(), users_count + 1)
