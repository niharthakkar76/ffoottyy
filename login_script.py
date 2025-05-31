from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import time
import sys
import os

def log_message(message):
    """Helper function to log messages with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] {message}")

def login_and_wait():
    # Get credentials from environment variables or use defaults
    USERNAME = os.environ.get('FOTTYY_USERNAME', 'nihar')
    PASSWORD = os.environ.get('FOTTYY_PASSWORD', 'nihar1234')


    
    with sync_playwright() as p:
        browser = None
        try:
            # Launch browser in headless mode for CI/CD with more stable settings
            log_message("Launching browser in headless mode...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ],
                slow_mo=200  # Increased from 100ms to 200ms for more reliability
            )
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()
            
            # Navigate to the login page with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    log_message(f"Navigation attempt {attempt + 1}/{max_retries}")
                    page.goto("https://fottyygit.streamlit.app/?page=login", 
                              timeout=90000,  # Increased timeout to 90 seconds
                              wait_until="domcontentloaded")
                    log_message(f"Page loaded successfully after {page.evaluate('window.performance.timing.loadEventEnd - window.performance.timing.navigationStart')}ms")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        log_message(f"Failed to load page after {max_retries} attempts: {str(e)}")
                        raise
                    log_message(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(5)  # Wait before retry
                
            log_message("Page loaded successfully")
            
            # Wait for the form to be visible
            log_message("Waiting for the login form...")
            
            # First, try to find and interact with the form directly
            try:
                # Wait for the username field to be visible
                log_message("Looking for username field...")
                username_field = page.wait_for_selector('input[aria-label="Username"]', timeout=10000)
                log_message("Found username field")
                
                # Clear and fill username
                username_field.click()
                page.keyboard.press('Control+A')
                page.keyboard.press('Backspace')
                username_field.type(USERNAME, delay=100)
                log_message("Filled username")
                
                # Find and fill password
                log_message("Looking for password field...")
                password_field = page.wait_for_selector('input[aria-label="Password"]', timeout=5000)
                log_message("Found password field")
                
                # Clear and fill password
                password_field.click()
                page.keyboard.press('Control+A')
                page.keyboard.press('Backspace')
                password_field.type(PASSWORD, delay=100)
                log_message("Filled password")
                
                # Click the login button
                log_message("Looking for login button...")
                login_button = page.wait_for_selector('button[data-testid="stBaseButton-secondaryFormSubmit"]', timeout=5000)
                log_message("Found login button")
                
                # Click the login button
                login_button.click()
                log_message("Clicked login button")
                
            except Exception as e:
                log_message(f"Error interacting with form: {str(e)}")
                
                # Try alternative approach with iframe if direct interaction fails
                try:
                    log_message("Trying alternative approach with iframe...")
                    
                    # Wait for the iframe to be visible
                    frame = page.wait_for_selector('iframe', timeout=5000)
                    if frame:
                        log_message("Found iframe, switching to it")
                        frame = frame.content_frame()
                        
                        # Now try to find elements inside the iframe
                        username_field = frame.wait_for_selector('input[aria-label="Username"]', timeout=5000)
                        username_field.click()
                        username_field.fill(USERNAME)
                        
                        password_field = frame.wait_for_selector('input[aria-label="Password"]', timeout=5000)
                        password_field.click()
                        password_field.fill(PASSWORD)
                        
                        login_button = frame.wait_for_selector('button[data-testid="stBaseButton-secondaryFormSubmit"]', timeout=5000)
                        login_button.click()
                        log_message("Successfully submitted form inside iframe")
                    
                except Exception as iframe_error:
                    log_message(f"Failed to interact with iframe: {str(iframe_error)}")
                    raise Exception("Could not interact with the login form")
            
            # Wait for navigation after login
            try:
                log_message("Waiting for navigation...")
                page.wait_for_load_state("networkidle")
                log_message("Successfully logged in!")
                
                # Wait for 10 minutes (600 seconds)
                wait_minutes = 10
                log_message(f"Waiting for {wait_minutes} minutes...")
                for remaining in range(wait_minutes * 60, 0, -1):
                    if remaining % 60 == 0:
                        log_message(f"Time remaining: {remaining//60} minutes")
                    time.sleep(1)
                log_message(f"{wait_minutes} minutes have passed!")
                
            except Exception as e:
                log_message(f"Navigation error: {str(e)}")
                # Continue even if navigation check fails an error
                log_message("Navigation error occurred")
                
        except Exception as e:
            log_message(f"An error occurred: {str(e)}")
            log_message(f"Error type: {type(e).__name__}")
            import traceback
            log_message("Traceback:" + traceback.format_exc())
            
        finally:
            # Close the browser
            if browser:
                try:
                    log_message("Closing browser...")
                    browser.close()
                    log_message("Browser closed successfully")
                except Exception as e:
                    log_message(f"Error while closing browser: {str(e)}")
            else:
                log_message("No browser instance to close")

if __name__ == "__main__":
    log_message("Script started")
    try:
        login_and_wait()
    except Exception as e:
        log_message(f"Script failed: {str(e)}")
        sys.exit(1)
    log_message("Script completed successfully")
