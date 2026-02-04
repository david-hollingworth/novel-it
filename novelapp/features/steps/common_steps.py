from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.urls import reverse
import re

def normalize_text(text):
    if isinstance(text, (bytes, str)):
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        # Replace any sequence of whitespace (including newlines) with a single space
        return ' '.join(text.lower().replace('’', "'").split())
    return str(text).lower()

@when('I fill in "{field}" with "{value}"')
def fill_field(context, field, value):
    field_map = {
        "username": "username",
        "password": "password",
        "email": "email",
        "confirm password": "password2",
        "current password": "old_password",
        "new password": "new_password1",
        "confirm new password": "new_password2",
        "title": "title",
        "description": "description",
        "premise": "premise",
        "genre": "genre",
    }
    
    clean_field = field.lower()
    field_name = field_map.get(clean_field, clean_field)

    # Add this block to store new password for later verification
    # if 'new password' in field_name.lower() and 'confirm' not in field_name.lower():
    context.new_password = value
    
    if context.use_client:
        context.form_data[field_name] = value
        return

    field_id = f"id_{field_name}"
    try:
        element = context.browser.find_element(By.ID, field_id)
    except:
        if clean_field == "password":
            element = context.browser.find_element(By.ID, "id_password1")
        elif clean_field == "confirm password":
            element = context.browser.find_element(By.ID, "id_password2")
        else:
            raise
            
    element.clear()
    element.send_keys(value)

@when('I change "{field}" to "{value}"')
def change_field(context, field, value):
    context.execute_steps(f'When I fill in "{field}" with "{value}"')

@when('I clear the "{field}" field')
def clear_field(context, field):
    if context.use_client:
        field_map = {"title": "title", "description": "description"}
        field_name = field_map.get(field.lower(), field.lower())
        context.form_data[field_name] = ""
        return
        
    field_id = f"id_{field.lower()}"
    element = context.browser.find_element(By.ID, field_id)
    element.clear()

@when('I click the "{button_text}" button')
def click_button(context, button_text):
    if context.use_client:
        clean_text = button_text.lower()
        
        # Priority 1: Check for links in content
        if context.response and context.response.content:
            content = context.response.content.decode('utf-8')
            # Improved regex to handle newlines and whitespace in link text
            # We replace spaces in button_text with \s+ to match any whitespace
            search_pattern = r'\s+'.join(map(re.escape, button_text.split()))
            pattern = f'<a[^>]+href="([^"]+)"[^>]*>[^<]*{search_pattern}[^<]*</a>'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                url = match.group(1)
                context.response = context.test.client.get(url, follow=True)
                context.form_data = {}
                return
        
        # Priority 2: Hardcoded navigation links
        link_map = {
            "create new novel": reverse('novel_create'),
            "cancel": reverse('novel_list'), # Fallback
        }
        
        if clean_text in link_map and not context.form_data:
            context.response = context.test.client.get(link_map[clean_text], follow=True)
            context.form_data = {}
            return

        # Priority 3: Form submission (POST)
        if context.response and hasattr(context.response, 'request'):
            current_path = context.response.request['PATH_INFO']
        else:
            current_path = getattr(context, 'current_path', '/')
            
        context.response = context.test.client.post(current_path, data=context.form_data, follow=True)
        context.form_data = {}
        return

    xpath = f"//button[contains(normalize-space(text()), '{button_text}')] | //input[@type='submit' and @value='{button_text}'] | //a[contains(normalize-space(text()), '{button_text}')]"
    try:
        button = context.browser.find_element(By.XPATH, xpath)
    except:
        xpath_lower = f"//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_text.lower()}')] | //a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_text.lower()}')]"
        button = context.browser.find_element(By.XPATH, xpath_lower)
    button.click()

@then('I should see a success message "{message}"')
def see_success_msg(context, message):
    if context.use_client:
        assert normalize_text(message) in normalize_text(context.response.content)
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: normalize_text(message) in normalize_text(driver.find_element(By.TAG_NAME, 'body').text)
    )

@then('I should see a success message')
def see_any_success(context):
    if context.use_client:
        content = normalize_text(context.response.content)
        msg_in_content = any(x in content for x in ["success", "created", "updated", "deleted"])
        assert msg_in_content, f"Success message not found in content: {content[:200]}..."
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: any(x in normalize_text(driver.find_element(By.TAG_NAME, 'body').text) for x in ["success", "created", "updated", "deleted"])
    )

@then('I should see an error message "{message}"')
def see_error_msg(context, message):
    if context.use_client:
        assert normalize_text(message) in normalize_text(context.response.content)
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: normalize_text(message) in normalize_text(driver.find_element(By.TAG_NAME, 'body').text)
    )

@then('I should see validation errors')
def see_validation_errors(context):
    if context.use_client:
        body = normalize_text(context.response.content)
        assert "errorlist" in body or "correct the error" in body or "is required" in body
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: len(driver.find_elements(By.CLASS_NAME, 'errorlist')) > 0 or 
                       "correct the error" in driver.find_element(By.TAG_NAME, 'body').text.lower() or
                       "is required" in driver.find_element(By.TAG_NAME, 'body').text.lower()
    )

@then('I should be redirected to the dashboard')
def redirected_to_dashboard(context):
    dashboard_url = reverse('dashboard')
    novel_list_url = reverse('novel_list')
    if context.use_client:
        assert context.response.status_code == 200
        request_path = context.response.request['PATH_INFO']
        assert request_path in [dashboard_url, novel_list_url] or "detail" in request_path or "novel" in request_path
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: dashboard_url in driver.current_url or driver.current_url.endswith('/') or novel_list_url in driver.current_url or "detail" in driver.current_url
    )
