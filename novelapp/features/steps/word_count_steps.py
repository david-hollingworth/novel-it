from behave import given, when, then
from behave.api.pending_step import StepNotImplementedError

@given('I have a scene with content:')
def scene_with_content_table(context):
    raise StepNotImplementedError('Given I have a scene with content:')

@when('the word count is calculated')
def calculate_word_count(context):
    raise StepNotImplementedError('When the word count is calculated')

@then('the word count should be {count:d}')
def word_count_should_be(context, count):
    raise StepNotImplementedError(f'Then the word count should be {count}')

@then('markdown syntax should be excluded from the count')
def markdown_excluded(context):
    raise StepNotImplementedError('Then markdown syntax should be excluded from the count')

@then('the bold markers should not be counted')
def bold_not_counted(context):
    raise StepNotImplementedError('Then the bold markers should not be counted')

@given('I have a chapter with scenes:')
def chapter_with_scenes(context):
    raise StepNotImplementedError('Given I have a chapter with scenes:')

@when('I view the chapter')
def view_chapter(context):
    raise StepNotImplementedError('When I view the chapter')

@then('the chapter word count should be {count:d}')
def chapter_word_count(context, count):
    raise StepNotImplementedError(f'Then the chapter word count should be {count}')

@given('I have a novel with chapters:')
def novel_with_chapters(context):
    raise StepNotImplementedError('Given I have a novel with chapters:')

@when('I view the novel')
def view_novel(context):
    raise StepNotImplementedError('When I view the novel')

@then('the novel word count should be {count:d}')
def novel_word_count(context, count):
    raise StepNotImplementedError(f'Then the novel word count should be {count}')

@given('I am viewing a scene with {count:d} words')
def viewing_scene_with_words(context, count):
    raise StepNotImplementedError(f'Given I am viewing a scene with {count} words')

@then('I should see "{text}" displayed')
def see_text_displayed(context, text):
    raise StepNotImplementedError(f'Then I should see "{text}" displayed')

@given('I am viewing a chapter with {count:d} words')
def viewing_chapter_with_words(context, count):
    raise StepNotImplementedError(f'Given I am viewing a chapter with {count} words')

@given('I am viewing a novel with {count:d} words')
def viewing_novel_with_words(context, count):
    raise StepNotImplementedError(f'Given I am viewing a novel with {count} words')

@then('the word count should update to {count:d}')
def word_count_updates(context, count):
    raise StepNotImplementedError(f'Then the word count should update to {count}')

@when('I type more words')
def type_more_words(context):
    raise StepNotImplementedError('When I type more words')

@then('the word count should update immediately')
def word_count_immediate(context):
    raise StepNotImplementedError('Then the word count should update immediately')

@given('I have a scene with no content')
def scene_no_content(context):
    raise StepNotImplementedError('Given I have a scene with no content')

@given('I have a scene with content "{content}"')
def scene_with_content(context, content):
    raise StepNotImplementedError(f'Given I have a scene with content "{content}"')