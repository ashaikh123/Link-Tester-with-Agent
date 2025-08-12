import time
from typing import List
from selenium.webdriver.remote.webelement import WebElement

def _js_set_select_value(driver, select_el: WebElement, value: str):
    driver.execute_script("""
        const sel = arguments[0], val = arguments[1];
        sel.value = val;
        const evt = new Event('change', { bubbles: true });
        sel.dispatchEvent(evt);
    """, select_el, value)

def answer_ranksort(select_elements: List[WebElement],
                              min_to_rank: int = 3,
                              driver=None,
                              DEBUG_MODE: bool = False) -> bool:
    try:
        # Keep only enabled elements
        selects = [s for s in select_elements if s.is_enabled()]
        if not selects:
            if DEBUG_MODE: print("RankSort: no enabled selects")
            return False

        # Which are unassigned? (value is "" or "-1")
        unassigned = []
        for s in selects:
            cur = (s.get_attribute("value") or "").strip()
            if cur in ("", "-1"):
                unassigned.append(s)

        if not unassigned:
            if DEBUG_MODE: print("RankSort: nothing to assign")
            return False

        # Probe options from the first select (don’t rely on visibility)
        # Read via JS to avoid stale/interactable issues
        options = driver.execute_script("""
            const sel = arguments[0];
            return Array.from(sel.options).map(o => ({value: o.value ?? "", text: (o.textContent||"").trim()}));
        """, unassigned[0]) if driver else []

        # valid ranks: skip placeholders (-1 / empty)
        rank_values = [o["value"] for o in options if o["value"] not in ("", "-1")]
        if not rank_values:
            if DEBUG_MODE: print("RankSort: no valid rank option values")
            return False

        to_assign = min(min_to_rank, len(rank_values), len(unassigned))
        used = set()

        for i in range(to_assign):
            select_el = unassigned[i]
            # pick first unused rank value
            choice = next((v for v in rank_values if v not in used), None)
            if choice is None:
                break

            # Scroll (helps some UIs even if hidden)
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", select_el)
            except: 
                pass

            # Set value via JS + dispatch change
            try:
                _js_set_select_value(driver, select_el, choice)
                used.add(choice)
                time.sleep(0.05)
            except Exception as e:
                if DEBUG_MODE: print(f"RankSort: JS set failed: {e}")
                # As a fallback, try native click only if displayed
                if select_el.is_displayed():
                    try:
                        # try selecting by index equal to the numeric value
                        driver.execute_script("arguments[0].click();", select_el)
                        # pick option via JS anyway (more reliable)
                        _js_set_select_value(driver, select_el, choice)
                        used.add(choice)
                    except Exception as e2:
                        if DEBUG_MODE: print(f"RankSort: fallback failed: {e2}")

        if DEBUG_MODE:
            print(f"✅ RankSort: assigned {len(used)} ranks -> {sorted(used)}")

        return len(used) > 0
    except Exception as e:
        print(f"⚠️ RankSort dropdown handler error: {e}")
        return False
