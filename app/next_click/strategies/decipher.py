from selenium.webdriver.common.by import By
from .base import NextClickStrategy
from ..helpers import wait_clickable, click_hard

class DecipherStrategy(NextClickStrategy):
    name = "decipher"

    def matches(self, driver) -> bool:
        return bool(driver.find_elements(By.ID, "btn_continue"))

    def click_next(self, driver, timeout: int) -> bool:
        el = wait_clickable(driver, By.ID, "btn_continue", timeout)
        return click_hard(driver, el)
