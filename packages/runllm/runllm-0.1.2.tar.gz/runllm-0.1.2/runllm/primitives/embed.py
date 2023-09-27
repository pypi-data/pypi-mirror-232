from typing import List, Optional, Tuple, Union

from runllm.constants.enums import (
    ImplementationType,
    OpenAIEmbeddingModelType,
    PrimitiveType,
    ResourceType,
    Service,
)
from runllm.context import ContextKey
from runllm.exceptions import (
    InvalidConfigurationException,
    InvalidResourceParamsException,
    UnknownImplementationTypeException,
)
from runllm.primitives.custom_primitive import CustomPrimitive
from runllm.primitives.primitive import Primitive, initialize_primitive_within_task
from runllm.primitives.read import ReadPrimitive
from runllm.primitives.spec import CustomSpec, DefaultEmbedSpec, FunctionSpec
from runllm.resources.parameters import EmbedParams
from runllm.resources.resources import Resource


class EmbedPrimitive(Primitive):
    inputs: List[Union[str, ContextKey]]
    implementation_spec: Union[DefaultEmbedSpec, CustomSpec]

    def __init__(
        self,
        data: Union[ReadPrimitive, CustomPrimitive, ContextKey],
        implementation_type: ImplementationType,
        resource: Optional[Resource] = None,
        params: Optional[EmbedParams] = None,
        function_spec: Optional[FunctionSpec] = None,
    ):
        dependencies, context_keys, inputs = self._process_inputs(data)

        spec = self._construct_primitive_spec(
            implementation_type,
            resource,
            params,
            function_spec,
        )

        # Pydantic's BaseModel is aware of all fields in both EmbedPrimitive and Primitive.
        # It properly processes the attributes to the correct classes and performs type-checking.
        super().__init__(
            type=PrimitiveType.EMBED,
            implementation_type=implementation_type,
            dependencies=dependencies,
            context_keys=context_keys,
            inputs=inputs,  # type: ignore
            implementation_spec=spec,
        )

        initialize_primitive_within_task(self)

    def _process_inputs(
        self, data: Union[ReadPrimitive, CustomPrimitive, ContextKey]
    ) -> Tuple[List[str], List[ContextKey], List[Union[str, ContextKey]]]:
        """
        Verify and process the input data for the EmbedPrimitive instance.

        Parameters:
            data (Union[ReadPrimitive, CustomPrimitive, ContextKey]): The input data to be verified and processed.

        Raises:
            InvalidInputException: If the input data is not of the expected type (ReadPrimitive or CustomPrimitive or ContextKey).
        """
        from runllm.primitives.utils import process_primitive_inputs

        target_types = (ReadPrimitive, CustomPrimitive)
        return process_primitive_inputs(data, target_types)

    def _construct_primitive_spec(
        self,
        implementation_type: ImplementationType,
        resource: Optional[Resource],
        params: Optional[EmbedParams],
        function_spec: Optional[FunctionSpec],
    ) -> Union[DefaultEmbedSpec, CustomSpec]:
        if implementation_type == ImplementationType.DEFAULT:
            if not (resource and params):
                raise Exception(
                    "Both resource and resource params need to be specified for the Default implementation"
                )
            self._verify_default_implementation(
                resource,
                params,
            )
            return DefaultEmbedSpec(
                resource_id=resource.id,
                params=params,
            )
        elif implementation_type == ImplementationType.CUSTOM:
            # We already verify the custom implementation in the decorator
            if not function_spec:
                raise InvalidConfigurationException(
                    "CUSTOM type implementation expects a function spec passed in."
                )

            return CustomSpec(
                function_spec=function_spec,
            )
        else:
            raise UnknownImplementationTypeException("Unknown type of implementation")

    def _verify_default_implementation(self, resource: Resource, params: EmbedParams) -> None:
        if resource.type == ResourceType.LLM:
            if not isinstance(params, EmbedParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of EmbedParams."
                )

            if resource.service == Service.OPENAI:
                if params.model not in OpenAIEmbeddingModelType:
                    raise InvalidResourceParamsException(
                        f"Invalid embedding model type {params.model} for OpenAI service. See runllm.constants.enums.OpenAIEmbeddingModelType for supported model types."
                    )
        else:
            raise InvalidConfigurationException("Embed Primitive expects a LLM resource type.")
