"""
Playwright tests for distraction-free mode, converted from
content/requirements/03-writing-interface.md per
data/requirements/phase-1-run-2-scope.yaml. 2 tests.

Implemented in editor.js as toggleFullscreen() / the .ni-fullscreen CSS
class (position: fixed; inset: 0), not the browser's real Fullscreen API --
matches the requirement's own note that this "is not true fullscreen."
Checking is_visible() on the sidebar wouldn't actually prove anything here,
since it stays visible-but-occluded behind the fixed overlay; the real
signal is the editor container's class and its bounding box covering the
full viewport.
"""
import pytest


# T-FUNC-0306.01.01
@pytest.mark.trace("T-FUNC-0306.01.01")
@pytest.mark.django_db(transaction=True)
def test_enter_distraction_free_mode(editor_page):
    page = editor_page['page']
    editor = page.locator('.ni-editor')

    page.locator('button[title*="Toggle fullscreen"]').click()

    assert 'ni-fullscreen' in editor.get_attribute('class')
    box = editor.bounding_box()
    viewport = page.viewport_size
    assert box['width'] == viewport['width']
    assert box['height'] == viewport['height']


# T-FUNC-0306.01.02
@pytest.mark.trace("T-FUNC-0306.01.02")
@pytest.mark.django_db(transaction=True)
def test_exit_distraction_free_mode(editor_page):
    page = editor_page['page']
    editor = page.locator('.ni-editor')

    page.locator('button[title*="Toggle fullscreen"]').click()
    page.locator('button[title*="Toggle fullscreen"]').click()

    assert 'ni-fullscreen' not in editor.get_attribute('class')
    box = editor.bounding_box()
    viewport = page.viewport_size
    assert box['width'] < viewport['width'] or box['height'] < viewport['height']
