from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os

def before_all(context):
    context.use_client = False
    context.browser = None  # Initialize as None
    
    # Only try to set up Firefox if we actually have selenium tests
    options = Options()
    options.add_argument("--headless")
    
    binary_path = "/snap/firefox/current/usr/lib/firefox/firefox"
    if os.path.exists(binary_path):
        options.binary_location = binary_path
    
    try:
        context.browser = webdriver.Firefox(options=options)
        context.browser.implicitly_wait(10)
    except Exception as e:
        print(f"Warning: Firefox not available - Selenium tests will be skipped: {e}")
        context.browser = None  # Set to None if Firefox fails

def before_scenario(context, scenario):
    context.form_data = {}  # Add this line
    context.response = None
    # Use client by default for everything unless tagged with selenium
    if 'selenium' in scenario.effective_tags:
        if context.browser is None:
            scenario.skip("Selenium/Firefox not available in this environment")
            return
        context.use_client = False
        if hasattr(context, 'browser'):
            context.browser.delete_all_cookies()
    else:
        context.use_client = True

def after_all(context):
    if hasattr(context, 'browser') and context.browser is not None:
        context.browser.quit()

