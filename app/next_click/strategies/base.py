from abc import ABC, abstractmethod

class NextClickStrategy(ABC):
    name: str = "base"

    @abstractmethod
    def matches(self, driver) -> bool: ...
    @abstractmethod
    def click_next(self, driver, timeout: int) -> bool: ...
