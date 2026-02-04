from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os

def before_all(context):
    # Django setup - must come first
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novelapp.settings_test')
    django.setup()
    context.use_client = False
    options = Options()
    options.add_argument("--headless")
    
    binary_path = "/snap/firefox/current/usr/lib/firefox/firefox"
    if os.path.exists(binary_path):
        options.binary_location = binary_path
    
    try:
        # We still initialize the browser for scenarios that might need it
        context.browser = webdriver.Firefox(options=options)
        context.browser.implicitly_wait(10)
    except Exception as e:
        print(f"Failed to start Firefox: {e}")
        options.binary_location = None
        try:
            context.browser = webdriver.Firefox(options=options)
            context.browser.implicitly_wait(10)
        except Exception as e2:
            print(f"Failed again: {e2}")
            pass

def after_all(context):
    if hasattr(context, 'browser'):
        context.browser.quit()

def before_scenario(context, scenario):
    context.form_data = {}
    context.response = None
    # Use client by default for everything unless tagged with selenium
    if 'selenium' in scenario.effective_tags:
        context.use_client = False
        if hasattr(context, 'browser'):
            context.browser.delete_all_cookies()
    else:
        context.use_client = True
