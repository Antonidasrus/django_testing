import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from enum import Enum

from news.models import Comment, News


class urls(Enum):
    DETAIL = 'news:detail'
    EDIT = 'news:edit'
    DELETE = 'news:delete'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор заметки')


@pytest.fixture
def visitor(django_user_model):
    return django_user_model.objects.create(username='Посетитель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def visitor_client(visitor, client):
    client.force_login(visitor)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def lots_of_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            text=f'Комментарий {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_for_news(news):
    return news.id,


@pytest.fixture
def get_detail_url(news):
    return reverse(urls.DETAIL.value, args=(news.id,))


@pytest.fixture
def get_edit_url(comment):
    return reverse(urls.EDIT.value, args=(comment.id,))


@pytest.fixture
def get_delete_url(comment):
    return reverse(urls.DELETE.value, args=(comment.id,))
