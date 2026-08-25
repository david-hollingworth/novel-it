"""
Shared fixtures for the js_dependent Playwright tests (writing-interface
scenarios that need a real browser -- see data/requirements/
phase-1-run-2-scope.yaml). App-scoped conftest.py, only affects tests under
novels/.
"""
import pytest
from django.test import Client
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, ChapterFactory, SceneFactory
from .models import Part


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def logged_in_browser(page, live_server, user):
    """
    Authenticate via Django's test Client (fast, no UI interaction needed),
    then inject the resulting sessionid cookie into the Playwright browser
    context. Works because live_server and the test Client share the same
    test database, and Django's default session backend is DB-backed.
    """
    client = Client()
    client.force_login(user)
    session_cookie = client.cookies['sessionid']
    page.context.add_cookies([{
        'name': session_cookie.key,
        'value': session_cookie.value,
        'url': live_server.url,
    }])
    return page


@pytest.fixture
def editor_page(logged_in_browser, live_server, user):
    """
    Navigates to the scene editor for a fresh novel/chapter/scene (empty
    content, parts disabled). Returns a dict of the page and the model
    objects, since most tests need to assert against DB state afterward as
    well as the browser DOM.
    """
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')

    url = reverse('scene_editor', kwargs={
        'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk})
    logged_in_browser.goto(f"{live_server.url}{url}")

    return {
        'page': logged_in_browser,
        'novel': novel,
        'part': part,
        'chapter': chapter,
        'scene': scene,
    }
