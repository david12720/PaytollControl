from abc import ABC, abstractmethod


class CostLogger(ABC):
    @abstractmethod
    def log(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """Log an API call with token counts and compute cost."""

    @abstractmethod
    def summary(self) -> None:
        """Print a summary of all logged costs in this session."""
