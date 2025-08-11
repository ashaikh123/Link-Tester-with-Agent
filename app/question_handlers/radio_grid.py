import time
import random
from selenium.webdriver.common.by import By

def answer_radio_grid(grids, driver, DEBUG_MODE=False):
    for grid in grids:
        try:
            rows = grid.find_elements(By.CSS_SELECTOR, 'tr.row.row-elements')
            if not rows:
                continue

            # Validate: at least 2 radios in each row
            if not all(len(row.find_elements(By.CSS_SELECTOR, 'input[type=radio]')) >= 2 for row in rows):
                continue

            print("✅ grid question found")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grid)
            time.sleep(0.3)

            grid_filled = False

            for i, row in enumerate(rows):
                try:
                    radios = row.find_elements(By.CSS_SELECTOR, 'input[type=radio]')
                    radios = [r for r in radios if r.is_enabled()]

                    if not radios:
                        print(f"⚠️ No enabled radios in row {i+1}")
                        continue

                    selected = random.choice(radios)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected)
                    driver.execute_script("arguments[0].click();", selected)
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
                print("❌ Grid visible but no radio options were clickable.")
        except Exception as e:
            print(f"⚠️ Grid block processing failed: {e}")
    return False
