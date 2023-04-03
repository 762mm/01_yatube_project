# posts/tests/tests_forms.py
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile  # type: ignore
from django.conf import settings  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase, override_settings  # type: ignore
from django.urls import reverse  # type: ignore

from posts.models import Comment, Post, Group


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
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
        self.author_client.force_login(PostCreateFormTests.user)

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group
        )

        self.post_detail_url = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response, reverse('posts:profile', args=('test-author',))
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=PostCreateFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """В форме редактируется запись."""
        group_new = Group.objects.create(
            title='Новая группа',
            slug='test-new-slug',
            description='Описание новой группы'
        )

        form_data = {
            'text': 'Новый текст записанный в форму',
            'group': group_new.id
        }

        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, self.post_detail_url)

        self.assertTrue(
            Post.objects.filter(
                text='Новый текст записанный в форму',
                group=group_new.id,
                author=PostCreateFormTests.user,
                pub_date=self.post.pub_date
            ).exists()
        )

    def test_comment_post(self):
        """Валидная форма создает комментарий в Post."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый комментарий',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(Post.objects.count(), comments_count + 1)
