"""
Playwright tests for the in-app navigation guard, converted from
content/requirements/03-writing-interface.md per
data/requirements/phase-1-run-2-scope.yaml. 4 tests.

This is the custom modal in scene_editor.html (#nav-guard-backdrop /
#nav-guard-cancel / #nav-guard-continue), driven by editor.isDirty() --
not editor.js's own beforeunload handler, which only covers true
browser-level navigation (closing the tab), explicitly out of scope per
the requirement's own note.
"""
import pytest
from django.urls import reverse


# T-USER-0303.01.01
@pytest.mark.trace("T-USER-0303.01.01")
@pytest.mark.django_db(transaction=True)
def test_confirmation_dialog_shown_with_unsaved_changes(editor_page):
    page = editor_page['page']
    novel, chapter = editor_page['novel'], editor_page['chapter']

    page.locator('#scene-editor').fill('some unsaved prose')
    chapter_url = reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    page.locator(f'a[href="{chapter_url}"]').first.click()

    backdrop = page.locator('#nav-guard-backdrop')
    assert backdrop.is_visible()
    assert page.locator('#nav-guard-cancel').is_visible()
    assert page.locator('#nav-guard-continue').is_visible()


# T-USER-0303.01.02
@pytest.mark.trace("T-USER-0303.01.02")
@pytest.mark.django_db(transaction=True)
def test_navigation_proceeds_when_continue_clicked(editor_page, live_server):
    page = editor_page['page']
    novel, chapter = editor_page['novel'], editor_page['chapter']

    page.locator('#scene-editor').fill('some unsaved prose')
    chapter_url = reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    page.locator(f'a[href="{chapter_url}"]').first.click()
    page.locator('#nav-guard-continue').click()

    page.wait_for_url(f"{live_server.url}{chapter_url}")
    assert chapter_url in page.url


# T-USER-0303.01.03
@pytest.mark.trace("T-USER-0303.01.03")
@pytest.mark.django_db(transaction=True)
def test_navigation_cancelled_when_cancel_clicked(editor_page):
    page = editor_page['page']
    novel, chapter = editor_page['novel'], editor_page['chapter']
    editor_url = page.url

    page.locator('#scene-editor').fill('some unsaved prose')
    chapter_url = reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    page.locator(f'a[href="{chapter_url}"]').first.click()
    page.locator('#nav-guard-cancel').click()

    assert not page.locator('#nav-guard-backdrop').is_visible()
    assert page.url == editor_url
    assert page.locator('#scene-editor').input_value() == 'some unsaved prose'


# T-USER-0303.01.04
@pytest.mark.trace("T-USER-0303.01.04")
@pytest.mark.django_db(transaction=True)
def test_no_confirmation_dialog_when_no_unsaved_changes(editor_page, live_server):
    page = editor_page['page']
    novel, chapter = editor_page['novel'], editor_page['chapter']

    chapter_url = reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    page.locator(f'a[href="{chapter_url}"]').first.click()

    page.wait_for_url(f"{live_server.url}{chapter_url}")
    assert chapter_url in page.url
