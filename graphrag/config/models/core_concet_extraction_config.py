# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Parameterization settings for the default configuration."""

from pathlib import Path

from pydantic import Field

import graphrag.config.defaults as defs
from graphrag.config.models.llm_config import LLMConfig


class CoreConceptExtractionConfig(LLMConfig):
    """Configuration section for core concept reports."""

    prompt: str | None = Field(
        description="The core concept report extraction prompt to use.", default=None
    )
    max_length: int = Field(
        description="The core concept report maximum length in tokens.",
        default=defs.COMMUNITY_REPORT_MAX_LENGTH,
    )
    max_input_length: int = Field(
        description="The maximum input length in tokens to use when generating reports.",
        default=defs.COMMUNITY_REPORT_MAX_INPUT_LENGTH,
    )
    strategy: dict | None = Field(
        description="The override strategy to use.", default=None
    )

    def resolved_strategy(self, root_dir) -> dict:
        """Get the resolved community report extraction strategy."""
        from graphrag.index.operations.summarize_communities import (
            CoreConceptExtractionStrategyType,
        )

        return self.strategy or {
            "type": CoreConceptExtractionStrategyType.graph_intelligence,
            "llm": self.llm.model_dump(),
            **self.parallelization.model_dump(),
            "extraction_prompt": (Path(root_dir) / self.prompt)
            .read_bytes()
            .decode(encoding="utf-8")
            if self.prompt
            else None,
            "max_report_length": self.max_length,
            "max_input_length": self.max_input_length,
        }
