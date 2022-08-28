from django.contrib.auth import get_user_model

from .fixtures.fixture_data import Settings

User = get_user_model()


class PostModelTests(Settings):

    FIELD_VERBOSES = {
        'text': 'Текст поста',
        'pub_date': 'Дата публикации',
        'author': 'Автор',
        'group': 'Группа',
    }

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей Post и Group корректно работает __str__."""
        post = self.post
        group = self.group
        self.assertEquals(post.__str__(), post.text[:15])
        self.assertEquals(group.__str__(), group.title)

    def test_verbose_name(self):
        """Проверяем verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        for field, expected_value in self.FIELD_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Проверяем help_text в полях формы совпадает с ожидаемым."""
        post = self.post
        self.assertEqual(
            post._meta.get_field('group').help_text,
            'Группа, к которой будет относиться пост'
        )
