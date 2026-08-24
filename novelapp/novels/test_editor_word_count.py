"""
Playwright tests for live in-editor word count, converted from
content/requirements/03-writing-interface.md per
data/requirements/phase-1-run-2-scope.yaml. 2 tests.

Word count updates purely client-side (editor.js's triggerChange(), fired
on every textarea 'input' event) -- no network request involved, so these
assert on the #word-count DOM element directly rather than DB state.
"""
import pytest


# T-FUNC-0304.01.01
@pytest.mark.trace("T-FUNC-0304.01.01")
@pytest.mark.django_db(transaction=True)
def test_word_count_increases_as_text_is_added(editor_page):
    page = editor_page['page']
    textarea = page.locator('#scene-editor')
    word_count = page.locator('#word-count')

    assert word_count.inner_text() == '0'
    textarea.fill('one two three four five')
    assert word_count.inner_text() == '5'


# T-FUNC-0304.01.02
@pytest.mark.trace("T-FUNC-0304.01.02")
@pytest.mark.django_db(transaction=True)
def test_word_count_decreases_as_text_is_deleted(editor_page):
    page = editor_page['page']
    textarea = page.locator('#scene-editor')
    word_count = page.locator('#word-count')

    textarea.fill('one two three four five')
    assert word_count.inner_text() == '5'
    textarea.fill('one two three')
    assert word_count.inner_text() == '3'
