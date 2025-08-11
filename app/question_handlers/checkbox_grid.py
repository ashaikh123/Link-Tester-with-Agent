import random
import time
from selenium.webdriver.common.by import By

def answer_checkbox_grid(grids, driver, DEBUG_MODE=False):
    if not grids:
        return False

    for grid in grids:
        try:
            rows = grid.find_elements(By.CSS_SELECTOR, 'tr.row.row-elements')
            if not rows:
                continue

            # Validate if it's a checkbox grid
            grid_is_checkbox = all(
                len(row.find_elements(By.CSS_SELECTOR, 'input[type=checkbox]')) >= 1
                for row in rows
            )
            if not grid_is_checkbox:
                continue

            print("✅ checkbox grid question found")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grid)
            time.sleep(0.3)

            grid_filled = False

            for i, row in enumerate(rows):
                try:
                    checkboxes = row.find_elements(By.CSS_SELECTOR, 'input[type=checkbox]')
                    checkboxes = [cb for cb in checkboxes if cb.is_enabled()]

                    if not checkboxes:
                        print(f"⚠️ No enabled checkboxes in row {i+1}")
                        continue

                    # Randomly select 1–2 checkboxes per row
                    num_to_select = min(len(checkboxes), random.randint(1, 2))
                    to_click = random.sample(checkboxes, num_to_select)

                    for checkbox in to_click:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                        driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.2)

                    grid_filled = True

                except Exception as e:
                    print(f"⚠️ Could not interact with row {i+1}: {e}")
                    continue

            if grid_filled:
                if DEBUG_MODE:
                    input("🔍 Press Enter to continue...")
                return True
            else:
                print("❌ Checkbox grid visible but nothing was clickable.")

        except Exception as e:
            print(f"⚠️ Error processing grid: {e}")

    return False
