from typing import List, Tuple

from runllm.constants.enums import PrimitiveType, ResourceType, Service

input_types = {
    PrimitiveType.READ: None,
    PrimitiveType.EMBED: List[str],
    PrimitiveType.WRITE: List[Tuple[List[float], str]],
    PrimitiveType.RETRIEVE: str,
    PrimitiveType.GENERATE: str,
}

output_types = {
    PrimitiveType.READ: List[str],
    PrimitiveType.EMBED: List[Tuple[List[float], str]],
    PrimitiveType.WRITE: None,
    PrimitiveType.RETRIEVE: List[str],
    PrimitiveType.GENERATE: str,
}

service_to_resource_type = {
    Service.SNOWFLAKE: ResourceType.RELATIONAL_DB,
    Service.POSTGRES: ResourceType.RELATIONAL_DB,
    Service.MYSQL: ResourceType.RELATIONAL_DB,
    Service.MARIADB: ResourceType.RELATIONAL_DB,
    Service.BIGQUERY: ResourceType.RELATIONAL_DB,
    Service.SQLITE: ResourceType.RELATIONAL_DB,
    Service.OPENAI: ResourceType.LLM,
    Service.HUGGINGFACE: ResourceType.LLM,
    Service.NOTION: ResourceType.NOTION,
    Service.GITHUB: ResourceType.GITHUB,
    Service.GOOGLEDOCS: ResourceType.GOOGLE_DOCS,
    Service.CHROMA: ResourceType.VECTOR_DB,
    Service.PINECONE: ResourceType.VECTOR_DB,
    Service.WEAVIATE: ResourceType.VECTOR_DB,
}
