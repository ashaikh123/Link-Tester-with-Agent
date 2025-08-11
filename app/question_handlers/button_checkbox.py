import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

def answer_button_checkbox(button_checkboxes, answer, driver, DEBUG_MODE=False):
    if not button_checkboxes:
        return False

    print("✅ button style checkbox found")

    try:
        max_to_select = min(2, len(button_checkboxes))
        num_to_select = random.randint(1, max_to_select)
        selected_buttons = random.sample(button_checkboxes, num_to_select)

        for btn in selected_buttons:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)

            try:
                ActionChains(driver).move_to_element(btn).click().perform()
                WebDriverWait(driver, 3).until(
                    lambda d: btn.get_attribute('aria-checked') != 'false'
                )
            except Exception:
                btn.send_keys(Keys.SPACE)
                WebDriverWait(driver, 3).until(
                    lambda d: btn.get_attribute('aria-checked') != 'false'
                )

            # Handle Other Specify
            try:
                possible_inputs = btn.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
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

    except Exception as e:
        print(f"⚠️ Button checkbox logic failed: {e}")
        return False
