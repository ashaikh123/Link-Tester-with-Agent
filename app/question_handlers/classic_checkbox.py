import random
from selenium.webdriver.common.by import By

def answer_classic_checkbox(checkboxes, q_block, driver, answer=None, DEBUG_MODE=False):
    if not checkboxes:
        return False

    print("✅ checkbox found")
    max_to_select = min(2, len(checkboxes))
    num_to_select = random.randint(1, max_to_select)
    selected_boxes = random.sample(checkboxes, num_to_select)
    print(f"{max_to_select},{len(checkboxes)}")

    for box in selected_boxes:
        try:
            print(f"answering checkbox {box}")
            driver.execute_script("arguments[0].click();", box)

            # Check for "other specify"
            print("checking for other specify")
            try:
                parent_label = box.find_element(By.XPATH, "./ancestor::label")
                print(f"✅ Found parent label: {parent_label}")
                search_context = parent_label
            except:
                print("⚠️ No parent label found")
                search_context = q_block

            try:
                possible_inputs = search_context.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                for inp in possible_inputs:
                    if inp.is_displayed() and inp.is_enabled():
                        inp.clear()
                        inp.send_keys(answer if answer else "Other response")
                        print("✅ Filled 'Other specify'")
                        break
            except:
                print("⚠️ Error checking for other input box")

        except Exception as e:
            print(f"⚠️ Failed to interact with checkbox: {e}")

    print("✅ marking handled=true for checkbox")
    if DEBUG_MODE:
        input("🔍 Press Enter to proceed to next step...")
    return True
