"""
+- Главная страница доступна анонимному пользователю.
+- Аутентифицированному пользователю доступна страница со списком заметок
  notes/, страница успешного добавления заметки done/, страница добавления
  новой заметки add/.
+- Страницы отдельной заметки,удаления и редактирования заметки доступны только
  автору заметки. Если на эти страницы попытается зайти другой пользователь —
  вернётся ошибка 404.
+- При попытке перейти на страницу списка заметок,страницу успешного добавления
  записи, страницу добавления заметки, отдельной заметки, редактирования или
  удаления заметки анонимный пользователь перенаправляется на страницу логина.
+- Страницы регистрации пользователей, входа в учётную запись и выхода из неё
  доступны всем пользователям.
"""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(title='Заголовок', text='Текст',
                                        slug='1', author=cls.author)

    def test_home_availibility_for_anonymous_user(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_availability_of_registration_for_all(self):
        for name in ('users:signup', 'users:login', 'users:logout'):
            url = reverse(name)
            response = self.client.get(url)
            assert response.status_code == HTTPStatus.OK

    def test_availability_for_auth_user(self):
        user = self.author
        status = HTTPStatus.OK
        self.client.force_login(user)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_for_author_only(self):
        user = self.author
        status = HTTPStatus.OK
        self.client.force_login(user)
        for name in ('notes:detail', 'notes:delete', 'notes:edit'):
            with self.subTest(user=user, name=name):
                url = reverse(name, args=(self.notes.pk,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.pk,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
