from behave import given, when, then
from behave.api.pending_step import StepNotImplementedError

from novelapp.novels.models import Chapter

# Scene creation steps
@given('the novel has a chapter titled "{title}"')
def novel_has_chapter(context, title):
    assert hasattr(context, 'current_novel'), "No novel found! Make sure you have a 'Given I have a novel...' step before this."
    
    # 1. Get the novel from context - what's it called?
    novel = context.current_novel
    
    # 2. You said order should always be 1
    order = 1
    
    # 3. Create the chapter
    chapter = Chapter.objects.create(
        title=title,
        novel=novel,
        order=order
    )
    
    # 4. Store in context - what should we call it?
    context.current_chapter = chapter

@given('I am viewing "{chapter}"')
def viewing_chapter(context, chapter):
    raise StepNotImplementedError(f'Given I am viewing "{chapter}"')

@then('the scene should be linked to "{chapter}"')
def scene_linked_to_chapter(context, chapter):
    raise StepNotImplementedError(f'Then the scene should be linked to "{chapter}"')

@then('no scene should be created')
def no_scene_created(context):
    raise StepNotImplementedError('Then no scene should be created')

@when('I create a scene titled "{title}"')
def create_scene(context, title):
    raise StepNotImplementedError(f'When I create a scene titled "{title}"')

@then('the scene should be a child of "{chapter}"')
def scene_child_of(context, chapter):
    raise StepNotImplementedError(f'Then the scene should be a child of "{chapter}"')

@then('the scene should only appear under "{chapter}"')
def scene_only_under(context, chapter):
    raise StepNotImplementedError(f'Then the scene should only appear under "{chapter}"')

@given('"{chapter}" has scenes:')
def chapter_has_scenes(context, chapter):
    raise StepNotImplementedError(f'Given "{chapter}" has scenes:')

@when('I create a new scene titled "{title}"')
def create_new_scene(context, title):
    raise StepNotImplementedError(f'When I create a new scene titled "{title}"')

@then('the scene order should be:')
def scene_order(context):
    raise StepNotImplementedError('Then the scene order should be:')

@when('I create scenes with titles:')
def create_multiple_scenes(context):
    raise StepNotImplementedError('When I create scenes with titles:')

@then('all 4 scenes should be created')
def four_scenes_created(context):
    raise StepNotImplementedError('Then all 4 scenes should be created')

@then('they should appear in the correct order')
def correct_order(context):
    raise StepNotImplementedError('Then they should appear in the correct order')

@given('I have a scene titled "{title}"')
def have_scene(context, title):
    raise StepNotImplementedError(f'Given I have a scene titled "{title}"')

@when('I navigate to the scene\'s page')
def navigate_to_scene(context):
    raise StepNotImplementedError('When I navigate to the scene\'s page')

# Scene status steps
@when('I change the status to "{status}"')
def change_status(context, status):
    raise StepNotImplementedError(f'When I change the status to "{status}"')

@when('I save the changes')
def save_changes(context):
    raise StepNotImplementedError('When I save the changes')

@then('the scene status should be "{status}"')
def scene_status_is(context, status):
    raise StepNotImplementedError(f'Then the scene status should be "{status}"')

@given('the scene status is "{status}"')
def scene_status_setup(context, status):
    raise StepNotImplementedError(f'Given the scene status is "{status}"')

@when('I write some content')
def write_content(context):
    raise StepNotImplementedError('When I write some content')

@then('the status progression should be recorded')
def status_progression_recorded(context):
    raise StepNotImplementedError('Then the status progression should be recorded')

@when('I view the chapter\'s scene cards')
def view_scene_cards(context):
    raise StepNotImplementedError('When I view the chapter\'s scene cards')

@then('the scene card should display "{status}"')
def scene_card_displays(context, status):
    raise StepNotImplementedError(f'Then the scene card should display "{status}"')

@then('the status should be visually distinct')
def status_visually_distinct(context):
    raise StepNotImplementedError('Then the status should be visually distinct')

@given('I have multiple scenes with different statuses:')
def multiple_scenes_statuses(context):
    raise StepNotImplementedError('Given I have multiple scenes with different statuses:')

@when('I filter by status "{status}"')
def filter_by_status(context, status):
    raise StepNotImplementedError(f'When I filter by status "{status}"')

@then('I should only see "{scene}"')
def only_see_scene(context, scene):
    raise StepNotImplementedError(f'Then I should only see "{scene}"')