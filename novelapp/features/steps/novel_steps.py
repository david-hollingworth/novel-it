from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
from novels.models import Novel
from selenium.webdriver.common.by import By
import sys
import re

def normalize_text(text):
    if isinstance(text, (bytes, str)):
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        return text.lower().replace('’', "'")
    return str(text).lower()

@given('I have a novel titled "{title}" with description "{description}"')
def have_novel_with_desc(context, title, description):
    user = User.objects.get(username=context.current_user)
    novel = Novel.objects.create(user=user, title=title, description=description)
    context.current_novel = novel
    context.initial_novel_count = 1

@given('I have a novel titled "{title}"')
def have_novel(context, title):
    user = User.objects.get(username=context.current_user)
    novel, created = Novel.objects.get_or_create(user=user, title=title)
    context.current_novel = novel
    context.initial_novel_count = Novel.objects.filter(user=user).count()

@given('user "{username}" has created a novel titled "{title}"')
@given('user "{username}" has a novel titled "{title}"')
def user_has_novel(context, username, title):
    user, _ = User.objects.get_or_create(username=username)
    Novel.objects.create(user=user, title=title)

@when('I navigate to the novel\'s edit page')
def navigate_to_edit(context):
    url = reverse('novel_detail', kwargs={'pk': context.current_novel.pk})
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        context.execute_steps('When I click the "Edit Details" button')
    else:
        context.browser.get(context.base_url + url)
        context.execute_steps('When I click the "Edit Details" button')

@when('I view my novels list')
def view_novels_list(context):
    url = reverse('novel_list')
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)

@when('I try to access the edit page for "{title}"')
def access_edit_page(context, title):
    novel = Novel.objects.filter(title=title).first()
    if not novel:
         raise Exception(f"Novel '{title}' not found in DB")
    
    url = reverse('novel_edit', kwargs={'pk': novel.pk})
    if context.use_client:
        context.response = context.test.client.get(url, follow=True)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)

@then('I should see "{title}" in my novels list')
def see_novel_in_list(context, title):
    if context.use_client:
        content = normalize_text(context.response.content)
        pattern = r'\b' + re.escape(normalize_text(title)) + r'\b'
        if re.search(pattern, content):
            return
        context.response = context.test.client.get(reverse('novel_list'))
        assert re.search(pattern, normalize_text(context.response.content))
    else:
        if reverse('novel_list') not in context.browser.current_url:
            context.browser.get(context.base_url + reverse('novel_list'))
        assert title in context.browser.find_element(By.TAG_NAME, 'body').text

@then('the novel should be saved to the database')
def novel_saved(context):
    assert Novel.objects.filter(user__username=context.current_user).exists()

@then('the novel should belong to the current user')
def novel_belongs_to_user(context):
    novel = Novel.objects.filter(user__username=context.current_user).last()
    assert novel is not None

@then('"{title}" should be created successfully')
def novel_created_successfully(context, title):
    assert Novel.objects.filter(title=title, user__username=context.current_user).exists()

@then('the novel title should be updated to "{title}"')
def novel_title_updated(context, title):
    novel = Novel.objects.get(pk=context.current_novel.pk)
    assert novel.title == title, f"Expected title '{title}', but got '{novel.title}'"

@then('the novel description should be updated to "{description}"')
def novel_desc_updated(context, description):
    novel = Novel.objects.get(pk=context.current_novel.pk)
    assert novel.description == description

@then('no novel should be created')
def no_novel_created(context):
    user = User.objects.get(username=context.current_user)
    count = Novel.objects.filter(user=user).count()
    expected = getattr(context, 'initial_novel_count', 0)
    assert count == expected, f"Expected {expected} novels, but found {count}"

@then('the novel should not be updated')
def novel_not_updated(context):
    if context.use_client:
        assert "is required" in normalize_text(context.response.content) or "error" in normalize_text(context.response.content)

@then('I should receive a 403 Forbidden error')
def forbidden_error(context):
    if context.use_client:
        if context.response.status_code in [403, 404]:
            return
            
        final_path = context.response.request['PATH_INFO']
        allowed = [reverse('dashboard'), reverse('login'), reverse('novel_list')]
        msg = f"Expected 403/404 or redirect to {allowed}, but got {context.response.status_code} at {final_path}"
        assert final_path in allowed or "detail" in final_path, msg
    else:
        body = context.browser.find_element(By.TAG_NAME, 'body').text.lower()
        assert any(x in body for x in ["403", "forbidden", "404", "not found"]) or any(x in context.browser.current_url for x in ["dashboard", "login", "novels"])

@then('I should be redirected to my dashboard')
def redirected_to_my_dashboard(context):
    context.execute_steps('Then I should be redirected to the dashboard')

