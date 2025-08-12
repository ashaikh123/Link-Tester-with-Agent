from typing import List, Optional
from .strategies import (
    NextClickStrategy,
    DecipherStrategy,
    AlchemerStrategy,
    ConfirmitStrategy,
    GenericEnterFallbackStrategy,
)

class NextClickOrchestrator:
    def __init__(self, strategies: Optional[List[NextClickStrategy]] = None):
        self.strategies = strategies or [
            DecipherStrategy(),
            AlchemerStrategy(),
            ConfirmitStrategy(),
            GenericEnterFallbackStrategy(),
        ]

    def run(self, driver, timeout: int = 3) -> bool:
        for strat in self.strategies:
            try:
                if strat.matches(driver):
                    if strat.click_next(driver, timeout):
                        return True
            except Exception:
                # keep trying the next strategy
                continue
        return False
