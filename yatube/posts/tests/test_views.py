# posts/tests/test_views.py
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile  # type: ignore
from django import forms  # type: ignore
from django.conf import settings  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase, override_settings  # type: ignore
from django.urls import reverse  # type: ignore

from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image='posts/small.gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.guest_client = Client()

        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.user)

        guest = self.guest_client
        authorized = self.authorized_client
        author = self.author_client

        Follow.objects.get_or_create(
            user=self.user,
            author=PostPagesTests.user
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.templates_pages = (
            {
                reverse('posts:index'):
                    {
                        'template': 'posts/index.html',
                        'page_data': {
                            'client': guest,
                            'object': 'page_obj',
                        },
                        'test_data':
                            {
                                'author': 'test-author',
                                'text': 'Тестовый текст',
                                'group': 'Тестовая группа',
                                'image': 'posts/small.gif',
                        }
                },
                reverse('posts:group', kwargs={'slug': 'test-slug'}):
                    {
                        'template': 'posts/group_list.html',
                        'page_data': {
                            'client': guest,
                            'object': 'page_obj',
                        },
                        'test_data':
                            {
                                'title': 'Тестовая группа',
                                'slug': 'test-slug',
                                'image': 'posts/small.gif',
                        }
                },
                reverse('posts:profile', kwargs={'username': 'test-author'}):
                    {
                        'template': 'posts/profile.html',
                        'page_data': {
                            'client': author,
                            'object': 'page_obj',
                        },
                        'test_data':
                            {
                                'author': 'test-author',
                                'text': 'Тестовый текст',
                                'group': 'Тестовая группа',
                                'image': 'posts/small.gif',
                        }
                },
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                    {
                        'template': 'posts/post_detail.html',
                        'page_data': {
                            'client': guest,
                            'object': 'post',
                        },
                        'test_data':
                            {
                                'author': 'test-author',
                                'text': 'Тестовый текст',
                                'group': 'Тестовая группа',
                                'image': 'posts/small.gif',
                        }
                },
                reverse('posts:post_create'):
                    {
                        'template': 'posts/create_post.html',
                        'page_data': {
                            'client': authorized,
                            'object': 'form',
                        },
                        'test_data':
                            {
                                'fields':
                                    {
                                        'text': forms.fields.CharField,
                                        'group': forms.fields.ChoiceField,
                                        'image': forms.fields.ImageField,
                                    }
                        }
                },
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                    {
                        'template': 'posts/create_post.html',
                        'page_data': {
                            'client': author,
                            'object': 'post',
                        },
                        'test_data':
                            {
                                'author': 'test-author',
                                'text': 'Тестовый текст',
                                'group': 'Тестовая группа',
                                'fields':
                                    {
                                        'text': forms.fields.CharField,
                                        'group': forms.fields.ChoiceField,
                                        'image': forms.fields.ImageField,
                                    }
                        }
                },
                reverse('posts:add_comment', kwargs={'post_id': self.post.id}):
                    {
                        'template': None,
                        'page_data': {
                            'client': authorized,
                            'object': None,
                        },
                        'test_data':
                            {
                                'text': 'Тестовый текст',
                                'fields':
                                    {
                                        'text': forms.fields.CharField,
                                    }
                        }
                },
                reverse('posts:follow_index'):
                    {
                        'template': 'posts/follow.html',
                        'page_data': {
                            'client': authorized,
                            'object': 'page_obj',
                        },
                        'test_data':
                            {
                                'author': 'test-author',
                                'text': 'Тестовый текст',
                                'group': 'Тестовая группа',
                                'image': 'posts/small.gif',
                        }
                },
            }
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, data in self.templates_pages.items():
            template = data['template']
            if template:
                with self.subTest(reverse_name=reverse_name):
                    response = data['page_data']['client'].get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        for reverse_name, data in self.templates_pages.items():
            if data['page_data']['object']:
                response = data['page_data']['client'].get(reverse_name)

                if data['page_data']['object'] == 'page_obj':
                    object = response.context[data['page_data']['object']][0]
                elif data['page_data']['object'] == 'post':
                    object = response.context[data['page_data']['object']]

                post_data = {
                    'author': object.author.username,
                    'text': object.text,
                    'group': object.group.title,
                    'slug': object.group.slug,
                    'title': object.group.title,
                    'image': object.image
                }
                if data['page_data']['object'] != 'form':
                    for key, expected_value in data['test_data'].items():
                        if key != 'fields':
                            self.assertEqual(post_data[key], expected_value)

            if data['test_data'].get('fields'):
                for value, expected in data['test_data']['fields'].items():
                    with self.subTest(value=value):
                        field = response.context.get('form').fields.get(value)
                        self.assertIsInstance(field, expected)

    def test_cache_index(self):
        """Проверка кэша для index."""
        index_url = reverse('posts:index')
        response = self.author_client.get(index_url)
        Post.objects.all().delete()
        self.assertEqual(
            response.content,
            self.author_client.get(index_url).content
        )

    def test_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        user = self.user
        author = PostPagesTests.user
        Follow.objects.get_or_create(user=user, author=author)
        self.assertTrue(Follow.objects.filter(user=user, author=author).all())
        Follow.objects.filter(user=user, author=author).delete()
        self.assertFalse(Follow.objects.filter(user=user, author=author).all())

    def test_follow_template_content(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        user = self.user
        user_other = User.objects.create_user(username='HasNoName_II')
        other_client = Client()
        other_client.force_login(user_other)
        author = PostPagesTests.user
        follow_index_url = reverse('posts:follow_index')
        Follow.objects.get_or_create(user=user, author=author)
        response = self.authorized_client.get(follow_index_url)
        response_other = other_client.get(follow_index_url)
        self.assertNotEqual(response, response_other)


class PaginatorViewsTest(TestCase):

    POST_ON_SECOND_PAGE = 1

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        Post.objects.bulk_create(
            Post(
                author=cls.user, text='Тестовый текст', group=cls.group
            ) for _ in range(
                settings.POSTS_PER_PAGE
                + PaginatorViewsTest.POST_ON_SECOND_PAGE
            )
        )

    def setUp(self):
        self.client = Client()

        self.test_pages = (
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        )

    def test_first_page_contains_right_records(self):
        """Проверка первой страницы паджинатора"""
        for adress in self.test_pages:
            response = self.client.get(adress)
            self.assertEqual(
                len(response.context['page_obj']),
                settings.POSTS_PER_PAGE
            )

    def test_second_page_contains_right_records(self):
        """Проверка второй страницы паджинатора"""
        for adress in self.test_pages:
            response = self.client.get(adress + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                PaginatorViewsTest.POST_ON_SECOND_PAGE
            )
