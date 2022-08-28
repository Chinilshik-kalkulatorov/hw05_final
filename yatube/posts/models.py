from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
        blank=True,
        null=False,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    def __str__(self):
        return self.text[:15]

    def save(self, *args, **kwargs):
        if not self.text:
            self.text = None
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('posts:profile', kwargs={'username': self.author})


class Group(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    slug = models.SlugField(verbose_name="слаг", unique=True)
    description = models.TextField(
        verbose_name="дефиниция", blank=True, null=True)

    class Meta:
        verbose_name = "Новость сообщества"
        verbose_name_plural = "Новости сообщества"

    def __str__(self):
        return self.title