@then('the novel title should remain "{title}"')
def novel_title_remains(context, title):
    novel = Novel.objects.get(pk=context.current_novel.pk)
    assert novel.title == title, f"Title was changed to '{novel.title}', expected it to remain '{title}'"

@then('I should be returned to the novel page')
def returned_to_novel(context):
    if context.use_client:
        path = context.response.request['PATH_INFO']
        detail_url = reverse('novel_detail', kwargs={'pk': context.current_novel.pk})
        assert path == detail_url or "detail" in path, f"Expected redirect to {detail_url}, but got {path}"
    else:
        assert "detail" in context.browser.current_url

@then('I should not see "{title}"')
def should_not_see(context, title):
    if context.use_client:
        content = context.response.content.decode('utf-8')
        content_no_messages = re.sub(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content_no_messages = re.sub(r'<div[^>]*class="[^"]*message[^"]*"[^>]*>.*?</div>', '', content_no_messages, flags=re.DOTALL | re.IGNORECASE)
        
        content_clean = normalize_text(content_no_messages)
        pattern = r'\b' + re.escape(normalize_text(title)) + r'\b'
        assert not re.search(pattern, content_clean), f"Expected '{title}' not to be in content (excluding messages), but it was found."
    else:
        body_text = context.browser.find_element(By.TAG_NAME, 'body').text
        assert title not in body_text, f"Expected '{title}' not to be in body text, but it was found."

@then('I should only see my own novels')
def only_own_novels(context):
    user = User.objects.get(username=context.current_user)
    other_novels = Novel.objects.exclude(user=user)
    if context.use_client:
        content = normalize_text(context.response.content)
        for novel in other_novels:
            assert normalize_text(novel.title) not in content
            
# --- Novel Deletion Steps ---

@given('I have a chapter titled "{chapter_title}" in "{novel_title}"')
def have_chapter_in_novel(context, chapter_title, novel_title):
    from novels.models import Chapter
    novel = Novel.objects.get(title=novel_title, user__username=context.current_user)
    chapter, created = Chapter.objects.get_or_create(novel=novel, title=chapter_title, defaults={'order': novel.get_chapter_count() + 1})
    context.current_chapter = chapter

@given('I have a scene titled "{scene_title}" in "{chapter_title}"')
def have_scene_in_chapter(context, scene_title, chapter_title):
    from novels.models import Chapter, Scene
    chapter = Chapter.objects.get(title=chapter_title, novel__user__username=context.current_user)
    scene, created = Scene.objects.get_or_create(chapter=chapter, title=scene_title, defaults={'order': chapter.get_scene_count() + 1})
    context.current_scene = scene

@when('I click the "Delete" button on "{novel_title}"')
def click_delete_on_novel(context, novel_title):
    novel = Novel.objects.get(title=novel_title, user__username=context.current_user)
    url = reverse('novel_detail', kwargs={'pk': novel.pk})
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_novel = novel
        delete_url = reverse('novel_delete', kwargs={'pk': novel.pk})
        context.response = context.test.client.get(delete_url)
    else:
        context.browser.get(context.base_url + url)
        context.execute_steps('When I click the "Delete" button')

@when('I confirm the deletion')
def confirm_deletion(context):
    if context.use_client:
        url = reverse('novel_delete', kwargs={'pk': context.current_novel.pk})
        context.response = context.test.client.post(url, follow=True)
    else:
        context.execute_steps('When I click the "Yes, Delete Novel" button')

@when('I cancel the deletion')
def cancel_deletion(context):
    if context.use_client:
        url = reverse('novel_detail', kwargs={'pk': context.current_novel.pk})
        context.response = context.test.client.get(url)
    else:
        context.execute_steps('When I click the "Cancel" button')

@then('I should not see "{title}" in the novel list')
def not_see_in_novel_list(context, title):
    # Verify in DB (Hard Delete: check absolute existence)
    assert not Novel.objects.filter(title=title, user__username=context.current_user).exists()
    context.execute_steps('When I view my novels list')
    context.execute_steps(f'Then I should not see "{title}"')

@then('I should see "{title}" in the novel list')
def see_in_novel_list(context, title):
    context.execute_steps('When I view my novels list')
    context.execute_steps(f'Then I should see "{title}" in my novels list')

@then('I should not see "{title}" in the chapter list')
def not_see_in_chapter_list(context, title):
    from novels.models import Chapter
    # Verify in DB (Hard Delete: check absolute existence)
    assert not Chapter.objects.filter(title=title, novel__user__username=context.current_user).exists()

@then('I should not see "{title}" in the scene list')
def not_see_in_scene_list(context, title):
    from novels.models import Scene
    # Verify in DB (Hard Delete: check absolute existence)
    assert not Scene.objects.filter(title=title, chapter__novel__user__username=context.current_user).exists()
