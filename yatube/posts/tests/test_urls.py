# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase, Client  # type: ignore

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
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
            group=cls.group
        )

    def setUp(self):

        self.guest_client = Client()

        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user)

        guest = self.guest_client
        authorized = self.authorized_client
        author = self.author_client
        self.test_urls = (
            (
                '/',
                guest,
                HTTPStatus.OK,
                'Главная страница '
                'не доступна любому пользователю.',
                'posts/index.html',
                None,
            ),
            (
                f'/group/{self.group.slug}/',
                guest,
                HTTPStatus.OK,
                'Страница группы '
                'не доступна любому пользователю.',
                'posts/group_list.html',
                None,
            ),
            (
                f'/profile/{self.user}/',
                guest,
                HTTPStatus.OK,
                'Страница профиля '
                'не доступна любому пользователю.',
                'posts/profile.html',
                None,
            ),
            (
                f'/posts/{self.post.id}/',
                guest,
                HTTPStatus.OK,
                'Страница поста '
                'не доступна любому пользователю.',
                'posts/post_detail.html',
                None,
            ),
            (
                f'/posts/{self.post.id}/edit/',
                author,
                HTTPStatus.OK,
                'Страница поста '
                'не доступна автору для редактирования.',
                'posts/create_post.html',
                {
                    authorized:
                        f'/posts/{self.post.id}/',
                    guest:
                        f'/auth/login/?next=/posts/{self.post.id}/edit/'
                },
            ),
            (
                '/create/',
                authorized,
                HTTPStatus.OK,
                'Страница создания поста '
                'не доступна авторизованному пользователю.',
                'posts/create_post.html',
                {
                    guest: '/auth/login/?next=/create/'
                },

            ),
            (
                f'/posts/{self.post.id}/comment/',
                guest,
                HTTPStatus.FOUND,
                'Неавторизованный пользователь '
                'может оставлять комментарии.',
                None,
                {
                    guest:
                    f'/auth/login/?next=/posts/{self.post.id}/comment/'
                },
            ),
            (
                '/follow/',
                authorized,
                HTTPStatus.OK,
                'Страница с подпиской'
                'не доступна авторизованному пользователю.',
                'posts/follow.html',
                None,
            ),
            (
                f'/profile/{PostURLTests.user}/follow/',
                authorized,
                HTTPStatus.FOUND,
                'Возможность подписаться на автора '
                'не доступна авторизованному пользователю.',
                None,
                {
                    authorized:
                    f'/profile/{PostURLTests.user}/',
                    guest:
                    f'/auth/login/?next=/profile/{PostURLTests.user}/follow/'
                },
            ),
            (
                f'/profile/{PostURLTests.user}/unfollow/',
                authorized,
                HTTPStatus.FOUND,
                'Возможность отписаться от автора '
                'не доступна авторизованному пользователю.',
                None,
                {
                    authorized:
                    f'/profile/{PostURLTests.user}/',
                    guest:
                    f'/auth/login/?next=/profile/{PostURLTests.user}/unfollow/'
                },
            ),
            (
                '/unexisting_page/',
                guest,
                HTTPStatus.NOT_FOUND,
                'Несуществующая страница '
                'почему-то доступна любому пользователю.',
                None,
                None,
            ),
        )

    def test_urls_exists_at_desired_location(self):
        """Доступ к страницам пользователей."""
        for url, user, exp_status, url_error_text, _, _ in self.test_urls:
            with self.subTest(url=url):
                self.assertEqual(
                    user.get(url).status_code,
                    exp_status,
                    url_error_text
                )

    def test_urls_templates(self):
        """Проверка шаблонов users-страниц."""
        for address, user, _, _, template, _ in self.test_urls:
            if template:
                with self.subTest(address=address):
                    response = user.get(address)
                    self.assertTemplateUsed(response, template)

    def test_urls_redirect_users(self):
        """Проверка редиректа пользователей"""
        for redirects in self.test_urls:
            if redirects[-1]:
                url = redirects[0]
                for user, redirect_url in redirects[-1].items():
                    response = user.get(url, follow=True)
                    self.assertRedirects(response, redirect_url)
