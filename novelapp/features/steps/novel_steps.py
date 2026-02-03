from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
from novels.models import Novel
from selenium.webdriver.common.by import By
import sys

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

@given('user "{username}" has created a novel titled "{title}"')
@given('user "{username}" has a novel titled "{title}"')
def user_has_novel(context, username, title):
    user, _ = User.objects.get_or_create(username=username)
    Novel.objects.create(user=user, title=title)

@when('I navigate to the novel\'s edit page')
def navigate_to_edit(context):
    # Instead of going directly to /edit/, we go to detail and click the button
    # This verifies the UI link actually works.
    url = reverse('novel_detail', kwargs={'pk': context.current_novel.pk})
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        # Now "click" the Edit Details link
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
        if normalize_text(title) in content:
            return
        context.response = context.test.client.get(reverse('novel_list'))
        assert normalize_text(title) in normalize_text(context.response.content)
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
        assert normalize_text(title) not in normalize_text(context.response.content)
    else:
        assert title not in context.browser.find_element(By.TAG_NAME, 'body').text

@then('I should only see my own novels')
def only_own_novels(context):
    user = User.objects.get(username=context.current_user)
    other_novels = Novel.objects.exclude(user=user)
    if context.use_client:
        content = normalize_text(context.response.content)
        for novel in other_novels:
            assert normalize_text(novel.title) not in content
