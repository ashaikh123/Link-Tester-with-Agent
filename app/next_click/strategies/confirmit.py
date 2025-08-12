# next_click/strategies/confirmit.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException
from .base import NextClickStrategy
from ..helpers import wait_clickable, click_hard

class ConfirmitStrategy(NextClickStrategy):
    name = "confirmit"

    def matches(self, driver) -> bool:
        return bool(driver.find_elements(By.ID, "forwardbutton")) or \
               bool(driver.find_elements(By.CSS_SELECTOR, ".confirmit-nav, .powerby a[href*='confirmit']"))

    def _wait_wix_ready(self, driver, timeout):
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return !!(window.wix && typeof wix.nav === 'function');")
            )
            return True
        except Exception:
            return False

    def _wait_navigated(self, driver, old_form, timeout):
        if not old_form:
            return False
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(old_form))
            return True
        except TimeoutException:
            return False

    def click_next(self, driver, timeout: int) -> bool:
        # capture current form so we can detect a page transition
        try:
            old_form = driver.find_element(By.ID, "ctlform")
        except Exception:
            old_form = None

        # 1) Preferred: call wix.nav like the onclick on #forwardbutton
        if self._wait_wix_ready(driver, timeout):
            try:
                driver.execute_script("""
                    (function(){
                        var btn = document.getElementById('forwardbutton');
                        var pageId = (function(){
                            var a = (document.forms[0] && document.forms[0].action) || '';
                            var m = a.match(/\\/wix\\/([^\\.]+)\\.aspx/);
                            return m ? m[1] : '';
                        })();
                        var ev = { preventDefault:function(){}, stopPropagation:function(){}, target: btn };
                        wix.nav(ev, pageId);
                    })();
                """)
                if self._wait_navigated(driver, old_form, 8):
                    return True
            except JavascriptException:
                pass

        # 2) Dispatch a real click event (some skins rely on event object)
        try:
            el = wait_clickable(driver, By.ID, "forwardbutton", timeout)
            driver.execute_script("""
                var btn = arguments[0];
                if (!btn) return;
                btn.focus();
                var ev = new MouseEvent('click', {bubbles:true, cancelable:true, view:window});
                btn.dispatchEvent(ev);
            """, el)
            if self._wait_navigated(driver, old_form, 8):
                return True
        except TimeoutException:
            pass
        except JavascriptException:
            pass

        # 3) Simple JS/native click fallback
        try:
            el = driver.find_element(By.ID, "forwardbutton")
            if click_hard(driver, el):
                if self._wait_navigated(driver, old_form, 8):
                    return True
        except Exception:
            pass

        # 4) Hard submit: set script enabled, push forward token, ensure __fwd, submit
        try:
            driver.execute_script("""
                (function(){
                    var f = document.getElementById('ctlform') || document.querySelector('form.ctlform');
                    if (!f) return;
                    var se = document.getElementById('script__enabled__');
                    if (se) se.value = '1';
                    var stack = f.querySelector("input[name='__navigationButtonStack']");
                    if (!stack) { stack = document.createElement('input'); stack.type='hidden'; stack.name='__navigationButtonStack'; f.appendChild(stack); }
                    stack.value = (stack.value || '') + 'fwd;';
                    var fwd = f.querySelector("input[name='__fwd']");
                    if (!fwd) { fwd = document.createElement('input'); fwd.type='hidden'; fwd.name='__fwd'; fwd.value='1'; f.appendChild(fwd); }
                    f.submit();
                })();
            """)
            if self._wait_navigated(driver, old_form, 8):
                return True
        except JavascriptException:
            pass

        return False
