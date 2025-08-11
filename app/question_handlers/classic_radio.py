import random
from selenium.webdriver.common.by import By

def answer_classic_radio(radios, q_block, answer, driver, DEBUG_MODE=False):
    if not radios:
        return False

    print("✅ radio found")

    try:
        selected = random.choice(radios)
        driver.execute_script("arguments[0].click();", selected)

        # Handle "Other Specify"
        try:
            parent_label = selected.find_element(By.XPATH, "./ancestor::label") if hasattr(selected, "find_element") else None
            search_context = parent_label if parent_label else q_block

            possible_inputs = search_context.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
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
        print(f"⚠️ Classic radio error: {e}")
        return False
