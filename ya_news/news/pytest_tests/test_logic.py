from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
FORM_DATA = {'text': COMMENT_TEXT}
NEW_COMMENT_TEXT = 'Новый текст комментария'
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, get_detail_url):
    url = get_detail_url
    client.post(url, FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, author, get_detail_url, news):
    url = get_detail_url
    response = author_client.post(url, FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, get_detail_url):
    url = get_detail_url
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, get_detail_url):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, f'{get_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(visitor_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = visitor_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, get_detail_url):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=NEW_FORM_DATA)
    assertRedirects(response, f'{get_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(visitor_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = visitor_client.post(url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
