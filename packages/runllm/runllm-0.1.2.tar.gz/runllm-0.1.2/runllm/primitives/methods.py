from typing import Dict, Union, Any

from runllm.constants.enums import ImplementationType, ResourceType
from runllm.context import ContextKey
from runllm.primitives.custom_primitive import CustomPrimitive
from runllm.primitives.embed import EmbedPrimitive
from runllm.primitives.generate import GeneratePrimitive
from runllm.primitives.read import ReadPrimitive
from runllm.primitives.retrieve import RetrievePrimitive
from runllm.primitives.write import WritePrimitive
from runllm.resources.parameters import (
    EmbedParams,
    GenerateParams,
    GithubReadParams,
    GoogleDocsReadParams,
    NotionReadParams,
    ReadParams,
    RelationalDBReadParams,
    VectorDBRetrieveParams,
    VectorDBWriteParams,
)
from runllm.resources.resources import Resource


def read(
    resource: Resource,
    params: Union[ReadParams, Dict[str, Any]],
    implementation_type: ImplementationType = ImplementationType.DEFAULT,
) -> ReadPrimitive:
    """
    Create a ReadPrimitive instance to read data from the specified resource.

    Args:
        resource (Resource): The resource to read data from.
        params (Union[ReadParams, Dict]): Parameters for the read operation. Can be an instance of ReadParams or a dictionary.
        implementation_type (ImplementationType, optional): The type of implementation for the read operation. Defaults to ImplementationType.DEFAULT.

    Returns:
        ReadPrimitive: An instance of ReadPrimitive for the read operation.

    Raises:
        TypeError: If the provided params is not of type ReadParams.
        ValueError: If there is an error parsing the dictionary into ReadParams.
    """
    if isinstance(params, dict):
        try:
            if resource.type == ResourceType.GITHUB:
                params = GithubReadParams(**params)
            elif resource.type == ResourceType.GOOGLE_DOCS:
                params = GoogleDocsReadParams(**params)
            elif resource.type == ResourceType.NOTION:
                params = NotionReadParams(**params)
            elif resource.type == ResourceType.RELATIONAL_DB:
                params = RelationalDBReadParams(**params)
            else:
                raise TypeError(
                    f"Expected params to be of type ReadParams, got {type(params).__name__}"
                )
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into ReadParams: {e}")

    return ReadPrimitive(
        implementation_type=implementation_type,
        resource=resource,
        params=params,
    )


def embed(
    data: Union[ReadPrimitive, CustomPrimitive, ContextKey],
    resource: Resource,
    params: Union[EmbedParams, Dict[str, Any]],
    implementation_type: ImplementationType = ImplementationType.DEFAULT,
) -> EmbedPrimitive:
    """
    Create an EmbedPrimitive instance to embed data using the specified resource and parameters.

    Args:
        data (Union[ReadPrimitive, CustomPrimitive, ContextKey]): The data to embed. Can be an instance of ReadPrimitive, CustomPrimitive, or ContextKey.
        resource (Resource): The resource to use for embedding.
        params (Union[EmbedParams, Dict]): Parameters for the embedding operation.
        implementation_type (ImplementationType, optional): The type of implementation for the embedding operation. Defaults to ImplementationType.DEFAULT.

    Returns:
        EmbedPrimitive: An instance of EmbedPrimitive for the embedding operation.

    Raises:
        ValueError: If there is an error parsing the dictionary into EmbedParams.
        TypeError: If the provided params is not of type EmbedParams.
    """
    if isinstance(params, dict):
        try:
            params = EmbedParams(**params)
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into EmbedParams: {e}")

    if not isinstance(params, EmbedParams):
        raise TypeError(f"Expected params to be of type EmbedParams, got {type(params).__name__}")

    return EmbedPrimitive(
        data=data,
        implementation_type=implementation_type,
        resource=resource,
        params=params,
    )


