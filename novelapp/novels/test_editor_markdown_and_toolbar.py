"""
Playwright tests for markdown preview rendering, the toolbar's heading
buttons, and the preview/edit toggle, converted from content/requirements/
03-writing-interface.md per data/requirements/phase-1-run-2-scope.yaml.
8 tests: T-FUNC-0301.01.01-04, T-UI-0301.01.01-02, T-FUNC-0305.01.01-02.

All markdown rendering happens client-side via marked.umd.js -- see
data/requirements/phase-1-run-2-scope.yaml's Known Gaps note on why these
were recategorised from backend_state to js_dependent.
"""
import pytest


def open_preview(page):
    page.locator('button[title*="Toggle preview"]').click()


# T-FUNC-0301.01.01
@pytest.mark.trace("T-FUNC-0301.01.01")
@pytest.mark.django_db(transaction=True)
def test_editor_renders_heading_elements(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill(
        '# H1\n\n## H2\n\n### H3\n\n#### H4\n\n##### H5\n\n###### H6')
    open_preview(page)
    preview = page.locator('.ni-preview-area')
    assert preview.locator('h1').inner_text() == 'H1'
    assert preview.locator('h2').inner_text() == 'H2'
    assert preview.locator('h3').inner_text() == 'H3'
    assert preview.locator('h4').inner_text() == 'H4'
    assert preview.locator('h5').inner_text() == 'H5'
    assert preview.locator('h6').inner_text() == 'H6'


# T-FUNC-0301.01.02
@pytest.mark.trace("T-FUNC-0301.01.02")
@pytest.mark.django_db(transaction=True)
def test_editor_renders_typography_elements(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill('**bold** *italic* ~~strikethrough~~')
    open_preview(page)
    preview = page.locator('.ni-preview-area')
    assert preview.locator('strong').inner_text() == 'bold'
    assert preview.locator('em').inner_text() == 'italic'
    assert preview.locator('s, del').inner_text() == 'strikethrough'


# T-FUNC-0301.01.03
@pytest.mark.trace("T-FUNC-0301.01.03")
@pytest.mark.django_db(transaction=True)
def test_editor_renders_list_elements(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill('- first\n- second\n\n1. one\n2. two')
    open_preview(page)
    preview = page.locator('.ni-preview-area')
    assert preview.locator('ul li').count() == 2
    assert preview.locator('ol li').count() == 2
    assert preview.locator('ul li').first.inner_text() == 'first'
    assert preview.locator('ol li').first.inner_text() == 'one'


# T-FUNC-0301.01.04
@pytest.mark.trace("T-FUNC-0301.01.04")
@pytest.mark.django_db(transaction=True)
def test_editor_renders_remaining_supported_elements(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill(
        '> a quote\n\n---\n\n[a link](https://example.com)\n\n'
        '![alt text](https://example.com/pic.png)\n\n`inline code`'
    )
    open_preview(page)
    preview = page.locator('.ni-preview-area')
    assert preview.locator('blockquote').inner_text() == 'a quote'
    assert preview.locator('hr').count() == 1
    link = preview.locator('a')
    assert link.get_attribute('href') == 'https://example.com'
    img = preview.locator('img')
    assert img.get_attribute('src') == 'https://example.com/pic.png'
    assert preview.locator('code').inner_text() == 'inline code'


# T-UI-0301.01.01
@pytest.mark.trace("T-UI-0301.01.01")
@pytest.mark.django_db(transaction=True)
def test_toolbar_provides_h1_h2_h3_shortcut_buttons(editor_page):
    page = editor_page['page']
    assert page.locator('button[title="Heading 1"]').count() == 1
    assert page.locator('button[title="Heading 2"]').count() == 1
    assert page.locator('button[title="Heading 3"]').count() == 1


# T-UI-0301.01.02
@pytest.mark.trace("T-UI-0301.01.02")
@pytest.mark.django_db(transaction=True)
def test_toolbar_does_not_provide_h4_h5_h6_shortcuts(editor_page):
    page = editor_page['page']
    assert page.locator('button[title="Heading 4"]').count() == 0
    assert page.locator('button[title="Heading 5"]').count() == 0
    assert page.locator('button[title="Heading 6"]').count() == 0


# T-FUNC-0305.01.01
@pytest.mark.trace("T-FUNC-0305.01.01")
@pytest.mark.django_db(transaction=True)
def test_switch_from_edit_to_preview_mode(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill('**bold text**')
    open_preview(page)

    assert page.locator('.ni-edit-area').is_hidden()
    assert page.locator('.ni-preview-area').is_visible()
    assert page.locator('.ni-preview-area strong').inner_text() == 'bold text'
    # Raw markdown syntax shouldn't be visible as literal text in the preview
    assert '**bold text**' not in page.locator('.ni-preview-area').inner_text()


# T-FUNC-0305.01.02
@pytest.mark.trace("T-FUNC-0305.01.02")
@pytest.mark.django_db(transaction=True)
def test_switch_from_preview_back_to_edit_mode(editor_page):
    page = editor_page['page']
    page.locator('#scene-editor').fill('**bold text**')
    open_preview(page)
    open_preview(page)  # toggle back

    assert page.locator('.ni-edit-area').is_visible()
    assert page.locator('.ni-preview-area').is_hidden()
    assert page.locator('#scene-editor').input_value() == '**bold text**'
