from typing import Optional, Union

from pydantic import BaseModel, Extra

from runllm.constants.enums import (
    EmbeddingModelType,
    LLMModelType,
    NotionDocumentType,
    VectorDBUpdateType,
)


class ResourceParams(BaseModel):
    class Config:
        extra = Extra.forbid


"""Resource parameters for Read primitive"""


class NotionReadParams(ResourceParams):
    document_type: NotionDocumentType
    url: str


class GoogleDocsReadParams(ResourceParams):
    url: str


class GithubReadParams(ResourceParams):
    owner: str
    repo: str
    branch: Optional[str] = None


class RelationalDBReadParams(ResourceParams):
    query: str


ReadParams = Union[NotionReadParams, GoogleDocsReadParams, GithubReadParams, RelationalDBReadParams]


"""Resource parameters for Write primitive
Note that in the current design, we only support writing to Vector databases"""


class VectorDBWriteParams(ResourceParams):
    index_name: str
    mode: VectorDBUpdateType


"""Resource parameters for Embed primitive"""


class EmbedParams(ResourceParams):
    # See runllm.constants.enums.OpenAIEmbeddingModelType for the list of supported models
    model: EmbeddingModelType


"""Resource parameters for Retrieve primitive"""


class VectorDBRetrieveParams(ResourceParams):
    index_name: str
    max_num_documents: int = 2  # this is the default value in llama-index


"""Resource parameters for Generate primitive"""


class GenerateParams(ResourceParams):
    model: LLMModelType
    token_limit: int
    prompt_template: Optional[str] = None
