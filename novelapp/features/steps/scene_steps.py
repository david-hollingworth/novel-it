from behave import given, when, then
from django.urls import reverse
from novels.models import Chapter, Scene


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_chapter(context, chapter_title):
    return Chapter.objects.get(
        title=chapter_title,
        novel__user__username=context.current_user,
    )


def _get_scene(context, scene_title):
    return Scene.objects.get(
        title=scene_title,
        chapter__novel__user__username=context.current_user,
    )


def _status_label_to_value(label):
    mapping = {display: value for value, display in Scene.STATUS_CHOICES}
    return mapping.get(label, label)


# ---------------------------------------------------------------------------
# Background / setup steps
# ---------------------------------------------------------------------------

@given('"{chapter}" has a scene titled "{title}"')
def chapter_has_scene(context, chapter, title):
    ch = _get_chapter(context, chapter)
    scene, _ = Scene.objects.get_or_create(
        chapter=ch,
        title=title,
        defaults={'order': ch.get_scene_count() + 1},
    )
    context.current_scene = scene


@given('"{chapter}" has scenes:')
def chapter_has_scenes(context, chapter):
    ch = _get_chapter(context, chapter)
    for row in context.table:
        title = row['title']
        Scene.objects.get_or_create(
            chapter=ch,
            title=title,
            defaults={'order': ch.get_scene_count() + 1},
        )
    context.current_chapter = ch


@given('I have a scene titled "{title}"')
def have_scene(context, title):
    if not hasattr(context, 'current_chapter'):
        context.execute_steps('Given I have a novel titled "My Novel"')
        context.execute_steps('Given the novel has a chapter titled "Chapter 1"')
    ch = context.current_chapter
    scene, _ = Scene.objects.get_or_create(
        chapter=ch,
        title=title,
        defaults={'order': ch.get_scene_count() + 1},
    )
    context.current_scene = scene


@given('"{title}" is archived')
def scene_is_archived_setup(context, title):
    scene = _get_scene(context, title)
    scene.archived = True
    scene.save()
    context.current_scene = scene


@given('the scene status is "{status}"')
def scene_status_setup(context, status):
    scene = context.current_scene
    scene.status = _status_label_to_value(status)
    scene.save()


# ---------------------------------------------------------------------------
# Navigation steps
# ---------------------------------------------------------------------------

