from django.conf import settings  # type: ignore
from django.db import models  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='идентификатор'
    )
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Введите текст сообщения'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Укажите группу, к которой будет относиться сообщение'
    )

    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='картинка',
        help_text='Изображение'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'

    def __str__(self):
        return self.text[:settings.POSTS_TEXT_LEN]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='сообщение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата комментария'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique following'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='author not own follower'
            ),
        ]
