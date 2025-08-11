import json
import time
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By

def get_current_block_ids(driver):
    try:
        blocks = driver.find_elements(By.CSS_SELECTOR, 'div.question, div[class*="question"]')
        return [block.get_attribute('id') for block in blocks if block.get_attribute('id')]
    except Exception:
        return []

def show_manual_alert(driver, message="Manual question detected. Please answer manually and press OK."):
    original_ids = get_current_block_ids(driver)

    while True:
        try:
            # Show alert
            driver.execute_script(f"alert({json.dumps(message)});")
            print("📢 Manual alert shown to user.")

        except Exception as e:
            print(f"⚠️ Alert JS error: {e}")
            return

        # Wait for user to dismiss the alert
        print("⏳ Waiting for user to dismiss the alert...")
        while True:
            try:
                driver.switch_to.alert
                time.sleep(0.5)
            except NoAlertPresentException:
                print("✅ Alert dismissed by user.")
                break

        # Start polling for question change (30 seconds max)
        print("⏳ Waiting up to 30s for user to manually answer and click next...")
        start_time = time.time()
        while time.time() - start_time < 30:
            current_ids = get_current_block_ids(driver)
            if current_ids != original_ids:
                print("✅ Page changed. Proceeding...")
                return
            time.sleep(0.5)

        print("⚠️ No page change detected. Repeating alert...")
