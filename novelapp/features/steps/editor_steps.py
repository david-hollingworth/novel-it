from behave import given, when, then
from behave.api.pending_step import StepNotImplementedError

# Autosave steps
@given('I am editing a scene')
def editing_scene(context):
    raise StepNotImplementedError('Given I am editing a scene')

@when('I type "{text}"')
def type_text(context, text):
    raise StepNotImplementedError(f'When I type "{text}"')

@when('I wait for 30 seconds')
def wait_30_seconds(context):
    raise StepNotImplementedError('When I wait for 30 seconds')

@then('the content should be automatically saved')
def content_autosaved(context):
    raise StepNotImplementedError('Then the content should be automatically saved')

@then('I should see a "Saved" indicator')
def see_saved_indicator(context):
    raise StepNotImplementedError('Then I should see a "Saved" indicator')

@when('I click outside the editor')
def click_outside_editor(context):
    raise StepNotImplementedError('When I click outside the editor')

@given('I am viewing the save status indicator')
def viewing_save_status(context):
    raise StepNotImplementedError('Given I am viewing the save status indicator')

@when('I type content')
def type_content(context):
    raise StepNotImplementedError('When I type content')

@then('the indicator should show "{status}"')
def indicator_shows(context, status):
    raise StepNotImplementedError(f'Then the indicator should show "{status}"')

@when('the save completes')
def save_completes(context):
    raise StepNotImplementedError('When the save completes')

@then('the timestamp should be updated')
def timestamp_updated(context):
    raise StepNotImplementedError('Then the timestamp should be updated')

@when('I wait for autosave to complete')
def wait_autosave(context):
    raise StepNotImplementedError('When I wait for autosave to complete')

@when('I refresh the page')
def refresh_page(context):
    raise StepNotImplementedError('When I refresh the page')

@then('the content should still be "{text}"')
def content_persists(context, text):
    raise StepNotImplementedError(f'Then the content should still be "{text}"')

@given('the server is unavailable')
def server_unavailable(context):
    raise StepNotImplementedError('Given the server is unavailable')

@when('autosave attempts to save')
def autosave_attempts(context):
    raise StepNotImplementedError('When autosave attempts to save')

@then('I should see an error indicator')
def see_error_indicator(context):
    raise StepNotImplementedError('Then I should see an error indicator')

@then('the content should remain in the editor')
def content_remains(context):
    raise StepNotImplementedError('Then the content should remain in the editor')

@then('autosave should retry after a delay')
def autosave_retries(context):
    raise StepNotImplementedError('Then autosave should retry after a delay')

@when('I immediately type "{text}"')
def immediately_type(context, text):
    raise StepNotImplementedError(f'When I immediately type "{text}"')

@then('only one save request should be made')
def one_save_request(context):
    raise StepNotImplementedError('Then only one save request should be made')

@then('all changes should be included')
def all_changes_included(context):
    raise StepNotImplementedError('Then all changes should be included')

# Markdown editor steps
@given('I am viewing a scene')
def viewing_scene(context):
    raise StepNotImplementedError('Given I am viewing a scene')

@then('I should see a CodeMirror editor')
def see_codemirror(context):
    raise StepNotImplementedError('Then I should see a CodeMirror editor')

@then('the editor should support markdown syntax highlighting')
def markdown_highlighting(context):
    raise StepNotImplementedError('Then the editor should support markdown syntax highlighting')

@when('I select the word "{word}"')
def select_word(context, word):
    raise StepNotImplementedError(f'When I select the word "{word}"')

@when('I press "{key}"')
def press_key(context, key):
    raise StepNotImplementedError(f'When I press "{key}"')

@then('the text should become "{text}"')
def text_becomes(context, text):
    raise StepNotImplementedError(f'Then the text should become "{text}"')

@then('the text should be highlighted as a heading')
def highlighted_as_heading(context):
    raise StepNotImplementedError('Then the text should be highlighted as a heading')

@when('I type a new line and enter "{text}"')
def type_new_line(context, text):
    raise StepNotImplementedError(f'When I type a new line and enter "{text}"')

@then('both should be highlighted appropriately')
def both_highlighted(context):
    raise StepNotImplementedError('Then both should be highlighted appropriately')

@when('I type:')
def type_multiline(context):
    raise StepNotImplementedError('When I type:')

@then('the editor should recognize it as a list')
def recognize_as_list(context):
    raise StepNotImplementedError('Then the editor should recognize it as a list')

@then('the formatting should be applied')
def formatting_applied(context):
    raise StepNotImplementedError('Then the formatting should be applied')

@then('the code block should be syntax highlighted')
def code_highlighted(context):
    raise StepNotImplementedError('Then the code block should be syntax highlighted')

@then('it should be recognized as a markdown link')
def recognized_as_link(context):
    raise StepNotImplementedError('Then it should be recognized as a markdown link')

@then('the link syntax should be highlighted')
def link_syntax_highlighted(context):
    raise StepNotImplementedError('Then the link syntax should be highlighted')