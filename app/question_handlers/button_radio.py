import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

def answer_button_radio(button_radios, driver, answer, DEBUG_MODE=False):
    if not button_radios:
        return False

    print("✅ button-style radio found")

    selected_button = random.choice(button_radios)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selected_button)

    try:
        # Try normal click
        ActionChains(driver).move_to_element(selected_button).click().perform()
        WebDriverWait(driver, 3).until(
            lambda d: selected_button.get_attribute('aria-checked') == 'true'
        )
    except Exception:
        # Fallback to space press
        selected_button.send_keys(Keys.SPACE)
        WebDriverWait(driver, 3).until(
            lambda d: selected_button.get_attribute('aria-checked') == 'true'
        )

    # --- Handle Other Specify ---
    try:
        possible_inputs = selected_button.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
        for inp in possible_inputs:
            if inp.is_displayed() and inp.is_enabled():
                inp.clear()
                inp.send_keys(answer if answer else "Other response")
                break
    except:
        pass

    if DEBUG_MODE:
        input("🔍 Press Enter to proceed to next step...")

    return True
