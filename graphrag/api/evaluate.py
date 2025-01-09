# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""
Evaluating Engine API.

This API provides access to the query engine of graphrag, allowing external applications
to hook into graphrag and run queries over a knowledge graph generated by graphrag.

Contains the following functions:
 - global_search: Perform a global search.
 - global_search_streaming: Perform a global search and stream results back.
 - local_search: Perform a local search.
 - local_search_streaming: Perform a local search and stream results back.

WARNING: This API is under development and may undergo changes in future releases.
Backwards compatibility is not guaranteed at this time.
"""

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from pydantic import validate_call

from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.index.config.embeddings import (
    community_full_content_embedding,
    entity_description_embedding,
)
from graphrag.logger.print_progress import PrintProgressLogger
from graphrag.query.factory import (
    get_drift_search_engine,
    get_global_search_engine,
    get_local_search_engine,
)
from graphrag.query.indexer_adapters import (
    read_indexer_communities,
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_report_embeddings,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.utils.cli import redact
from graphrag.utils.embeddings import create_collection_name
from graphrag.vector_stores.base import BaseVectorStore
from graphrag.vector_stores.factory import VectorStoreFactory

if TYPE_CHECKING:
    from graphrag.query.structured_search.base import SearchResult

logger = PrintProgressLogger("")


@validate_call(config={"arbitrary_types_allowed": True})
async def global_search(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    communities: pd.DataFrame,
    community_reports: pd.DataFrame,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    query: str,
) -> tuple[
    str | dict[str, Any] | list[dict[str, Any]],
    str | list[pd.DataFrame] | dict[str, pd.DataFrame],
]:
    """Perform a global search and return the context data and response.

    Parameters
    ----------
    - config (GraphRagConfig): A graphrag configuration (from settings.yaml)
    - nodes (pd.DataFrame): A DataFrame containing the final nodes (from create_final_nodes.parquet)
    - entities (pd.DataFrame): A DataFrame containing the final entities (from create_final_entities.parquet)
    - communities (pd.DataFrame): A DataFrame containing the final communities (from create_final_communities.parquet)
    - community_reports (pd.DataFrame): A DataFrame containing the final community reports (from create_final_community_reports.parquet)
    - community_level (int): The community level to search at.
    - dynamic_community_selection (bool): Enable dynamic community selection instead of using all community reports at a fixed level. Note that you can still provide community_level cap the maximum level to search.
    - response_type (str): The type of response to return.
    - query (str): The user query to search for.

    Returns
    -------
    TODO: Document the search response type and format.

    Raises
    ------
    TODO: Document any exceptions to expect.
    """
    communities_ = read_indexer_communities(communities, nodes, community_reports)
    reports = read_indexer_reports(
        community_reports,
        nodes,
        community_level=community_level,
        dynamic_community_selection=dynamic_community_selection,
    )
    entities_ = read_indexer_entities(nodes, entities, community_level=community_level)
    map_prompt = _load_search_prompt(config.root_dir, config.global_search.map_prompt)
    reduce_prompt = _load_search_prompt(
        config.root_dir, config.global_search.reduce_prompt
    )
    knowledge_prompt = _load_search_prompt(
        config.root_dir, config.global_search.knowledge_prompt
    )

    search_engine = get_global_search_engine(
        config,
        reports=reports,
        entities=entities_,
        communities=communities_,
        response_type=response_type,
        dynamic_community_selection=dynamic_community_selection,
        map_system_prompt=map_prompt,
        reduce_system_prompt=reduce_prompt,
        general_knowledge_inclusion_prompt=knowledge_prompt,
    )
    result: SearchResult = await search_engine.asearch(query=query)
    response = result.response
    context_data = _reformat_context_data(result.context_data)  # type: ignore
    return response, context_data


@validate_call(config={"arbitrary_types_allowed": True})
async def global_search_streaming(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    communities: pd.DataFrame,
    community_reports: pd.DataFrame,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    query: str,
) -> AsyncGenerator:
    """Perform a global search and return the context data and response via a generator.

    Context data is returned as a dictionary of lists, with one list entry for each record.

    Parameters
    ----------
    - config (GraphRagConfig): A graphrag configuration (from settings.yaml)
    - nodes (pd.DataFrame): A DataFrame containing the final nodes (from create_final_nodes.parquet)
    - entities (pd.DataFrame): A DataFrame containing the final entities (from create_final_entities.parquet)
    - communities (pd.DataFrame): A DataFrame containing the final communities (from create_final_communities.parquet)
    - community_reports (pd.DataFrame): A DataFrame containing the final community reports (from create_final_community_reports.parquet)
    - community_level (int): The community level to search at.
    - dynamic_community_selection (bool): Enable dynamic community selection instead of using all community reports at a fixed level. Note that you can still provide community_level cap the maximum level to search.
    - response_type (str): The type of response to return.
    - query (str): The user query to search for.

    Returns
    -------
    TODO: Document the search response type and format.

    Raises
    ------
    TODO: Document any exceptions to expect.
    """
    communities_ = read_indexer_communities(communities, nodes, community_reports)
    reports = read_indexer_reports(
        community_reports,
        nodes,
        community_level=community_level,
        dynamic_community_selection=dynamic_community_selection,
    )
    entities_ = read_indexer_entities(nodes, entities, community_level=community_level)
    map_prompt = _load_search_prompt(config.root_dir, config.global_search.map_prompt)
    reduce_prompt = _load_search_prompt(
        config.root_dir, config.global_search.reduce_prompt
    )
    knowledge_prompt = _load_search_prompt(
        config.root_dir, config.global_search.knowledge_prompt
    )

    search_engine = get_global_search_engine(
        config,
        reports=reports,
        entities=entities_,
        communities=communities_,
        response_type=response_type,
        dynamic_community_selection=dynamic_community_selection,
        map_system_prompt=map_prompt,
        reduce_system_prompt=reduce_prompt,
        general_knowledge_inclusion_prompt=knowledge_prompt,
    )
    search_result = search_engine.astream_search(query=query)

    # when streaming results, a context data object is returned as the first result
    # and the query response in subsequent tokens
    context_data = None
    get_context_data = True
    async for stream_chunk in search_result:
        if get_context_data:
            context_data = _reformat_context_data(stream_chunk)  # type: ignore
            yield context_data
            get_context_data = False
        else:
            yield stream_chunk


@validate_call(config={"arbitrary_types_allowed": True})
async def local_search(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    community_reports: pd.DataFrame,
    text_units: pd.DataFrame,
    relationships: pd.DataFrame,
    covariates: pd.DataFrame | None,
    community_level: int,
    response_type: str,
    query: str,
) -> tuple[
    str | dict[str, Any] | list[dict[str, Any]],
    str | list[pd.DataFrame] | dict[str, pd.DataFrame],
]:
    """Perform a local search and return the context data and response.

    Parameters
    ----------
    - config (GraphRagConfig): A graphrag configuration (from settings.yaml)
    - nodes (pd.DataFrame): A DataFrame containing the final nodes (from create_final_nodes.parquet)
    - entities (pd.DataFrame): A DataFrame containing the final entities (from create_final_entities.parquet)
    - community_reports (pd.DataFrame): A DataFrame containing the final community reports (from create_final_community_reports.parquet)
    - text_units (pd.DataFrame): A DataFrame containing the final text units (from create_final_text_units.parquet)
    - relationships (pd.DataFrame): A DataFrame containing the final relationships (from create_final_relationships.parquet)
    - covariates (pd.DataFrame): A DataFrame containing the final covariates (from create_final_covariates.parquet)
    - community_level (int): The community level to search at.
    - response_type (str): The response type to return.
    - query (str): The user query to search for.

    Returns
    -------
    TODO: Document the search response type and format.

    Raises
    ------
    TODO: Document any exceptions to expect.
    """
    vector_store_args = config.embeddings.vector_store
    logger.info(f"Vector Store Args: {redact(vector_store_args)}")  # type: ignore # noqa

    description_embedding_store = _get_embedding_store(
        config_args=vector_store_args,  # type: ignore
        embedding_name=entity_description_embedding,
    )

    entities_ = read_indexer_entities(nodes, entities, community_level)
    covariates_ = read_indexer_covariates(covariates) if covariates is not None else []
    prompt = _load_search_prompt(config.root_dir, config.local_search.prompt)

    search_engine = get_local_search_engine(
        config=config,
        reports=read_indexer_reports(community_reports, nodes, community_level),
        text_units=read_indexer_text_units(text_units),
        entities=entities_,
        relationships=read_indexer_relationships(relationships),
        covariates={"claims": covariates_},
        description_embedding_store=description_embedding_store,  # type: ignore
        response_type=response_type,
        system_prompt=prompt,
    )

    result: SearchResult = await search_engine.asearch(query=query)
    response = result.response
    context_data = _reformat_context_data(result.context_data)  # type: ignore
    return response, context_data


@validate_call(config={"arbitrary_types_allowed": True})
async def local_search_streaming(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    community_reports: pd.DataFrame,
    text_units: pd.DataFrame,
    relationships: pd.DataFrame,
    covariates: pd.DataFrame | None,
    community_level: int,
    response_type: str,
    query: str,
) -> AsyncGenerator:
    """Perform a local search and return the context data and response via a generator.

    Parameters
    ----------
    - config (GraphRagConfig): A graphrag configuration (from settings.yaml)
    - nodes (pd.DataFrame): A DataFrame containing the final nodes (from create_final_nodes.parquet)
    - entities (pd.DataFrame): A DataFrame containing the final entities (from create_final_entities.parquet)
    - community_reports (pd.DataFrame): A DataFrame containing the final community reports (from create_final_community_reports.parquet)
    - text_units (pd.DataFrame): A DataFrame containing the final text units (from create_final_text_units.parquet)
    - relationships (pd.DataFrame): A DataFrame containing the final relationships (from create_final_relationships.parquet)
    - covariates (pd.DataFrame): A DataFrame containing the final covariates (from create_final_covariates.parquet)
    - community_level (int): The community level to search at.
    - response_type (str): The response type to return.
    - query (str): The user query to search for.

    Returns
    -------
    TODO: Document the search response type and format.

    Raises
    ------
    TODO: Document any exceptions to expect.
    """
    vector_store_args = config.embeddings.vector_store
    logger.info(f"Vector Store Args: {redact(vector_store_args)}")  # type: ignore # noqa

    description_embedding_store = _get_embedding_store(
        config_args=vector_store_args,  # type: ignore
        embedding_name=entity_description_embedding,
    )

    entities_ = read_indexer_entities(nodes, entities, community_level)
    covariates_ = read_indexer_covariates(covariates) if covariates is not None else []
    prompt = _load_search_prompt(config.root_dir, config.local_search.prompt)

    search_engine = get_local_search_engine(
        config=config,
        reports=read_indexer_reports(community_reports, nodes, community_level),
        text_units=read_indexer_text_units(text_units),
        entities=entities_,
        relationships=read_indexer_relationships(relationships),
        covariates={"claims": covariates_},
        description_embedding_store=description_embedding_store,  # type: ignore
        response_type=response_type,
        system_prompt=prompt,
    )
    search_result = search_engine.astream_search(query=query)

    # when streaming results, a context data object is returned as the first result
    # and the query response in subsequent tokens
    context_data = None
    get_context_data = True
    async for stream_chunk in search_result:
        if get_context_data:
            context_data = _reformat_context_data(stream_chunk)  # type: ignore
            yield context_data
            get_context_data = False
        else:
            yield stream_chunk


@validate_call(config={"arbitrary_types_allowed": True})
async def drift_search(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    community_reports: pd.DataFrame,
    text_units: pd.DataFrame,
    relationships: pd.DataFrame,
    community_level: int,
    query: str,
) -> tuple[
    str | dict[str, Any] | list[dict[str, Any]],
    str | list[pd.DataFrame] | dict[str, pd.DataFrame],
]:
    """Perform a DRIFT search and return the context data and response.

    Parameters
    ----------
    - config (GraphRagConfig): A graphrag configuration (from settings.yaml)
    - nodes (pd.DataFrame): A DataFrame containing the final nodes (from create_final_nodes.parquet)
    - entities (pd.DataFrame): A DataFrame containing the final entities (from create_final_entities.parquet)
    - community_reports (pd.DataFrame): A DataFrame containing the final community reports (from create_final_community_reports.parquet)
    - text_units (pd.DataFrame): A DataFrame containing the final text units (from create_final_text_units.parquet)
    - relationships (pd.DataFrame): A DataFrame containing the final relationships (from create_final_relationships.parquet)
    - community_level (int): The community level to search at.
    - query (str): The user query to search for.

    Returns
    -------
    TODO: Document the search response type and format.

    Raises
    ------
    TODO: Document any exceptions to expect.
    """
    vector_store_args = config.embeddings.vector_store
    logger.info(f"Vector Store Args: {redact(vector_store_args)}")  # type: ignore # noqa

    description_embedding_store = _get_embedding_store(
        config_args=vector_store_args,  # type: ignore
        embedding_name=entity_description_embedding,
    )

    full_content_embedding_store = _get_embedding_store(
        config_args=vector_store_args,  # type: ignore
        embedding_name=community_full_content_embedding,
    )

    entities_ = read_indexer_entities(nodes, entities, community_level)
    reports = read_indexer_reports(community_reports, nodes, community_level)
    read_indexer_report_embeddings(reports, full_content_embedding_store)
    prompt = _load_search_prompt(config.root_dir, config.drift_search.prompt)
    search_engine = get_drift_search_engine(
        config=config,
        reports=reports,
        text_units=read_indexer_text_units(text_units),
        entities=entities_,
        relationships=read_indexer_relationships(relationships),
        description_embedding_store=description_embedding_store,  # type: ignore
        local_system_prompt=prompt,
    )

    result: SearchResult = await search_engine.asearch(query=query)
    response = result.response
    context_data = _reformat_context_data(result.context_data)  # type: ignore

    # TODO: Map/reduce the response to a single string with a comprehensive answer including all follow-ups
    # For the time being, return highest scoring response (position 0) and context data
    match response:
        case dict():
            return response["nodes"][0]["answer"], context_data  # type: ignore
        case str():
            return response, context_data
        case list():
            return response, context_data


def _get_embedding_store(
    config_args: dict,
    embedding_name: str,
) -> BaseVectorStore:
    """Get the embedding description store."""
    vector_store_type = config_args["type"]
    collection_name = create_collection_name(
        config_args.get("container_name", "default"), embedding_name
    )
    embedding_store = VectorStoreFactory().create_vector_store(
        vector_store_type=vector_store_type,
        kwargs={**config_args, "collection_name": collection_name},
    )
    embedding_store.connect(**config_args)
    return embedding_store


def _reformat_context_data(context_data: dict) -> dict:
    """
    Reformats context_data for all query responses.

    Reformats a dictionary of dataframes into a dictionary of lists.
    One list entry for each record. Records are grouped by original
    dictionary keys.

    Note: depending on which query algorithm is used, the context_data may not
          contain the same information (keys). In this case, the default behavior will be to
          set these keys as empty lists to preserve a standard output format.
    """
    final_format = {
        "reports": [],
        "entities": [],
        "relationships": [],
        "claims": [],
        "sources": [],
    }
    for key in context_data:
        records = (
            context_data[key].to_dict(orient="records")
            if context_data[key] is not None and not isinstance(context_data[key], dict)
            else context_data[key]
        )
        if len(records) < 1:
            continue
        final_format[key] = records
    return final_format


def _load_search_prompt(root_dir: str, prompt_config: str | None) -> str | None:
    """
    Load the search prompt from disk if configured.

    If not, leave it empty - the search functions will load their defaults.

    """
    if prompt_config:
        prompt_file = Path(root_dir) / prompt_config
        if prompt_file.exists():
            return prompt_file.read_bytes().decode(encoding="utf-8")
    return None
