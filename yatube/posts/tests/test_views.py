from random import randint

from django.conf import settings
from django.core.paginator import Paginator
from django.test import Client, TestCase

from ..models import Group, Post
from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post
from .fixtures.fixture_data import Settings

User = get_user_model()


class PostViewsTests(Settings):

    def assert_post_is_the_same(self, post):
        """Сверка"""

        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.group.id, self.group.id)
        self.assertEqual(post.author.id, self.user.id)

    def setUp(self):
        self.TEMPLATES_PAGES_NAMES = {
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:home'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        self.TEMPLATES_PAGES_NAMES_CONTEXT = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:home'),
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        self.FORM_FIELDS = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        # URLS для теста контекста создания и редактирования поста
        self.PAGE_GROUP1 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.PAGE_GROUP2 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group2.slug})

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = self.TEMPLATES_PAGES_NAMES
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_group_list_profile_show_correct_context(self):
        """Шаблон home, group_list, profile сформирован с правильным
        контекстом."""

        for reverse_name in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assert_post_is_the_same(first_object)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))

        self.assert_post_is_the_same(response.context['post'])

    def test_edit_post_get_correct_contex(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = self.post
        page = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(page)
        self.assertEqual(response.context['form'].instance, post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Проверяем, что типы полей формы в словаре context работают
        for value, expected in self.FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_added_with_group_exists_on_pages(self):
        """Если при создании поста указать группу, то этот пост появляется
        на главной странице сайта, на странице выбранной группы, в профайле
        пользователя."""
        post2 = Post.objects.create(
            text='Пост из формы',
            author=self.user,
            group=self.group)
        for page in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            response = self.authorized_client.get(page).context['page_obj']
            self.assertIn(
                post2, response, f'поста {post2} нет на странице {page}'
            )

    def test_post_added_with_group_not_in_wrong_group(self):
        """Проверка, что созданный пост не попал в группу, для которой не был
        предназначен."""
        post2 = Post.objects.create(
            text='Пост из формы',
            author=self.user,
            group=self.group2)

        response = (
            self.authorized_client.get(self.PAGE_GROUP1).context['page_obj']
        )
        response2 = (
            self.authorized_client.get(self.PAGE_GROUP2).context['page_obj']
        )
        self.assertNotIn(
            post2, response, f'пост {post2} на странице "Тестовая группа"'
        )
        self.assertIn(
            post2, response2,
            f'поста {post2} нет на странице "Тестоваягруппа 2"'
        )


NUM_POSTS = randint(11, 19)
MODULO_POSTS = NUM_POSTS % settings.PER_PAGE_COUNT
ERROR_MSG = 'Количество постов не соответствует ожидаемому'


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.guest_client = Client()
        posts_list = [
            Post(text=f'Пост {i}', group=cls.group,
                 author=cls.user) for i in range(NUM_POSTS)
        ]
        posts = Post.objects.bulk_create(posts_list)
        cls.paginator = Paginator(posts, settings.PER_PAGE_COUNT)
        cls.TEMPLATES_PAGES_NAMES_CONTEXT = (
            reverse('posts:group_list', kwargs={
                'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user}),
            reverse('posts:home'),
        )

    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на страницах для не авторизованного
        пользователя."""

        self.assertTrue(NUM_POSTS > settings.PER_PAGE_COUNT,
                        'Недостаточно постов для проверки пагинации')
        self.assertTrue(self.paginator.num_pages == 2,
                        'Для проверки пагинации предоставлено больше двух '
                        'страниц')

        for reverse_name in self.TEMPLATES_PAGES_NAMES_CONTEXT:
            response_page_1 = self.guest_client.get(reverse_name)
            response_page_2 = self.guest_client.get(reverse_name + '?page=2')
            cnt1 = len(response_page_1.context['page_obj'])
            cnt2 = len(response_page_2.context['page_obj'])

            self.assertEqual(cnt1, settings.PER_PAGE_COUNT, ERROR_MSG)
            self.assertEqual(cnt2, MODULO_POSTS, ERROR_MSG)
