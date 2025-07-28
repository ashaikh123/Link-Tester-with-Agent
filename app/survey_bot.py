
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
            question_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.question, div[class*="question"]')
            if not question_blocks:
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, 'button, input[type=submit]')
                    next_btn.click()
                    continue
                except:
                    break
            #print(f"All Questions: {question_blocks}")                
            for q_block in question_blocks:
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
                        # standard label-based questions
                        options = [opt.text.strip() for opt in option_els if opt.text.strip()]
                    else:
                        # fallback: first try extracting from legend spans
                        legends = q_block.find_elements(By.CSS_SELECTOR, '.sq-atm1d-legend')
                        for legend in legends:
                            label_text = legend.text.strip()
                            if label_text:
                                options.append(label_text)

                        # if no legends were found, fall back to the li text itself
                        if not options:
                            button_opts = q_block.find_elements(By.CSS_SELECTOR, 'li.sq-atm1d-button.clickable')
                            for li in button_opts:
                                label_text = li.text.strip()
                                if label_text:
                                    options.append(label_text)
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
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")

                        continue
                except:
                    pass

                # Radio buttons
                try:
                    radios = q_block.find_elements(By.CSS_SELECTOR, 'input[type=radio]')
                    if radios:
                        print("radio found")
                        # choose one radio at random
                        selected = random.choice(radios)
                        # click the radio (JavaScript click works too)
                        driver.execute_script("arguments[0].click();", selected)

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
                        if DEBUG_MODE:
                            input("🔍 Press Enter to proceed to next step...")
                        continue
                except:
                    pass

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'button, input[type=submit]')
                next_btn.click()
            except:
                break
    finally:
        driver.quit()
