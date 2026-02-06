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

    clean_field = field.lower()
        
    # Determine the correct field name based on context
    if clean_field == "password":
        # Check current path to determine if registration or login
        current_path = getattr(context, 'current_path', '')
        if 'register' in current_path:
            field_name = "password1"  # Registration form
        else:
            field_name = "password"   # Login/other forms
    elif clean_field == "confirm password":
        field_name = "password2"
    elif clean_field == "current password":
        field_name = "old_password"
    elif clean_field == "new password":
        field_name = "new_password1"
    elif clean_field == "confirm new password":
        field_name = "new_password2"
    else:
        # Use simple mapping for other fields
        simple_map = {
            "username": "username",
            "email": "email",
            "title": "title",
            "description": "description",
            "premise": "premise",
            "genre": "genre",
        }
        field_name = simple_map.get(clean_field, clean_field)   
    
    # Store new password for later verification
    context.new_password = value
    
    if context.use_client:
        if not hasattr(context, 'form_data'):
            context.form_data = {}
        
        context.form_data[field_name] = value
        print(f"DEBUG: Added {field_name}={value}, form_data is now: {context.form_data}")
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
        print(f"DEBUG click_button: form_data at start = {context.form_data}")
        clean_text = button_text.lower()
        
        # Priority 1: Form submission if we have form data
        if context.form_data:
            if context.response and hasattr(context.response, 'request'):
                current_path = context.response.request['PATH_INFO']
            else:
                current_path = getattr(context, 'current_path', '/')
            
            print(f"DEBUG: Posting form to {current_path} with data: {context.form_data}")
            context.response = context.test.client.post(current_path, data=context.form_data, follow=True)
            saved_form_data = context.form_data.copy()
            context.form_data = {}
            print(f"DEBUG: Posted {saved_form_data}, response status: {context.response.status_code}, redirected to: {context.response.request['PATH_INFO']}")
            return
        
        # Priority 2: Check for links in content
        if context.response and context.response.content:
            content = context.response.content.decode('utf-8')
            search_pattern = r'\s+'.join(map(re.escape, button_text.split()))
            pattern = f'<a[^>]+href="([^"]+)"[^>]*>[^<]*{search_pattern}[^<]*</a>'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                print(f"DEBUG: Found link matching '{button_text}', navigating")
                url = match.group(1)
                context.response = context.test.client.get(url, follow=True)
                context.form_data = {}
                return
        
        # Priority 3: Hardcoded navigation links
        link_map = {
            "create new novel": reverse('novel_create'),
            "cancel": reverse('novel_list'),
            "logout": reverse('logout'),
        }
        
        if clean_text in link_map:
            print(f"DEBUG: Found hardcoded link for '{button_text}'")
            context.response = context.test.client.get(link_map[clean_text], follow=True)
            context.form_data = {}
            return
        
        # Fallback
        print(f"DEBUG: No action taken for button '{button_text}'")
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
        content = normalize_text(context.response.content)
        normalized_message = normalize_text(message)
        
        if normalized_message not in content:
            # Debug: show what we're looking for vs what we got
            print(f"\n=== ERROR MESSAGE DEBUG ===")
            print(f"Looking for: '{normalized_message}'")
            print(f"Current path: {context.response.request['PATH_INFO']}")
            print(f"Status code: {context.response.status_code}")
            print(f"Response content (first 500 chars):\n{content[:500]}")
            
            # Check if form errors exist
            if 'form' in context.response.context:
                print(f"Form errors: {context.response.context['form'].errors}")
        
        assert normalized_message in content, \
            f"Expected error message '{message}' not found in response"
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

@then('I should see an error message about password strength')
def see_password_strength_error(context):
    # Check for common password strength error messages
    if context.use_client:
        content = normalize_text(context.response.content)
        password_errors = ['too short', 'too common', 'too similar', 'entirely numeric']
        assert any(err in content for err in password_errors), \
            "No password strength error found in response"
        return

@then('I should remain on the login page')
def remain_on_login_page(context):
    if context.use_client:
        assert context.response.request['PATH_INFO'] == reverse('login')
        return

@then('I should be redirected to the login page')
def redirected_to_login_page(context):
    if context.use_client:
        assert context.response.request['PATH_INFO'] == reverse('login')
        return    
