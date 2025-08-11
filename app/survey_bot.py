import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.answerer import answer_question
from app.utils.alert_utils import show_manual_alert

# question handlers (unchanged)
from app.question_handlers import (
    answer_textarea,
    answer_button_rating,
    answer_slider,
    answer_button_radio,
    answer_radio_grid,
    answer_classic_radio,
    answer_button_checkbox,
    answer_checkbox_grid,
    answer_classic_checkbox,
    answer_dropdown,
    answer_input_box,
    answer_numeric_box,
)

# -------------------------
# Helpers
# -------------------------
def has_actionable_inputs(block):
    """True if this block has something the bot can answer (even if not a plain <input>)."""
    try:
        # Classic inputs quickly
        if block.find_elements(By.CSS_SELECTOR, "input[type='radio'], input[type='checkbox']"):
            return True
        if block.find_elements(By.CSS_SELECTOR, "select, textarea, input[type='text'], input[type='number']"):
            # visible + enabled?
            for el in block.find_elements(By.CSS_SELECTOR, "select, textarea, input[type='text'], input[type='number']"):
                if el.is_displayed() and el.is_enabled():
                    return True

        # Button‑style single/multi selects
        if block.find_elements(By.CSS_SELECTOR, "li.sq-atm1d-button"):
            return True  # role="radio" or role="option" handled later

        # Button rating (no classic inputs)
        if block.find_elements(By.CSS_SELECTOR, ".sq-atmrating-container"):
            # Reassure: look for actual clickable buttons if present
            if block.find_elements(By.CSS_SELECTOR, ".sq-atmrating-container .atmrating-btn"):
                return True
            return True  # container itself is enough to treat as actionable

        # Slider
        if block.find_elements(By.CSS_SELECTOR, ".sq-sliderpoints-container, .ui-slider"):
            return True

        # Grids (radio/checkbox grids)
        if block.find_elements(By.CSS_SELECTOR, "table.grid"):
            return True

        return False
    except Exception:
        return False



def safe_click_next(driver, timeout=3):
    """Click NEXT safely if available."""
    try:
        next_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "btn_continue"))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        return True
    except Exception as e:
        print(f"⚠️ Next click failed: {e}")
        return False


def wait_inputs_ready(block, timeout=3):
    """
    Wait briefly for something actionable in this block:
    - classic inputs
    - button‑style items
    - button rating / slider / grids
    """
    try:
        WebDriverWait(block, timeout).until(
            lambda el: (
                len(el.find_elements(By.CSS_SELECTOR, "input, select, textarea")) > 0
                or el.find_elements(By.CSS_SELECTOR, "li.sq-atm1d-button")
                or el.find_elements(By.CSS_SELECTOR, ".sq-atmrating-container")
                or el.find_elements(By.CSS_SELECTOR, ".sq-sliderpoints-container, .ui-slider")
                or el.find_elements(By.CSS_SELECTOR, "table.grid")
            )
        )
        print("✅ Inputs detected in time.")
        time.sleep(0.2)
    except Exception:
        print("⚠️ Inputs not detected in time.")


