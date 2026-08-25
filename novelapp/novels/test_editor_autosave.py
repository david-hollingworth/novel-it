"""
Playwright tests for autosave timing, converted from content/requirements/
03-writing-interface.md per data/requirements/phase-1-run-2-scope.yaml.
3 tests: T-FUNC-0302.01.01, T-FUNC-0302.01.02, T-PERF-0302.01.01.

Uses Playwright's clock-mocking API rather than real 30-second waits --
page.clock.install() must happen BEFORE navigation, since it needs to be in
place before editor.js's setInterval(..., 30000) is registered on page load.
That's why these tests build their own setup instead of using the shared
editor_page fixture (which navigates during fixture setup, too late to
install the clock first).
"""
import pytest
from django.urls import reverse

from .factories import NovelFactory, ChapterFactory, SceneFactory
from .models import Part


@pytest.fixture
def scene_setup(user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')
    return novel, part, chapter, scene


def goto_editor_with_clock_installed(page, live_server, novel, chapter, scene):
    url = reverse('scene_editor', kwargs={
        'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk})
    page.clock.install()
    # install() alone doesn't freeze time -- real wall-clock time (page load,
    # locator actions) keeps accumulating underneath until we explicitly
    # pause. Without this, boundary-precision assertions (e.g. "not yet at
    # 30s") can fail because real elapsed time plus a fast_forward() already
    # exceeds the interval, even though the fast_forward amount alone didn't.
    page.clock.pause_at('2027-01-01T00:00:00')
    page.goto(f"{live_server.url}{url}")


# T-FUNC-0302.01.01
@pytest.mark.trace("T-FUNC-0302.01.01")
@pytest.mark.django_db(transaction=True)
def test_editor_autosaves_after_changes_are_made(logged_in_browser, live_server, scene_setup):
    page = logged_in_browser
    novel, part, chapter, scene = scene_setup
    goto_editor_with_clock_installed(page, live_server, novel, chapter, scene)

    page.locator('#scene-editor').fill('one two three four five')

    save_url = reverse('scene_save', kwargs={
        'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk})
    with page.expect_response(lambda r: save_url in r.url):
        page.clock.fast_forward(30000)

    scene.refresh_from_db()
    assert scene.content == 'one two three four five'
    assert page.locator('#save-status').inner_text() == 'Saved'


# T-FUNC-0302.01.02
@pytest.mark.trace("T-FUNC-0302.01.02")
@pytest.mark.django_db(transaction=True)
def test_editor_does_not_autosave_when_no_changes_made(logged_in_browser, live_server, scene_setup):
    page = logged_in_browser
    novel, part, chapter, scene = scene_setup
    goto_editor_with_clock_installed(page, live_server, novel, chapter, scene)

    save_url = reverse('scene_save', kwargs={
        'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk})
    requests_seen = []
    page.on('request', lambda r: requests_seen.append(r.url) if save_url in r.url else None)

    page.clock.fast_forward(30000)
    page.wait_for_timeout(200)  # let any pending microtasks flush

    assert requests_seen == []


# T-PERF-0302.01.01
@pytest.mark.trace("T-PERF-0302.01.01")
@pytest.mark.django_db(transaction=True)
def test_default_autosave_interval_is_30_seconds(logged_in_browser, live_server, scene_setup):
    page = logged_in_browser
    novel, part, chapter, scene = scene_setup
    goto_editor_with_clock_installed(page, live_server, novel, chapter, scene)

    page.locator('#scene-editor').fill('one two three four five')

    save_url = reverse('scene_save', kwargs={
        'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk})
    requests_seen = []
    page.on('request', lambda r: requests_seen.append(r.url) if save_url in r.url else None)

    # Just under the interval: should not have fired yet
    page.clock.fast_forward(29999)
    page.wait_for_timeout(100)
    assert requests_seen == []

    # The remaining 1ms to reach exactly 30000ms: should fire now
    with page.expect_response(lambda r: save_url in r.url):
        page.clock.fast_forward(1)

    scene.refresh_from_db()
    assert scene.content == 'one two three four five'
