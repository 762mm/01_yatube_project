# Generated by Django 2.2.16 on 2023-02-27 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230227_1723'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-user',), 'verbose_name': 'подписка', 'verbose_name_plural': 'подписки'},
        ),
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
    ]