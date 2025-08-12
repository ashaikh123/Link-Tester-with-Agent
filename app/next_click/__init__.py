from .orchestrator import NextClickOrchestrator

def safe_click_next(driver, timeout: int = 3) -> bool:
    """Public API used by the rest of your code."""
    ok = NextClickOrchestrator().run(driver, timeout)
    if not ok:
        print("⚠️ Next click failed: no strategy succeeded")
    return ok
