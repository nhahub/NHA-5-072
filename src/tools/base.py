import time
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from src.models.evidence import EvidenceRecord

class ToolResult(BaseModel):
    """Normalized result returned by any tool in Atlas AQAR."""
    success: bool
    data: Any = None
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    error_message: str | None = None
    execution_time_ms: float = 0.0

class BaseTool(ABC):
    """Abstract base class for all deterministic and retrieval tools."""
    name: str
    description: str
    parameters_schema: type[BaseModel]

    def run(self, **kwargs: Any) -> ToolResult:
        """Validates input against parameters_schema, measures runtime, and invokes execute."""
        start_time = time.perf_counter()
        try:
            validated_params = self.parameters_schema(**kwargs)
            result = self.execute(validated_params)
            result.execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return result
        except Exception as e:
            elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ToolResult(
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed,
            )

    @abstractmethod
    def execute(self, params: Any) -> ToolResult:
        """Concrete execution logic implemented by child classes."""
        pass
