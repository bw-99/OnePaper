# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing run, _run_extractor and _load_nodes_edges_for_claim_chain methods definition."""

import logging
import traceback

from datashaper import VerbCallbacks
from fnllm import ChatLLM

from graphrag.cache.pipeline_cache import PipelineCache
from graphrag.index.llm.load_llm import load_llm, read_llm_params
from graphrag.index.operations.summarize_communities.community_reports_extractor.keyword_extractor import KeywordReportsExtractor
from graphrag.index.operations.summarize_communities.typing import (
    KeywordReport,
    Finding,
    StrategyConfig,
)
from graphrag.index.utils.rate_limiter import RateLimiter

DEFAULT_CHUNK_SIZE = 3000

log = logging.getLogger(__name__)


async def run_graph_intelligence(
    community: str | int,
    input: str,
    callbacks: VerbCallbacks,
    cache: PipelineCache,
    args: StrategyConfig,
) -> KeywordReport | None:
    """Run the graph intelligence entity extraction strategy."""
    llm_config = read_llm_params(args.get("llm", {}))
    llm = load_llm("keyword_reporting", llm_config, callbacks=callbacks, cache=cache)
    return await _run_extractor(llm, community, input, args, callbacks)


async def _run_extractor(
    llm: ChatLLM,
    community: str | int,
    input: str,
    args: StrategyConfig,
    callbacks: VerbCallbacks,
) -> KeywordReport | None:
    # RateLimiter
    rate_limiter = RateLimiter(rate=1, per=60)
    extractor = KeywordReportsExtractor(
        llm,
        extraction_prompt=args.get("extraction_prompt", None),
        max_report_length=args.get("max_report_length", None),
        on_error=lambda e, stack, _data: callbacks.error(
            "Keyword Report Extraction Error", e, stack
        ),
    )

    try:
        await rate_limiter.acquire()
        results = await extractor({"input_text": input})
        report = results.structured_output
        if report is None:
            log.warning("No keyword found for community: %s", community)
            return None

        return KeywordReport(
            community=community,
            keyword=report.keyword,
            keyword_explanation=report.keyword_explanation,
        )
    except Exception as e:
        log.exception("Error processing community: %s", community)
        callbacks.error("Keyword Report Extraction Error", e, traceback.format_exc())
        return None