def write(
    data: Union[EmbedPrimitive, CustomPrimitive, ContextKey],
    resource: Resource,
    params: Union[VectorDBWriteParams, Dict[str, Any]],
    implementation_type: ImplementationType = ImplementationType.DEFAULT,
) -> WritePrimitive:
    """
    Create a WritePrimitive instance to write data using the specified resource and parameters.

    Args:
        data (Union[EmbedPrimitive, CustomPrimitive, ContextKey]): The data to write. Can be an instance of EmbedPrimitive, CustomPrimitive, or ContextKey.
        resource (Resource): The resource to use for writing.
        params (Union[VectorDBWriteParams, Dict]): Parameters for the writing operation.
        implementation_type (ImplementationType, optional): The type of implementation for the writing operation. Defaults to ImplementationType.DEFAULT.

    Returns:
        WritePrimitive: An instance of WritePrimitive for the writing operation.

    Raises:
        ValueError: If there is an error parsing the dictionary into VectorDBWriteParams.
        TypeError: If the provided params is not of type VectorDBWriteParams.
    """
    if isinstance(params, dict):
        try:
            params = VectorDBWriteParams(**params)
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into VectorDBWriteParams: {e}")

    if not isinstance(params, VectorDBWriteParams):
        raise TypeError(
            f"Expected params to be of type VectorDBWriteParams, got {type(params).__name__}"
        )

    return WritePrimitive(
        data=data,
        implementation_type=implementation_type,
        resource=resource,
        params=params,
    )


def retrieve(
    data: Union[CustomPrimitive, ContextKey],
    llm_resource: Resource,
    llm_params: Union[EmbedParams, Dict[str, Any]],
    vector_db_resource: Resource,
    vector_db_params: Union[VectorDBRetrieveParams, Dict[str, Any]],
    implementation_type: ImplementationType = ImplementationType.DEFAULT,
) -> RetrievePrimitive:
    """
    Create a RetrievePrimitive instance to retrieve data using both LLM and VectorDB resources.

    Args:
        data (Union[CustomPrimitive, ContextKey]): The data to retrieve. Can be an instance of CustomPrimitive or ContextKey.
        llm_resource (Resource): The LLM resource to use for retrieving contextual data.
        llm_params (Union[EmbedParams, Dict]): Parameters for the LLM retrieval operation.
        vector_db_resource (Resource): The VectorDB resource to use for retrieving data.
        vector_db_params (Union[VectorDBRetrieveParams, Dict]): Parameters for the VectorDB retrieval operation.
        implementation_type (ImplementationType, optional): The type of implementation for the retrieval operation. Defaults to ImplementationType.DEFAULT.

    Returns:
        RetrievePrimitive: An instance of RetrievePrimitive for the retrieval operation.

    Raises:
        ValueError: If there is an error parsing the dictionary into EmbedParams or VectorDBRetrieveParams.
        TypeError: If the provided params are not of type EmbedParams or VectorDBRetrieveParams.
    """
    if isinstance(llm_params, dict):
        try:
            llm_params = EmbedParams(**llm_params)
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into EmbedParams: {e}")

    if isinstance(vector_db_params, dict):
        try:
            vector_db_params = VectorDBRetrieveParams(**vector_db_params)
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into VectorDBRetrieveParams: {e}")

    if not isinstance(llm_params, EmbedParams):
        raise TypeError(
            f"Expected params to be of type EmbedParams, got {type(llm_params).__name__}"
        )

    if not isinstance(vector_db_params, VectorDBRetrieveParams):
        raise TypeError(
            f"Expected params to be of type VectorDBRetrieveParams, got {type(llm_params).__name__}"
        )

    return RetrievePrimitive(
        data=data,
        implementation_type=implementation_type,
        llm_resource=llm_resource,
        llm_params=llm_params,
        vector_db_resource=vector_db_resource,
        vector_db_params=vector_db_params,
    )


def generate(
    data: Union[CustomPrimitive, ContextKey],
    resource: Resource,
    params: Union[GenerateParams, Dict[str, Any]],
    implementation_type: ImplementationType = ImplementationType.DEFAULT,
) -> GeneratePrimitive:
    """
    Create a GeneratePrimitive instance to generate data using the specified resource and parameters.

    Args:
        data (Union[CustomPrimitive, ContextKey]): The data to generate. Can be an instance of CustomPrimitive or ContextKey.
        resource (Resource): The resource to use for data generation.
        params (Union[GenerateParams, Dict]): Parameters for the data generation operation.
        implementation_type (ImplementationType, optional): The type of implementation for the data generation operation. Defaults to ImplementationType.DEFAULT.

    Returns:
        GeneratePrimitive: An instance of GeneratePrimitive for the data generation operation.

    Raises:
        ValueError: If there is an error parsing the dictionary into GenerateParams.
        TypeError: If the provided params is not of type GenerateParams.
    """
    if isinstance(params, dict):
        try:
            params = GenerateParams(**params)
        except Exception as e:
            raise ValueError(f"Error parsing dictionary into GenerateParams: {e}")

    if not isinstance(params, GenerateParams):
        raise TypeError(
            f"Expected params to be of type GenerateParams, got {type(params).__name__}"
        )

    return GeneratePrimitive(
        data=data,
        implementation_type=implementation_type,
        resource=resource,
        params=params,
    )
