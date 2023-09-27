from enum import Enum, EnumMeta
from typing import Any, Iterable, Union, cast

"""
All these enums can be replaced with protobufs for consistency with the backend.
"""


class MetaEnum(EnumMeta):
    """Allows to very easily check if strings are present in the enum, without a helper.

    Eg.
        if "batch" in Mode:
            ...
    """

    def __contains__(cls, item: Any) -> Any:
        return item in [v.value for v in cast(Iterable[Enum], cls.__members__.values())]


class Mode(str, Enum, metaclass=MetaEnum):
    BATCH = "batch"
    REAL_TIME = "real_time"


class NotionDocumentType(str, Enum, metaclass=MetaEnum):
    PAGE = "page"
    DATABASE = "database"


class VectorDBUpdateType(str, Enum, metaclass=MetaEnum):
    APPEND = "append"
    REPLACE = "replace"


class Service(str, Enum, metaclass=MetaEnum):
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    BIGQUERY = "bigquery"
    SQLITE = "sqlite"
    S3 = "s3"
    NOTION = "notion"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    GITHUB = "github"
    GOOGLEDOCS = "googledocs"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"


class ResourceType(str, Enum, metaclass=MetaEnum):
    LLM = "llm"
    VECTOR_DB = "vector_db"
    NOTION = "notion"
    GOOGLE_DOCS = "google_docs"
    GITHUB = "github"
    RELATIONAL_DB = "relational_db"


class PrimitiveType(str, Enum, metaclass=MetaEnum):
    READ = "read"
    WRITE = "write"
    EMBED = "embed"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    CUSTOM = "custom"


class ImplementationType(str, Enum, metaclass=MetaEnum):
    DEFAULT = "default"
    LLAMA_INDEX = "llama_index"
    LANGCHAN = "langchain"
    CUSTOM = "custom"


class FunctionType(str, Enum, metaclass=MetaEnum):
    FILE = "file"


# Copied from https://github.com/jerryjliu/llama_index/blob/main/llama_index/embeddings/openai.py
# But since OpenAI recommend only the second generation model, we only support that.
class OpenAIEmbeddingModelType(str, Enum, metaclass=MetaEnum):
    """OpenAI embedding model type."""

    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"


EmbeddingModelType = Union[OpenAIEmbeddingModelType]


# Pulled from all non-legacy models listed at https://platform.openai.com/docs/models/overview.
# Last updated: 2023-09-13
class OpenAIGPTModelType(str, Enum, metaclass=MetaEnum):
    """These are all the supported OpenAI models a user can use."""

    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_35_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT_35_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT_35_TURBO_16K_0613 = "gpt-3.5-turbo-16k-0613"
    GPT_4 = "gpt-4"
    GPT_4_0613 = "gpt-4-0613"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_32K_0613 = "gpt-4-32k-0613"


LLMModelType = Union[OpenAIGPTModelType]
