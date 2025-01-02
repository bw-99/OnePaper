# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Common default configuration values."""

from pathlib import Path

from datashaper import AsyncType

from graphrag.config.enums import (
    CacheType,
    InputFileType,
    InputType,
    LLMType,
    ReportingType,
    StorageType,
    TextEmbeddingTarget,
)
from graphrag.vector_stores.factory import VectorStoreType

ASYNC_MODE = AsyncType.Threaded
ENCODING_MODEL = "cl100k_base"
AZURE_AUDIENCE = "https://cognitiveservices.azure.com/.default"
#
# LLM Parameters
#
LLM_FREQUENCY_PENALTY = 0.0
LLM_TYPE = LLMType.OpenAIChat
LLM_MODEL = "gpt-4-turbo-preview"
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0
LLM_TOP_P = 1
LLM_N = 1
LLM_REQUEST_TIMEOUT = 180.0
LLM_TOKENS_PER_MINUTE = 0
LLM_REQUESTS_PER_MINUTE = 0
LLM_MAX_RETRIES = 10
LLM_MAX_RETRY_WAIT = 10.0
LLM_PRESENCE_PENALTY = 0.0
LLM_SLEEP_ON_RATE_LIMIT_RECOMMENDATION = True
LLM_CONCURRENT_REQUESTS = 25

#
# Text Embedding Parameters
#
EMBEDDING_TYPE = LLMType.OpenAIEmbedding
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 16
EMBEDDING_BATCH_MAX_TOKENS = 8191
EMBEDDING_TARGET = TextEmbeddingTarget.required

CACHE_TYPE = CacheType.file
CACHE_BASE_DIR = "cache"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 100
CHUNK_GROUP_BY_COLUMNS = ["id"]
CLAIM_DESCRIPTION = (
    "Any claims or facts that could be relevant to information discovery."
)
CLAIM_MAX_GLEANINGS = 1
CLAIM_EXTRACTION_ENABLED = False
MAX_CLUSTER_SIZE = 10
COMMUNITY_REPORT_MAX_LENGTH = 2000
COMMUNITY_REPORT_MAX_INPUT_LENGTH = 8000
KEYWORD_REPORT_MAX_LENGTH = 2000
KEYWORD_REPORT_MAX_INPUT_LENGTH = 8000
ENTITY_EXTRACTION_ENTITY_TYPES = ["organization", "person", "geo", "event"]
ENTITY_EXTRACTION_MAX_GLEANINGS = 1
INPUT_FILE_TYPE = InputFileType.text
INPUT_TYPE = InputType.file
INPUT_BASE_DIR = "input"
INPUT_FILE_ENCODING = "utf-8"
INPUT_TEXT_COLUMN = "text"
INPUT_CSV_PATTERN = ".*\\.csv$"
INPUT_TEXT_PATTERN = ".*\\.txt$"
PARALLELIZATION_STAGGER = 0.3
PARALLELIZATION_NUM_THREADS = 50
NODE2VEC_ENABLED = False
NODE2VEC_NUM_WALKS = 10
NODE2VEC_WALK_LENGTH = 40
NODE2VEC_WINDOW_SIZE = 2
NODE2VEC_ITERATIONS = 3
NODE2VEC_RANDOM_SEED = 597832
REPORTING_TYPE = ReportingType.file
REPORTING_BASE_DIR = "logs"
SNAPSHOTS_GRAPHML = False
SNAPSHOTS_EMBEDDINGS = False
SNAPSHOTS_TRANSIENT = False
STORAGE_BASE_DIR = "output"
STORAGE_TYPE = StorageType.file
SUMMARIZE_DESCRIPTIONS_MAX_LENGTH = 500
UMAP_ENABLED = False
UPDATE_STORAGE_BASE_DIR = "update_output"

VECTOR_STORE = f"""
    type: {VectorStoreType.LanceDB.value}
    db_uri: '{(Path(STORAGE_BASE_DIR) / "lancedb")!s}'
    container_name: default
    overwrite: true\
"""

VECTOR_STORE_DICT = {
    "type": VectorStoreType.LanceDB.value,
    "db_uri": str(Path(STORAGE_BASE_DIR) / "lancedb"),
    "container_name": "default",
    "overwrite": True,
}

# Local Search
LOCAL_SEARCH_TEXT_UNIT_PROP = 0.5
LOCAL_SEARCH_COMMUNITY_PROP = 0.1
LOCAL_SEARCH_CONVERSATION_HISTORY_MAX_TURNS = 5
LOCAL_SEARCH_TOP_K_MAPPED_ENTITIES = 10
LOCAL_SEARCH_TOP_K_RELATIONSHIPS = 10
LOCAL_SEARCH_MAX_TOKENS = 12_000
LOCAL_SEARCH_LLM_TEMPERATURE = 0
LOCAL_SEARCH_LLM_TOP_P = 1
LOCAL_SEARCH_LLM_N = 1
LOCAL_SEARCH_LLM_MAX_TOKENS = 2000

# Global Search
GLOBAL_SEARCH_LLM_TEMPERATURE = 0
GLOBAL_SEARCH_LLM_TOP_P = 1
GLOBAL_SEARCH_LLM_N = 1
GLOBAL_SEARCH_MAX_TOKENS = 12_000
GLOBAL_SEARCH_DATA_MAX_TOKENS = 12_000
GLOBAL_SEARCH_MAP_MAX_TOKENS = 1000
GLOBAL_SEARCH_REDUCE_MAX_TOKENS = 2_000
GLOBAL_SEARCH_CONCURRENCY = 32

# Global Search with dynamic community selection
DYNAMIC_SEARCH_LLM_MODEL = "gpt-4o-mini"
DYNAMIC_SEARCH_RATE_THRESHOLD = 1
DYNAMIC_SEARCH_KEEP_PARENT = False
DYNAMIC_SEARCH_NUM_REPEATS = 1
DYNAMIC_SEARCH_USE_SUMMARY = False
DYNAMIC_SEARCH_CONCURRENT_COROUTINES = 16
DYNAMIC_SEARCH_MAX_LEVEL = 2

# DRIFT Search
DRIFT_SEARCH_LLM_TEMPERATURE = 0
DRIFT_SEARCH_LLM_TOP_P = 1
DRIFT_SEARCH_LLM_N = 3
DRIFT_SEARCH_MAX_TOKENS = 12_000
DRIFT_SEARCH_DATA_MAX_TOKENS = 12_000
DRIFT_SEARCH_CONCURRENCY = 32

DRIFT_SEARCH_K_FOLLOW_UPS = 20
DRIFT_SEARCH_PRIMER_FOLDS = 5
DRIFT_SEARCH_PRIMER_MAX_TOKENS = 12_000

DRIFT_LOCAL_SEARCH_TEXT_UNIT_PROP = 0.9
DRIFT_LOCAL_SEARCH_COMMUNITY_PROP = 0.1
DRIFT_LOCAL_SEARCH_TOP_K_MAPPED_ENTITIES = 10
DRIFT_LOCAL_SEARCH_TOP_K_RELATIONSHIPS = 10
DRIFT_LOCAL_SEARCH_MAX_TOKENS = 12_000
DRIFT_LOCAL_SEARCH_LLM_TEMPERATURE = 0
DRIFT_LOCAL_SEARCH_LLM_TOP_P = 1
DRIFT_LOCAL_SEARCH_LLM_N = 1
DRIFT_LOCAL_SEARCH_LLM_MAX_TOKENS = 2000

DRIFT_N_DEPTH = 3
