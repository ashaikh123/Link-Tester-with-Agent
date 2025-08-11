import time
import random
from selenium.webdriver.common.action_chains import ActionChains

def answer_slider(slider_blocks, driver, DEBUG_MODE=False):
    if not slider_blocks:
        return False

    print("✅ slider question found")
    handled_any = False

    for block in slider_blocks:
        try:
            slider = block.find_element("class name", "ui-slider")
            handle = slider.find_element("class name", "ui-slider-handle")

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider)
            time.sleep(0.2)

            # Get width of slider bar
            slider_width = slider.size['width']

            # Random offset between 10% to 90% of width
            offset = int(slider_width * random.uniform(0.1, 0.9))

            # Drag handle to the offset
            ActionChains(driver).click_and_hold(handle).move_by_offset(offset, 0).release().perform()
            print(f"✅ Slider moved by offset: {offset}px")

            handled_any = True

        except Exception as e:
            print(f"⚠️ Failed to move slider: {e}")

    if handled_any and DEBUG_MODE:
        input("🔍 Press Enter to proceed to next step...")

    return handled_any
