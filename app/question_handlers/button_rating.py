import random
import time

def answer_button_rating(button_rating_blocks, driver, DEBUG_MODE=False):
    for block in button_rating_blocks:
        try:
            # Get the visible rating buttons inside the container
            buttons_container = block.find_element("class name", "atmrating_input")
            buttons = buttons_container.find_elements("class name", "atmrating-btn")

            if not buttons:
                print("⚠️ No visible buttons found in atmrating_input.")
                continue

            # Randomly select a rating button and click it
            selected = random.choice(buttons)
            driver.execute_script("arguments[0].scrollIntoView(true);", selected)
            time.sleep(0.2)
            selected.click()
            print(f"➡️ Clicked rating button: {buttons.index(selected)+1}")

        except Exception as e:
            print(f"⚠️ Failed to click rating button: {e}")

    if DEBUG_MODE:
        input("🔍 Press Enter to continue...")

    return True  # Mark question as handled
