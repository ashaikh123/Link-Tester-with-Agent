from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, JavascriptException

def wait_clickable(driver, by: By, selector: str, timeout: int):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )

def click_hard(driver, elem) -> bool:
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
    except Exception:
        pass
    try:
        elem.click()
        return True
    except ElementClickInterceptedException:
        pass
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].click();", elem)
        return True
    except (JavascriptException, Exception):
        return False
