from pydantic import BaseModel

from runllm.constants.enums import FunctionType
from runllm.resources.parameters import (
    EmbedParams,
    GenerateParams,
    ReadParams,
    VectorDBRetrieveParams,
    VectorDBWriteParams,
)


class FunctionSpec(BaseModel):
    type: FunctionType = FunctionType.FILE
    # base64 encoded byte string
    file: str


class DefaultReadSpec(BaseModel):
    is_default_read: bool = True

    resource_id: int
    params: ReadParams


class DefaultEmbedSpec(BaseModel):
    is_default_embed: bool = True

    resource_id: int
    params: EmbedParams


class DefaultRetrieveSpec(BaseModel):
    is_default_retrieve: bool = True

    llm_resource_id: int
    llm_params: EmbedParams
    vector_db_resource_id: int
    vector_db_params: VectorDBRetrieveParams


class DefaultGenerateSpec(BaseModel):
    is_default_generate: bool = True

    resource_id: int
    params: GenerateParams


class DefaultWriteSpec(BaseModel):
    is_default_write: bool = True

    resource_id: int
    params: VectorDBWriteParams


class CustomSpec(BaseModel):
    is_custom: bool = True

    function_spec: FunctionSpec
