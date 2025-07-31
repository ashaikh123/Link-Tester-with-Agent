
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.answerer import answer_question
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def run_survey(driver, survey_url: str, profile: dict):
    driver.get(survey_url)
    DEBUG_MODE = False
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        while True:
            time.sleep(2)
            print("\n--- page loaded ---\n")
            question_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.question, div[class*="question"]')
            if not question_blocks:
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, 'button, input[type=submit]')
                    next_btn.click()
                    continue
                except:
                    break
            no_of_questions=len(question_blocks)
            print(f"All Questions: {no_of_questions}")                
            for q_block in question_blocks:
                handled = False
                #question_text = q_block.text.strip() or "Unnamed Question"

                try:
                    # 1. Question Text
                    question_text_el = q_block.find_element(By.CSS_SELECTOR, '.question-text')
                    question_text = question_text_el.get_attribute('innerText').strip()
                except:
                    question_text = "Unnamed Question"

                try:
                    # 2. Instruction Text (optional)
                    instruction_el = q_block.find_element(By.CSS_SELECTOR, '.instruction-text')
                    instruction_text = instruction_el.get_attribute('innerText').strip()
                except:
                    instruction_text = ""

                # 3. All answer labels
                try:
                    option_els = q_block.find_elements(By.CSS_SELECTOR, '.cell-text.cell-sub-column label')
                    options = []

                    if option_els:
                        # Try to collect non‑empty label text
                        for opt in option_els:
                            label_text = opt.text.strip()
                            if label_text:
                                options.append(label_text)

                        # If no label text was found, treat it as button‑select
                        if not options:
                            # extract from .sq‑atm1d-legend spans
                            legends = q_block.find_elements(By.CSS_SELECTOR, '.sq-atm1d-legend')
                            for legend in legends:
                                legend_text = legend.text.strip()
                                if legend_text:
                                    options.append(legend_text)

                            # if still nothing, fall back to li text itself
                            if not options:
                                button_opts = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable')
                                for li in button_opts:
                                    li_text = li.text.strip()
                                    if li_text:
                                        options.append(li_text)
                    else:
                        # No label elements at all: use button‑select fallback
                        legends = q_block.find_elements(By.CSS_SELECTOR, '.sq-atm1d-legend')
                        for legend in legends:
                            legend_text = legend.text.strip()
                            if legend_text:
                                options.append(legend_text)

                        if not options:
                            button_opts = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable')
                            for li in button_opts:
                                li_text = li.text.strip()
                                if li_text:
                                    options.append(li_text)
                except:
                    options = []





                # --- Debug print ---
                print("\n--- Question Block ---")
                print("Q:", question_text)
                if instruction_text:
                    print("Instruction:", instruction_text)
                print("Options:", options)
                #if DEBUG_MODE:
                    #input("🔍 Press Enter to proceed to next step...")




                answer = answer_question(question_text, profile)
                print(f"Q: {question_text}\nA: {answer}")
                #if DEBUG_MODE:
                    #input("🔍 Press Enter to proceed to next step...")




                try:
                    textarea = q_block.find_element(By.TAG_NAME, 'textarea')
                    if textarea.is_displayed() and textarea.is_enabled():
                        print(f"textarea found")
                        textarea.clear()
                        textarea.send_keys(answer)
                        print(f"Answer {answer}")
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")

                        continue
                except:
                    pass









                try:
                    grids = q_block.find_elements(By.CSS_SELECTOR, 'table.grid')
                    for grid in grids:
                        rows = grid.find_elements(By.CSS_SELECTOR, 'tr.row.row-elements')
                        if not rows:
                            continue

                        grid_is_valid = all(
                            len(row.find_elements(By.CSS_SELECTOR, 'input[type=radio]')) >= 2
                            for row in rows
                        )
                        if not grid_is_valid:
                            continue

                        print("✅ grid question confirmed")
                        for row in rows:
                            radios = row.find_elements(By.CSS_SELECTOR, 'input[type=radio]')
                            radios = [r for r in radios if r.is_displayed() and r.is_enabled()]
                            if not radios:
                                continue
                            selected = random.choice(radios)
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected)
                            driver.execute_script("arguments[0].click();", selected)
                            time.sleep(0.2)  # small wait for UI feedback

                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except Exception as e:
                    print(f"⚠️ Grid answer error: {e}")



                # Radio buttons
                try:
                    radios = q_block.find_elements(By.CSS_SELECTOR, 'input[type=radio]')
                    if radios:
                        print("radio found")
                        # choose one radio at random
                        selected = random.choice(radios)
                        # click the radio (JavaScript click works too)
                        driver.execute_script("arguments[0].click();", selected)
                        handled = True
                        # --- New: handle “Other/Specify” text field for radio ---
                        try:
                            # if the radio is wrapped in a <label>, search there; otherwise search within the question block
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
                        continue
                except:
                    pass





                # Button-style multi-select checkboxes
                try:
                    button_checkboxes = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable')
                    if button_checkboxes:
                        print("checkbox found button")
                        # choose a random number of options to select (1–2 or up to available)
                        max_to_select = min(2, len(button_checkboxes))
                        num_to_select = random.randint(1, max_to_select)
                        selected_buttons = random.sample(button_checkboxes, num_to_select)

                        for btn in selected_buttons:
                            # bring into view
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                            try:
                                # try normal click first
                                ActionChains(driver).move_to_element(btn).click().perform()
                                WebDriverWait(driver, 3).until(
                                    lambda d: btn.get_attribute('aria-checked') != 'false'
                                )
                            except Exception:
                                # fallback: toggle with space
                                btn.send_keys(Keys.SPACE)
                                WebDriverWait(driver, 3).until(
                                    lambda d: btn.get_attribute('aria-checked') != 'false'
                                )
                            # --- New: handle “Other/Specify” text field ---
                            # After clicking, look for a visible text input or textarea inside this list item
                            try:
                                possible_inputs = btn.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                                for inp in possible_inputs:
                                    if inp.is_displayed() and inp.is_enabled():
                                        # fill the specify field with your generated answer or a placeholder
                                        inp.clear()
                                        inp.send_keys(answer if answer else "Other response")
                                        break
                            except:
                                pass
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass

                # Classic multi-select checkboxes
                try:
                    checkboxes = q_block.find_elements(By.CSS_SELECTOR, 'input[type=checkbox]')
                    if checkboxes:
                        print("checkbox found")
                        max_to_select = min(2, len(checkboxes))
                        num_to_select = random.randint(1, max_to_select)
                        selected_boxes = random.sample(checkboxes, num_to_select)

                        for box in selected_boxes:
                            driver.execute_script("arguments[0].click();", box)
                            # after clicking a checkbox, check whether a sibling text input appears
                            parent_label = box.find_element(By.XPATH, "./ancestor::label") if hasattr(box, "find_element") else None
                            search_context = parent_label if parent_label else q_block
                            possible_inputs = search_context.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                            for inp in possible_inputs:
                                if inp.is_displayed() and inp.is_enabled():
                                    inp.clear()
                                    inp.send_keys(answer if answer else "Other response")
                                    break
                        handled = True        
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass




                try:
                    select = q_block.find_element(By.TAG_NAME, 'select')
                    options = select.find_elements(By.TAG_NAME, 'option')
                    if options:
                        print(f"dropdown found")
                        options[1].click()
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass


                try:
                    input_box = q_block.find_element(By.CSS_SELECTOR, 'input[type="text"]')
                    if input_box.is_displayed() and input_box.is_enabled():
                        print(f"Input box found")
                        input_box.clear()
                        input_box.send_keys(answer)
                        print(f"Answer {answer}")
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass

                try:
                    input_box = q_block.find_element(By.CSS_SELECTOR, 'input[type="number"]')
                    if input_box.is_displayed() and input_box.is_enabled():
                        print(f"Numeric box found")
                        input_box.clear()
                        input_box.send_keys(answer)
                        print(f"Answer {answer}")
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass

                try:
                    info_screen = q_block.find_element(By.CSS_SELECTOR, 'div.html comment')
                    print(f"Checking for info screen \n {info_screen}")
                    
                    if info_screen.is_displayed():
                        print(f"Info screen found")
                        info_screen.clear()
                        handled = True
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass


                try:
                    slider_blocks = q_block.find_elements(By.CSS_SELECTOR, ".sq-sliderpoints-container")
                    if not slider_blocks:
                        print("no slider question found")
                        continue
                    
                    print("✅ slider question found")

                    for block in slider_blocks:
                        try:
                            slider = block.find_element(By.CLASS_NAME, "ui-slider")
                            handle = slider.find_element(By.CLASS_NAME, "ui-slider-handle")
                            
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

                        except Exception as e:
                            print(f"⚠️ Failed to move slider: {e}")
                    
                    continue

                except Exception as e:
                    print(f"⚠️ Slider question handling failed: {e}")


            if not handled:
                driver.execute_script("alert('Please answer the question manually, then click OK to continue');")
                # the script will pause here until the alert is closed
                WebDriverWait(driver, 3000).until(EC.alert_is_present())
                driver.switch_to.alert.accept()

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'button, input[type=submit]')
                next_btn.click()
            except:
                break
    finally:
        driver.quit()
