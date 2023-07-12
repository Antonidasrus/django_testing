"""
+- отдельная заметка передаётся на страницу со списком заметок в списке
  object_list в словаре context;
+- в список заметок одного пользователя не попадают заметки другого
  пользователя;
+- на страницы создания и редактирования заметки передаются формы.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.not_author = User.objects.create(username='Неавтор заметки')
        cls.notes = Note.objects.create(title='Заголовок', text='Текст',
                                        slug='1', author=cls.author)

    def test_object_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn('object_list', response.context)

    def test_add_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_author_not_author_notes(self):
        Note.objects.create(title='Заголовок', text='Текст',
                            slug='2', author=self.author)
        Note.objects.create(title='Заголовок', text='Текст',
                            slug='3', author=self.not_author)
        url = reverse('notes:list')
        self.client.force_login(self.not_author)
        response = self.client.get(url)
        self.assertNotEqual(response.context['user'], self.author)
