from django.shortcuts import get_object_or_404
from django.urls import reverse

from posts.models import Post
from posts.tests.fixtures.fixture_data import Settings


class PostFormTests(Settings):
    def setUp(self) -> None:
        # URLS для теста создания и редактирования поста
        self.PAGE_CREATE = reverse('posts:post_create')
        self.PAGE_CREATE_REDIRECT = reverse(
            'posts:profile', kwargs={'username': self.user})
        self.PAGE_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}
        )
        self.PAGE_EDIT_REDIRECT = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        )

    def test_post_create(self):
        """Валидная форма создает запись в Task."""
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        form_data = {'text': 'Тестовый пост из формы', 'group': self.group.id}
        response = self.authorized_client.post(
            self.PAGE_CREATE, data=form_data, follow=True
        )
        # Проверяем, что в БД добавилась запись
        self.assertEqual(Post.objects.count(), 1)
        # Проверяем, что редирект yes
        self.assertRedirects(response, self.PAGE_CREATE_REDIRECT)
        # Проверяем, что в базу добавилась запись с переданным контекстом
        self.assertTrue(Post.objects.filter(**form_data).exists())
        # Проверка создания поста под анонимом
        self.guest_client.post(
            self.PAGE_EDIT, data=form_data, follow=True
        )

    def test_form_fields_labels(self):
        """Проверка переопределенных  labels и help_texts в форме"""
        text_label = self.form.fields['text'].label
        group_label = self.form.fields['group'].label
        group_help_text = self.form.fields['group'].help_text
        self.assertEquals(text_label, 'Текст поста')
        self.assertEquals(group_label, 'Группа')
        self.assertEquals(
            group_help_text, 'Группа, к которой будет относиться пост')

    def test_post_edit(self):
        """Валидная форма со страницы редактирования поста сохраняет
        изменения"""
        form_data = {'text': 'Тестовый пост из формы', 'group': self.group.id}
        response = self.authorized_client.post(
            self.PAGE_EDIT, data=form_data, follow=True
        )
        # Проверка редиректа yes
        self.assertRedirects(response, self.PAGE_EDIT_REDIRECT)
        # Проверка, что пост с изменяемыми данными есть
        self.assertTrue(Post.objects.filter(**form_data).exists())
        # Проверка, что автор измененного поста...
        post = get_object_or_404(Post, pk=self.post.id)
        self.assertEquals(post.author, self.user)
        # Проверка перенаправления ...
        response2 = self.authorized_client2.get(
            self.PAGE_EDIT, data=form_data, follow=True
        )
        self.assertRedirects(response2, self.PAGE_EDIT_REDIRECT)
        # Проверка редактирования поста под анонимом
        self.guest_client.post(
            self.PAGE_EDIT, data=form_data, follow=True
        )
