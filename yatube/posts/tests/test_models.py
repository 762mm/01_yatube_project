# posts/tests/test_models.py
from django.conf import settings  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase  # type: ignore

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' + '!' * settings.POSTS_TEXT_LEN,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name = self.post.text[:settings.POSTS_TEXT_LEN]
        self.assertEqual(
            expected_object_name,
            str(self.post),
            'Некорректно работает __str__ у модели Post'
        )
        expected_object_name = self.group.title
        self.assertEqual(
            expected_object_name,
            str(self.group),
            'Некорректно работает __str__ у модели Group'
        )

    def test_models_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст сообщения',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                    f'verbose_name в поле "{field}" '
                    'модели "Post" не совпадает с ожидаемым'
                )

        field_verboses = {
            'title': 'Название группы',
            'slug': 'идентификатор',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value,
                    f'verbose_name в поле "{field}" '
                    'модели "Group" не совпадает с ожидаемым'
                )

    def test_models_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_helps = {
            'text': 'Введите текст сообщения',
            'group': 'Укажите группу, к которой будет относиться сообщение',
        }
        for field, expected_value in field_helps.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value,
                    f'help_text в поле "{field}" '
                    'модели "Post" не совпадает с ожидаемым'
                )
