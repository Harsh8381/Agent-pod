from abc import ABC, abstractmethod

from app.models.encounter import EncounterContext


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, context: EncounterContext) -> EncounterContext:
        """Read and update the shared encounter context."""