from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from .fixtures.fixture_data import Settings

User = get_user_model()


class StaticURLTests(TestCase):

    def test_homepage(self):
        # Создаем экземпляр клиента
        # Делаем запрос к глв стр
        response = self.client.get('/')
        # Утверждаем, что код должен быть равен 200
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(Settings):

    def setUp(self):
        self.POSTS_URLS = {
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/': 'posts/index.html',
        }
        self.POSTS_URLS_LOGIN_REQUIRED = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }

    def test_post_urls_exists_at_desired_location(self):
        """Проверяем урлы приложения Post на доступность и соответствие
        шаблонам"""

        for url, template in self.POSTS_URLS.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

        for url, template in self.POSTS_URLS_LOGIN_REQUIRED.items():
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_post_urls_not_exists_at_desired_location(self):
        """Проверяем обработку несуществующих урлов в приложении Post"""
        response = self.guest_client.get('/not_exists/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
