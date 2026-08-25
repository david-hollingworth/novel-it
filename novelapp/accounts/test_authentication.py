"""
Backend/state tests for authentication (registration, login, logout,
password change), converted from content/requirements/01-user-management.md
per data/requirements/phase-1-run-2-scope.yaml. 16 tests -- all of
01-user-management is included in Run 2, nothing excluded.

Note on T-FUNC-0102.01.01 ("redirected to my novels list"): login_view
redirects to 'dashboard', not 'novel_list' directly. Checked core/views.py:
dashboard_view is a smart router that redirects straight to novel_list once
the user has any novels, or shows an empty-state page otherwise. For a
freshly registered/logged-in user with zero novels (this test's setup),
'dashboard' is the correct, literal target -- not a mismatch with the
requirement's intent.

Message-framework assertions use django.contrib.messages.get_messages
against the response's wsgi_request, the standard way to inspect
messages.success()/messages.error() output from a test client response.
"""
import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from accounts.factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


def get_message_strings(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


# T-FUNC-0101.01.01
@pytest.mark.trace("T-FUNC-0101.01.01")
@pytest.mark.django_db
def test_register_new_account_success(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'a-genuinely-strong-pw9',
        'password2': 'a-genuinely-strong-pw9',
    })
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(username='newuser').exists()


# T-SEC-0101.01.01
@pytest.mark.trace("T-SEC-0101.01.01")
@pytest.mark.django_db
def test_register_with_existing_username_rejected(client, user):
    response = client.post(reverse('register'), {
        'username': user.username,
        'email': 'someoneelse@example.com',
        'password1': 'a-genuinely-strong-pw9',
        'password2': 'a-genuinely-strong-pw9',
    })
    assert response.status_code == 200
    assert User.objects.filter(username=user.username).count() == 1
    assert response.context['form'].errors.get('username')


# T-SEC-0101.02.01
@pytest.mark.trace("T-SEC-0101.02.01")
@pytest.mark.django_db
def test_register_with_weak_password_rejected(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': '12345678',  # entirely numeric -- fails NumericPasswordValidator
        'password2': '12345678',
    })
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()
    assert response.context['form'].errors.get('password2')


# T-DATA-0101.01.01
@pytest.mark.trace("T-DATA-0101.01.01")
@pytest.mark.django_db
def test_email_address_persisted_at_registration(client):
    client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'a-genuinely-strong-pw9',
        'password2': 'a-genuinely-strong-pw9',
    })
    new_user = User.objects.get(username='newuser')
    assert new_user.email == 'newuser@example.com'


# T-FUNC-0101.02.01
@pytest.mark.trace("T-FUNC-0101.02.01")
@pytest.mark.django_db
def test_register_without_password_confirmation_rejected(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'a-genuinely-strong-pw9',
        'password2': '',
    })
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()
    assert response.context['form'].errors.get('password2')


# T-FUNC-0101.02.02
@pytest.mark.trace("T-FUNC-0101.02.02")
@pytest.mark.django_db
def test_register_with_mismatched_passwords_rejected(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'a-genuinely-strong-pw9',
        'password2': 'a-different-strong-pw9',
    })
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()
    assert response.context['form'].errors.get('password2')


# T-FUNC-0102.01.01
@pytest.mark.trace("T-FUNC-0102.01.01")
@pytest.mark.django_db
def test_login_success(client):
    user = UserFactory()  # default password: testpass123, see accounts/factories.py
    response = client.post(reverse('login'), {
        'username': user.username,
        'password': 'testpass123',
    })
    assert response.status_code == 302
    assert response.url == reverse('dashboard')


# T-FUNC-0102.01.02
@pytest.mark.trace("T-FUNC-0102.01.02")
@pytest.mark.django_db
def test_login_with_incorrect_password_fails(client, user):
    response = client.post(reverse('login'), {
        'username': user.username,
        'password': 'wrong-password',
    })
    assert response.status_code == 200
    assert '_auth_user_id' not in client.session


# T-FUNC-0102.02.01
@pytest.mark.trace("T-FUNC-0102.02.01")
@pytest.mark.django_db
def test_logout_success(auth_client):
    response = auth_client.get(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert '_auth_user_id' not in auth_client.session


# T-FUNC-0102.02.02
@pytest.mark.trace("T-FUNC-0102.02.02")
@pytest.mark.django_db
def test_access_after_logout_redirects_to_login(auth_client):
    auth_client.get(reverse('logout'))
    response = auth_client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert reverse('login') in response.url


# T-SEC-0102.01.01
@pytest.mark.trace("T-SEC-0102.01.01")
@pytest.mark.django_db
def test_unauthenticated_access_redirects_to_login(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert reverse('login') in response.url


# T-USER-0102.01.01
@pytest.mark.trace("T-USER-0102.01.01")
@pytest.mark.django_db
def test_login_failure_message_generic_for_unknown_username(client):
    response = client.post(reverse('login'), {
        'username': 'does-not-exist',
        'password': 'whatever123',
    })
    assert 'Invalid username or password.' in get_message_strings(response)


# T-USER-0102.01.02
@pytest.mark.trace("T-USER-0102.01.02")
@pytest.mark.django_db
def test_login_failure_message_identical_for_wrong_password(client, user):
    unknown_response = client.post(reverse('login'), {
        'username': 'does-not-exist',
        'password': 'whatever123',
    })
    wrong_password_response = client.post(reverse('login'), {
        'username': user.username,
        'password': 'wrong-password',
    })
    unknown_messages = get_message_strings(unknown_response)
    wrong_password_messages = get_message_strings(wrong_password_response)
    assert unknown_messages == wrong_password_messages


# T-FUNC-0103.01.01
@pytest.mark.trace("T-FUNC-0103.01.01")
@pytest.mark.django_db
def test_change_password_success(auth_client, user):
    response = auth_client.post(reverse('password_change'), {
        'old_password': 'testpass123',
        'new_password1': 'a-genuinely-strong-pw9',
        'new_password2': 'a-genuinely-strong-pw9',
    })
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password('a-genuinely-strong-pw9')


# T-FUNC-0103.01.02
@pytest.mark.trace("T-FUNC-0103.01.02")
@pytest.mark.django_db
def test_change_password_with_incorrect_current_password_fails(auth_client, user):
    response = auth_client.post(reverse('password_change'), {
        'old_password': 'wrong-current-password',
        'new_password1': 'a-genuinely-strong-pw9',
        'new_password2': 'a-genuinely-strong-pw9',
    })
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password('testpass123')
    assert response.context['form'].errors.get('old_password')


# T-FUNC-0103.02.01
@pytest.mark.trace("T-FUNC-0103.02.01")
@pytest.mark.django_db
def test_change_password_mismatched_new_passwords_fails(auth_client, user):
    response = auth_client.post(reverse('password_change'), {
        'old_password': 'testpass123',
        'new_password1': 'a-genuinely-strong-pw9',
        'new_password2': 'a-different-strong-pw9',
    })
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password('testpass123')
    assert response.context['form'].errors.get('new_password2')