# -------------------------
# Main
# -------------------------
def run_survey(driver, survey_url: str, profile: dict):
    driver.get(survey_url)
    DEBUG_MODE = False

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        while True:
            # Wait for a page with at least one question/comment block
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.question, div[class*="question"]'))
                )
                time.sleep(0.5)  # small buffer so inputs are interactive
            except Exception:
                print("⚠️ Timed out waiting for question block. Exiting.")
                break

            print("\n--- page loaded ---\n")
            all_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.question, div[class*="question"]')
            print(f"All Questions: {len(all_blocks)}")

            # PAGE-LEVEL: filter to actionable blocks; do NOT click Next inside the loop
            actionable_blocks = [b for b in all_blocks if has_actionable_inputs(b)]

            if not actionable_blocks:
                # Pure intro/info page -> just Next
                print("✅ Detected info screen or intro page (no actionable inputs). Skipping…")
                if not safe_click_next(driver):
                    # If Next isn't clickable, fall back to generic submit selector
                    try:
                        driver.find_element(By.CSS_SELECTOR, 'button, input[type=submit]').click()
                    except Exception:
                        pass
                continue  # next page

            # There ARE actionable blocks on this page → answer them
            page_handled_any = False

            for q_block in actionable_blocks:
                # grab question text (best effort)
                try:
                    qt_el = q_block.find_element(By.CSS_SELECTOR, '.question-text')
                    question_text = (qt_el.get_attribute('innerText') or "").strip()
                except Exception:
                    question_text = "Unnamed Question"

                # wait a beat for inputs in this specific block
                wait_inputs_ready(q_block, timeout=3)

                # gather options (best effort; used only for logging/answer heuristics)
                try:
                    option_els = q_block.find_elements(By.CSS_SELECTOR, '.cell-text.cell-sub-column label')
                    options = [opt.text.strip() for opt in option_els if opt.text.strip()]
                    if not options:
                        legends = q_block.find_elements(By.CSS_SELECTOR, '.sq-atm1d-legend')
                        options = [lg.text.strip() for lg in legends if lg.text.strip()]
                        if not options:
                            btns = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable')
                            options = [li.text.strip() for li in btns if li.text.strip()]
                except Exception:
                    options = []

                print("\n--- Question Block ---")
                print("Q:", question_text)
                if options:
                    print("Options:", options)

                # generate an answer string for OE/specify fields
                answer = answer_question(question_text, profile)
                # print(f"Q: {question_text}\nA: {answer}")

                handled = False

                # === Handlers (order matters; keep as you had) ===

                # textarea
                try:
                    textarea = q_block.find_element(By.TAG_NAME, 'textarea')
                    if answer_textarea(textarea, answer, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # button rating
                try:
                    blocks = q_block.find_elements(By.CSS_SELECTOR, ".sq-atmrating-container")
                    if blocks and answer_button_rating(blocks, driver, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"⚠️ Button rating handler error: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # slider
                try:
                    sblocks = q_block.find_elements(By.CSS_SELECTOR, ".sq-sliderpoints-container")
                    if sblocks and answer_slider(sblocks, driver, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"⚠️ Slider question handling failed: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # button-style single-select radio
                try:
                    button_radios = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button[role="radio"]')
                    if button_radios and answer_button_radio(button_radios, driver, answer, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"⚠️ Button radio logic failed: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # radio grid
                try:
                    grid_tables = q_block.find_elements(By.CSS_SELECTOR, 'table.grid')
                    if grid_tables and answer_radio_grid(grid_tables, driver, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"⚠️ Grid answer error: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # classic radio
                try:
                    radios = q_block.find_elements(By.CSS_SELECTOR, 'input[type=radio]')
                    if radios and answer_classic_radio(radios, q_block, answer, driver, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # button-style multi-select checkboxes
                try:
                    button_checkboxes = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable[role="option"]')
                    if button_checkboxes and answer_button_checkbox(button_checkboxes, answer, driver, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # checkbox grid
                try:
                    cgrids = q_block.find_elements(By.CSS_SELECTOR, 'table.grid')
                    if cgrids and answer_checkbox_grid(cgrids, driver, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"⚠️ Checkbox grid answer error: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # classic checkboxes
                try:
                    checkboxes = q_block.find_elements(By.CSS_SELECTOR, 'input[type=checkbox]')
                    if checkboxes and answer_classic_checkbox(checkboxes, q_block, driver, answer, DEBUG_MODE):
                        handled = True
                except Exception as e:
                    print(f"❌ Error in checkbox handler: {e}")
                if handled: 
                    page_handled_any = True
                    continue

                # dropdown
                try:
                    select = q_block.find_element(By.TAG_NAME, 'select')
                    if select and answer_dropdown(select, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # input text
                try:
                    input_box = q_block.find_element(By.CSS_SELECTOR, 'input[type="text"]')
                    if input_box and answer_input_box(input_box, answer, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # input number
                try:
                    num_box = q_block.find_element(By.CSS_SELECTOR, 'input[type="number"]')
                    if num_box and answer_numeric_box(num_box, answer, DEBUG_MODE):
                        handled = True
                except Exception:
                    pass
                if handled: 
                    page_handled_any = True
                    continue

                # end of handlers for this q_block

            # If nothing on this page was handled, prompt manual input and loop.
            if not page_handled_any:
                print("⚠️ Unhandled actionable block(s). Prompting manual input…")
                show_manual_alert(driver)  # your improved alert waits for page change
                continue  # after manual, page should change and we re-loop

            # Otherwise try Next (some pages auto-advance; this is harmless)
            safe_click_next(driver)

    finally:
        driver.quit()
