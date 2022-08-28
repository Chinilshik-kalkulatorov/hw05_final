from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов и шаблонов приложения About."""
        urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for url, template in urls.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)
