from behave import given, then, when
from django.contrib.auth.models import User
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@given('I have a registered account with username "{username}" and password "{password}"')
def registered_account(context, username, password):
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password=password, email=f"{username}@example.com")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()

@given('I am logged in as "{username}"')
def logged_in_as(context, username):
    password = 'SecurePass123!' 
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.save()
    
    if context.use_client:
        context.test.client.force_login(user)
        context.current_user = username
        context.current_path = reverse('dashboard')
        return

    login_url = context.base_url + reverse('login')
    context.browser.get(login_url)
    
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "id_username"))
    )
    
    context.browser.find_element(By.ID, "id_username").send_keys(username)
    context.browser.find_element(By.ID, "id_password").send_keys(password)
    
    btn_xpath = "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')] | " +                 "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')] | " +                 "//button[@type='submit']"
    context.browser.find_element(By.XPATH, btn_xpath).click()
    
    WebDriverWait(context.browser, 10).until(
        lambda driver: "login" not in driver.current_url
    )
    
    context.current_user = username
    context.current_password = password

@given('I am logged in')
def logged_in_default(context):
    context.execute_steps('Given I am logged in as "johndoe"')

@given('I am not logged in')
def not_logged_in(context):
    if context.use_client:
        context.test.client.logout()
        context.current_user = None
        return
    logout_url = context.base_url + reverse('logout')
    context.browser.get(logout_url)
    context.current_user = None

@given('I am on the login page')
def on_login_page(context):
    url = reverse('login')
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        return
    context.browser.get(context.base_url + url)

@given('I am on the registration page')
def on_registration_page(context):
    url = reverse('register')
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        return
    context.browser.get(context.base_url + url)
    context.user_count_before = User.objects.count()

@given('I am on the dashboard')
def on_dashboard(context):
    url_name = 'dashboard'
    if context.use_client:
        context.response = context.test.client.get(reverse(url_name))
        context.current_path = reverse(url_name)
        return
    url = context.base_url + reverse(url_name)
    context.browser.get(url)

@given('a user exists with username "{username}"')
def user_exists(context, username):
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password='somepassword', email=f"{username}@example.com")
    context.user_count_before = User.objects.count()

@when('I try to access the dashboard')
def access_dashboard(context):
    url = reverse('dashboard')
    if context.use_client:
        context.response = context.test.client.get(url, follow=True)
        context.current_path = url
    else:
        context.browser.get(context.base_url + url)

@then('I should be logged in')
def should_be_logged_in(context):
    if context.use_client:
        assert context.response.status_code == 200
        assert context.response.request['PATH_INFO'] in [reverse('dashboard'), reverse('novel_list')]
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: "login" not in driver.current_url
    )
    body_text = context.browser.find_element(By.TAG_NAME, 'body').text.lower()
    assert 'logout' in body_text

@then('I should not be logged in')
def should_not_be_logged_in(context):
    if context.use_client:
        # Check if we are on login page or redirected to it
        assert context.response.request['PATH_INFO'] == reverse('login')
        return
    body_text = context.browser.find_element(By.TAG_NAME, 'body').text.lower()
    is_on_login = "login" in context.browser.current_url
    login_btn_present = len(context.browser.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABC', 'abc'), 'sign in')]")) > 0
    assert is_on_login or login_btn_present

@then('I should be logged out')
def should_be_logged_out(context):
    if context.use_client:
        assert context.response.request['PATH_INFO'] == reverse('login')
        return
    WebDriverWait(context.browser, 10).until(
        lambda driver: "login" in driver.current_url
    )

@then('I should not be able to access protected pages')
def cannot_access_protected(context):
    url = reverse('dashboard')
    if context.use_client:
        context.response = context.test.client.get(url, follow=True)
        assert context.response.request['PATH_INFO'] == reverse('login')
    else:
        context.browser.get(context.base_url + url)
        assert reverse('login') in context.browser.current_url

@then('a new user account should be created in the database')
def user_created(context):
    assert User.objects.filter(username="johndoe").exists()

@then('no user account should be created')
@then('no new user account should be created')
def no_user_created(context):
    if hasattr(context, 'user_count_before'):
        assert User.objects.count() == context.user_count_before
    else:
        assert not User.objects.filter(username="johndoe", email="invalid-email").exists()

@given('my current password is "{password}"')
def current_pw(context, password):
    user = User.objects.get(username=context.current_user)
    if not user.check_password(password):
        user.set_password(password)
        user.save()
        if context.use_client:
            context.test.client.force_login(user)
        else:
            login_url = context.base_url + reverse('login')
            context.browser.get(login_url)
            context.browser.find_element(By.ID, "id_username").send_keys(context.current_user)
            context.browser.find_element(By.ID, "id_password").send_keys(password)
            btn_xpath = "//button[contains(translate(text(), 'ABC', 'abc'), 'sign in')] | //button[@type='submit']"
            context.browser.find_element(By.XPATH, btn_xpath).click()
            WebDriverWait(context.browser, 10).until(
                lambda driver: "login" not in driver.current_url
            )
    context.current_password = password

@given('I am on the password change page')
def on_pw_change_page(context):
    url = reverse('password_change')
    if context.use_client:
        context.response = context.test.client.get(url)
        context.current_path = url
        return
    context.browser.get(context.base_url + url)
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "id_old_password"))
    )

@then('I should be able to login with the new password')
def login_new_pw(context):
    if context.use_client:
        context.test.client.logout()
        user = User.objects.get(username=context.current_user)
        # Verify password check
        assert user.check_password(context.new_password)
        return
    context.browser.get(context.base_url + reverse('logout'))
    context.browser.get(context.base_url + reverse('login'))
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "id_username"))
    )
    context.browser.find_element(By.ID, "id_username").send_keys(context.current_user)
    context.browser.find_element(By.ID, "id_password").send_keys(context.new_password)
    btn_xpath = "//button[contains(translate(text(), 'ABC', 'abc'), 'sign in')] | //button[@type='submit']"
    context.browser.find_element(By.XPATH, btn_xpath).click()
    WebDriverWait(context.browser, 10).until(
        lambda driver: "login" not in driver.current_url
    )

@then('my password should not be changed')
def pw_not_changed(context):
    user = User.objects.get(username=context.current_user)
    assert user.check_password(context.current_password)

# Password validation steps
@then('I should see an error message about password strength')
def see_password_strength_error(context):
    raise StepNotImplementedError('Then I should see an error message about password strength')

@then('I should remain on the login page')
def remain_on_login_page(context):
    raise StepNotImplementedError('Then I should remain on the login page')

@then('I should be redirected to the login page')
def redirected_to_login(context):
    raise StepNotImplementedError('Then I should be redirected to the login page')