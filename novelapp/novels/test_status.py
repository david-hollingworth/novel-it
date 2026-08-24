"""
Backend/state tests for the manuscript-entity Status field (FEAT-0229),
converted from content/requirements/02-novel-management.md per
data/requirements/phase-1-run-2-scope.yaml.

Covers the "Status" sub-batch: T-FUNC-0229.01.01 through T-FUNC-0229.02.04
(8 tests) -- the final sub-batch for novel-management.

Note: the requirements doc's Gherkin writes the first status option as
"Not started" (lowercase s); the actual implementation's display label is
"Not Started" (MANUSCRIPT_STATUS_CHOICES in novels/models.py). This is a
cosmetic difference in the doc text, not a functional one, so labels are
compared against the real choices rather than the doc's exact casing.

Each test carries a @pytest.mark.trace(...) tag mapping it back to its
requirements-doc test ID -- see conftest.py for how this surfaces in -v
output, and data/requirements/phase-1-run-2-scope.yaml for the full scope.
"""
import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, ChapterFactory
from .models import Novel, Part, Chapter

EXPECTED_STATUS_LABELS = [
    'Not Started', 'Plotting', 'First Draft', 'First Review', 'Second Draft',
    'Second Review', 'Structural Edit', 'Final Edit', 'Beta Reading',
    'Publishing', 'Published',
]


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


def status_labels(form):
    return [label for _value, label in form.fields['status'].choices]


# T-FUNC-0229.01.01
@pytest.mark.trace("T-FUNC-0229.01.01")
@pytest.mark.django_db
def test_status_options_available_on_novel(auth_client):
    response = auth_client.get(reverse('novel_create'))
    assert status_labels(response.context['form']) == EXPECTED_STATUS_LABELS


# T-FUNC-0229.01.02
@pytest.mark.trace("T-FUNC-0229.01.02")
@pytest.mark.django_db
def test_status_options_available_on_part(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    response = auth_client.get(reverse('part_create', kwargs={'novel_pk': novel.pk}))
    assert status_labels(response.context['form']) == EXPECTED_STATUS_LABELS


# T-FUNC-0229.01.03
@pytest.mark.trace("T-FUNC-0229.01.03")
@pytest.mark.django_db
def test_status_options_available_on_chapter(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.get(reverse('chapter_create', kwargs={'novel_pk': novel.pk}))
    assert status_labels(response.context['form']) == EXPECTED_STATUS_LABELS


# T-FUNC-0229.01.04
@pytest.mark.trace("T-FUNC-0229.01.04")
@pytest.mark.django_db
def test_status_options_available_on_scene(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    response = auth_client.get(
        reverse('scene_create', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert status_labels(response.context['form']) == EXPECTED_STATUS_LABELS


# T-FUNC-0229.02.01
@pytest.mark.trace("T-FUNC-0229.02.01")
@pytest.mark.django_db
def test_status_defaults_to_not_started_on_novel(auth_client):
    response = auth_client.get(reverse('novel_create'))
    assert response.context['form']['status'].value() == 'not_started'


# T-FUNC-0229.02.02
@pytest.mark.trace("T-FUNC-0229.02.02")
@pytest.mark.django_db
def test_status_defaults_to_not_started_on_part(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    response = auth_client.get(reverse('part_create', kwargs={'novel_pk': novel.pk}))
    assert response.context['form']['status'].value() == 'not_started'


# T-FUNC-0229.02.03
@pytest.mark.trace("T-FUNC-0229.02.03")
@pytest.mark.django_db
def test_status_defaults_to_not_started_on_chapter(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.get(reverse('chapter_create', kwargs={'novel_pk': novel.pk}))
    assert response.context['form']['status'].value() == 'not_started'


# T-FUNC-0229.02.04
@pytest.mark.trace("T-FUNC-0229.02.04")
@pytest.mark.django_db
def test_status_defaults_to_not_started_on_scene(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    response = auth_client.get(
        reverse('scene_create', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert response.context['form']['status'].value() == 'not_started'
