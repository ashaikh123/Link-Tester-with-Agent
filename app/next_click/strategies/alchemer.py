from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .base import NextClickStrategy
from ..helpers import wait_clickable, click_hard

class AlchemerStrategy(NextClickStrategy):
    name = "alchemer"

    def matches(self, driver) -> bool:
        return bool(driver.find_elements(By.ID, "sg_NextButton")) or \
               bool(driver.find_elements(By.CSS_SELECTOR, "form.sg-survey-form"))

    def click_next(self, driver, timeout: int) -> bool:
        # Set nav choice like Alchemer's onclick handler
        try:
            driver.execute_script("""
                (function(){
                  var f = document.querySelector('form.sg-survey-form');
                  if (!f) return;
                  var nav = document.getElementById('sg_navchoice') || f.querySelector("input[name='sg_navchoice']");
                  if (nav) nav.value = 'sGizmoNextButton';
                })();
            """)
        except Exception:
            pass

        try:
            el = wait_clickable(driver, By.ID, "sg_NextButton", timeout)
            if click_hard(driver, el): return True
        except TimeoutException:
            pass

        for sel in ("input.sg-next-button", "button.sg-next-button"):
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els and click_hard(driver, els[0]): return True

        try:
            driver.execute_script("""
                var f = document.querySelector('form.sg-survey-form');
                if (f) f.submit();
            """)
            return True
        except Exception:
            return False