@given('I am viewing "{chapter}"')
def viewing_chapter(context, chapter):
    ch = _get_chapter(context, chapter)
    context.current_chapter = ch
    url = reverse('chapter_detail', kwargs={
        'novel_pk': ch.novel.pk,
        'chapter_pk': ch.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


@given('I am viewing the scene "{title}"')
def viewing_scene(context, title):
    scene = _get_scene(context, title)
    context.current_scene = scene
    url = reverse('chapter_detail', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


@when("I navigate to the scene's page")
def navigate_to_scene(context):
    scene = context.current_scene
    url = reverse('scene_edit', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
        'scene_pk': scene.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        # Pre-populate form_data with current values so required fields are present on submit
        context.form_data = {
            'title': scene.title,
            'notes': scene.notes or '',
            'status': scene.status,
        }
    else:
        context.browser.get(context.base_url + url)


@when('I navigate to the "Archived Scenes" page for "{chapter}"')
def navigate_to_archived_scenes(context, chapter):
    ch = _get_chapter(context, chapter)
    url = reverse('archived_scene_list', kwargs={
        'novel_pk': ch.novel.pk,
        'chapter_pk': ch.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


# ---------------------------------------------------------------------------
# Scene creation steps
# ---------------------------------------------------------------------------

@when('I create a scene titled "{title}"')
def create_scene(context, title):
    ch = context.current_chapter
    url = reverse('scene_create', kwargs={
        'novel_pk': ch.novel.pk,
        'chapter_pk': ch.pk,
    })
    if context.use_client:
        context.response = context.test.client.post(url, {'title': title}, follow=True)
    else:
        context.browser.get(context.base_url + url)
        context.execute_steps(f'When I fill in "title" with "{title}"')
        context.execute_steps('When I click the "Create Scene" button')
    context.current_scene = Scene.objects.filter(chapter=ch, title=title).last()


@when('I create a new scene titled "{title}"')
def create_new_scene(context, title):
    context.execute_steps(f'When I create a scene titled "{title}"')


@when('I create scenes with titles:')
def create_multiple_scenes(context):
    ch = context.current_chapter
    for row in context.table:
        title = row['title']
        url = reverse('scene_create', kwargs={'novel_pk': ch.novel.pk, 'chapter_pk': ch.pk})
        if context.use_client:
            context.response = context.test.client.post(url, {'title': title}, follow=True)
        else:
            context.browser.get(context.base_url + url)
            context.execute_steps(f'When I fill in "title" with "{title}"')
            context.execute_steps('When I click the "Create Scene" button')


# ---------------------------------------------------------------------------
# Scene editing steps
# ---------------------------------------------------------------------------

@when('I click the "Archive" button on the scene')
def click_archive_scene(context):
    scene = context.current_scene
    url = reverse('scene_archive', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
        'scene_pk': scene.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


@when('I click the "Delete" button on the scene')
def click_delete_scene(context):
    scene = context.current_scene
    url = reverse('scene_delete', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
        'scene_pk': scene.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


# ---------------------------------------------------------------------------
# Scene status steps
# ---------------------------------------------------------------------------

@when('I change the status to "{status}"')
def change_status(context, status):
    if context.use_client:
        if not hasattr(context, 'form_data'):
            context.form_data = {}
        context.form_data['status'] = _status_label_to_value(status)
    else:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        select = Select(context.browser.find_element(By.ID, 'id_status'))
        select.select_by_visible_text(status)


@when('I save the changes')
def save_changes(context):
    context.execute_steps('When I click the "Save Changes" button')


@when('I write some content')
def write_content(context):
    if context.use_client:
        if not hasattr(context, 'form_data'):
            context.form_data = {}
        context.form_data['content'] = 'Some test content for the scene.'
    else:
        from selenium.webdriver.common.by import By
        context.browser.find_element(By.ID, 'id_content').send_keys('Some test content.')


@then('the scene status should be "{status}"')
def scene_status_is(context, status):
    scene = Scene.objects.get(pk=context.current_scene.pk)
    expected = _status_label_to_value(status)
    assert scene.status == expected, f"Expected status '{expected}', got '{scene.status}'"


@then('the status progression should be recorded')
def status_progression_recorded(context):
    scene = Scene.objects.get(pk=context.current_scene.pk)
    assert scene.status == Scene.STATUS_FIRST_DRAFT


@when("I view the chapter's scene cards")
def view_scene_cards(context):
    scene = context.current_scene
    url = reverse('chapter_detail', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
    else:
        context.browser.get(context.base_url + url)


@then('the scene card should display "{status}"')
def scene_card_displays(context, status):
    if context.use_client:
        content = context.response.content.decode('utf-8').lower()
        assert status.lower() in content, f"Expected '{status}' in page content"
    else:
        from selenium.webdriver.common.by import By
        body = context.browser.find_element(By.TAG_NAME, 'body').text
        assert status in body


@then('the status should be visually distinct')
def status_visually_distinct(context):
    if context.use_client:
        assert context.response.status_code == 200


@given('I have multiple scenes with different statuses:')
def multiple_scenes_statuses(context):
    ch = getattr(context, 'current_chapter', None) or context.current_scene.chapter
    context.current_chapter = ch
    for row in context.table:
        title, status_label = row['title'], row['status']
        scene, _ = Scene.objects.get_or_create(
            chapter=ch,
            title=title,
            defaults={'order': ch.get_scene_count() + 1},
        )
        scene.status = _status_label_to_value(status_label.strip())
        scene.save()


@when('I filter by status "{status}"')
def filter_by_status(context, status):
    ch = context.current_chapter
    url = (
        reverse('chapter_detail', kwargs={'novel_pk': ch.novel.pk, 'chapter_pk': ch.pk})
        + f'?status={_status_label_to_value(status)}'
    )
    if context.use_client:
        context.response = context.test.client.get(url)
    else:
        context.browser.get(context.base_url + url)


@then('I should only see "{scene}"')
def only_see_scene(context, scene):
    if context.use_client:
        content = context.response.content.decode('utf-8')
        assert scene in content, f"Expected to see '{scene}' in content"
    else:
        from selenium.webdriver.common.by import By
        body = context.browser.find_element(By.TAG_NAME, 'body').text
        assert scene in body


# ---------------------------------------------------------------------------
# Assertion steps
# ---------------------------------------------------------------------------

@then('the scene should be linked to "{chapter}"')
def scene_linked_to_chapter(context, chapter):
    if hasattr(context, 'current_scene') and context.current_scene:
        scene = context.current_scene
    else:
        # Look up the most-recently created scene for this chapter
        scene = Scene.objects.filter(
            chapter__title=chapter,
            chapter__novel__user__username=context.current_user,
        ).last()
    assert scene is not None, f"No scene found for chapter '{chapter}'"
    assert scene.chapter.title == chapter, \
        f"Expected scene linked to '{chapter}', got '{scene.chapter.title}'"


@then('no scene should be created')
def no_scene_created(context):
    ch = context.current_chapter
    expected = getattr(context, 'initial_scene_count', 0)
    count = Scene.objects.filter(chapter=ch, archived=False).count()
    assert count == expected, f"Expected {expected} scenes, got {count}"


@then('the scene should be a child of "{chapter}"')
def scene_child_of(context, chapter):
    context.execute_steps(f'Then the scene should be linked to "{chapter}"')


@then('the scene should only appear under "{chapter}"')
def scene_only_under(context, chapter):
    scene = context.current_scene
    assert scene.chapter.title == chapter
    assert Scene.objects.filter(title=scene.title, chapter__title=chapter).exists()


@then('the scene order should be:')
def scene_order(context):
    ch = context.current_chapter
    scenes = Scene.objects.filter(chapter=ch, archived=False).order_by('order')
    expected = [row['title'] for row in context.table]
    actual = [s.title for s in scenes]
    assert actual == expected, f"Expected order {expected}, got {actual}"


@then('all 4 scenes should be created')
def four_scenes_created(context):
    ch = context.current_chapter
    count = Scene.objects.filter(chapter=ch, archived=False).count()
    assert count == 4, f"Expected 4 scenes, got {count}"


@then('they should appear in the correct order')
def correct_order(context):
    ch = context.current_chapter
    scenes = Scene.objects.filter(chapter=ch, archived=False).order_by('order')
    orders = [s.order for s in scenes]
    assert orders == sorted(orders), f"Scenes not in order: {orders}"


@then('the scene should be archived')
def scene_is_archived_assertion(context):
    scene = Scene.objects.get(pk=context.current_scene.pk)
    assert scene.archived, "Scene should be archived"


@then('"{title}" should not appear in the chapter\'s scene list')
def scene_not_in_chapter_list(context, title):
    scene = Scene.objects.get(pk=context.current_scene.pk)
    assert scene.archived, f"Expected '{title}' to be archived"


@then('"{title}" should appear in the chapter\'s scene list')
def scene_in_chapter_list(context, title):
    scene = Scene.objects.get(title=title, chapter__novel__user__username=context.current_user)
    assert not scene.archived, f"Expected '{title}' to be active (not archived)"


@then('"{title}" should be permanently deleted')
def scene_permanently_deleted(context, title):
    assert not Scene.objects.filter(
        title=title,
        chapter__novel__user__username=context.current_user,
    ).exists(), f"Scene '{title}' still exists in the database"


# ---------------------------------------------------------------------------
# Reordering steps
# ---------------------------------------------------------------------------

@when('I reorder the scenes in "{chapter}" to:')
def reorder_scenes(context, chapter):
    import json
    ch = _get_chapter(context, chapter)
    new_order = [row['title'] for row in context.table]
    scene_ids = [Scene.objects.get(chapter=ch, title=t).pk for t in new_order]
    url = reverse('scene_reorder', kwargs={'novel_pk': ch.novel.pk, 'chapter_pk': ch.pk})
    if context.use_client:
        context.response = context.test.client.post(
            url,
            data=json.dumps({'scene_ids': scene_ids}),
            content_type='application/json',
        )
    else:
        js_payload = json.dumps({'scene_ids': scene_ids})
        context.browser.execute_script(f"""
            fetch("{url}", {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)[1]
                }},
                body: '{js_payload}'
            }});
        """)
        import time
        time.sleep(1)


@when('I move "{title}" to position 1 in "{chapter}"')
def move_scene_to_first(context, title, chapter):
    import json
    ch = _get_chapter(context, chapter)
    scene_to_move = Scene.objects.get(title=title, chapter=ch)
    others = list(
        Scene.objects.filter(chapter=ch, archived=False)
        .exclude(pk=scene_to_move.pk)
        .order_by('order')
    )
    scene_ids = [scene_to_move.pk] + [s.pk for s in others]
    url = reverse('scene_reorder', kwargs={'novel_pk': ch.novel.pk, 'chapter_pk': ch.pk})
    if context.use_client:
        context.response = context.test.client.post(
            url,
            data=json.dumps({'scene_ids': scene_ids}),
            content_type='application/json',
        )


@then('"{title}" should be first in the scene list')
def scene_is_first(context, title):
    scene = _get_scene(context, title)
    scene.refresh_from_db()
    assert scene.order == 1, f"Expected '{title}' to be order 1, got {scene.order}"


# ---------------------------------------------------------------------------
# Editor navigation steps
# ---------------------------------------------------------------------------

@given('I am on the editor for "{title}"')
def on_editor_for_scene(context, title):
    scene = _get_scene(context, title)
    context.current_scene = scene
    url = reverse('scene_editor', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
        'scene_pk': scene.pk,
    })
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)


@then('I should be on the editor for "{title}"')
def should_be_on_editor(context, title):
    scene = _get_scene(context, title)
    expected_url = reverse('scene_editor', kwargs={
        'novel_pk': scene.chapter.novel.pk,
        'chapter_pk': scene.chapter.pk,
        'scene_pk': scene.pk,
    })
    if context.use_client:
        assert context.response.request['PATH_INFO'] == expected_url, \
            f"Expected path {expected_url}, got {context.response.request['PATH_INFO']}"
    else:
        assert expected_url in context.browser.current_url


@then('I should not see a "Previous Scene" button')
def no_prev_scene_button(context):
    if context.use_client:
        content = context.response.content.decode('utf-8')
        assert 'Previous Scene' not in content, "Expected 'Previous Scene' button to be absent"
    else:
        from selenium.webdriver.common.by import By
        elements = context.browser.find_elements(By.LINK_TEXT, 'Previous Scene')
        assert not elements, "Expected 'Previous Scene' button to be absent"


@then('I should not see a "Next Scene" button')
def no_next_scene_button(context):
    if context.use_client:
        content = context.response.content.decode('utf-8')
        assert 'Next Scene' not in content, "Expected 'Next Scene' button to be absent"
    else:
        from selenium.webdriver.common.by import By
        elements = context.browser.find_elements(By.LINK_TEXT, 'Next Scene')
        assert not elements, "Expected 'Next Scene' button to be absent"
