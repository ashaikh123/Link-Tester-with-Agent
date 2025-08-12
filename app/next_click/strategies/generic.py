from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import NextClickStrategy

class GenericEnterFallbackStrategy(NextClickStrategy):
    name = "generic-enter"

    def matches(self, driver) -> bool:
        return True  # last in order only

    def click_next(self, driver, timeout: int) -> bool:
        try:
            form = driver.find_element(By.CSS_SELECTOR, "form")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", form)
            form.send_keys(Keys.ENTER)
            return True
        except Exception:
            return False
