from typing import List, Optional, Tuple, Union

from runllm.constants.enums import ImplementationType, PrimitiveType, ResourceType
from runllm.context import ContextKey
from runllm.exceptions import (
    InvalidConfigurationException,
    InvalidResourceParamsException,
    UnknownImplementationTypeException,
)
from runllm.primitives.custom_primitive import CustomPrimitive
from runllm.primitives.embed import EmbedPrimitive
from runllm.primitives.primitive import Primitive, initialize_primitive_within_task
from runllm.primitives.spec import CustomSpec, DefaultWriteSpec, FunctionSpec
from runllm.resources.parameters import VectorDBWriteParams
from runllm.resources.resources import Resource


class WritePrimitive(Primitive):
    inputs: List[Union[str, ContextKey]]
    implementation_spec: Union[DefaultWriteSpec, CustomSpec]

    def __init__(
        self,
        data: Union[EmbedPrimitive, CustomPrimitive, ContextKey],
        implementation_type: ImplementationType,
        resource: Optional[Resource] = None,
        params: Optional[VectorDBWriteParams] = None,
        function_spec: Optional[FunctionSpec] = None,
    ):
        dependencies, context_keys, inputs = self._process_inputs(data)

        spec = self._construct_primitive_spec(
            implementation_type,
            resource,
            params,
            function_spec,
        )

        # Pydantic's BaseModel is aware of all fields in both WritePrimitive and Primitive.
        # It properly processes the attributes to the correct classes and performs type-checking.
        super().__init__(
            type=PrimitiveType.WRITE,
            implementation_type=implementation_type,
            dependencies=dependencies,
            context_keys=context_keys,
            inputs=inputs,  # type: ignore
            implementation_spec=spec,
        )

        initialize_primitive_within_task(self)

    def _process_inputs(
        self, data: Union[EmbedPrimitive, CustomPrimitive, ContextKey]
    ) -> Tuple[List[str], List[ContextKey], List[Union[str, ContextKey]]]:
        """
        Verify and process the input data for the WritePrimitive instance.

        Parameters:
            data (Union[EmbedPrimitive, CustomPrimitive, ContextKey]): The input data to be verified and processed.

        Raises:
            InvalidInputException: If the input data is not of the expected type (EmbedPrimitive or CustomPrimitive or ContextKey).
        """
        from runllm.primitives.utils import process_primitive_inputs

        target_types = (EmbedPrimitive, CustomPrimitive)
        return process_primitive_inputs(data, target_types)

    def _construct_primitive_spec(
        self,
        implementation_type: ImplementationType,
        resource: Optional[Resource],
        params: Optional[VectorDBWriteParams],
        function_spec: Optional[FunctionSpec],
    ) -> Union[DefaultWriteSpec, CustomSpec]:
        if implementation_type == ImplementationType.DEFAULT:
            if not (resource and params):
                raise InvalidConfigurationException(
                    "Both resource and resource params need to be specified for the Default implementation"
                )
            self._verify_default_implementation(
                resource,
                params,
            )
            return DefaultWriteSpec(
                resource_id=resource.id,
                params=params,
            )
        elif implementation_type == ImplementationType.CUSTOM:
            if not function_spec:
                raise InvalidConfigurationException(
                    "CUSTOM type implementation expects a function spec passed in."
                )
            # We already verify the custom implementation in the decorator
            return CustomSpec(
                function_spec=function_spec,
            )
        else:
            raise UnknownImplementationTypeException("Unknown type of implementation")

    def _verify_default_implementation(self, resource: Resource, params: VectorDBWriteParams) -> None:
        if resource.type == ResourceType.VECTOR_DB:
            if not isinstance(params, VectorDBWriteParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of VectorDBWriteParams."
                )
        else:
            raise InvalidConfigurationException("Embed Primitive expects a VectorDB resource type.")
