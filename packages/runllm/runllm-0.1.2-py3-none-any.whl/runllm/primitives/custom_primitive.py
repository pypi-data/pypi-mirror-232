from typing import List, Union

from runllm.constants.enums import ImplementationType, PrimitiveType
from runllm.context import ContextKey
from runllm.primitives.primitive import Primitive, initialize_primitive_within_task
from runllm.primitives.spec import CustomSpec, FunctionSpec


class CustomPrimitive(Primitive):
    inputs: List[Union[str, ContextKey]]
    implementation_spec: CustomSpec

    # This is a sample implementation of a custom primitive
    # that takes in an arbitrary number of inputs, each of which
    # can be either a Primitive or a ContextKey.
    def __init__(self, function_spec: FunctionSpec, *args: Union[Primitive, ContextKey]):
        dependencies = []
        context_keys = []
        inputs: List[Union[str, ContextKey]] = []

        for input_item in args:
            if isinstance(input_item, Primitive):
                dependencies.append(input_item.id)
                inputs.append(input_item.id)
            elif isinstance(input_item, ContextKey):
                context_keys.append(input_item)
                inputs.append(input_item)
            else:
                raise ValueError("Input must be either of type CustomPrimitive or ContextKey")

        spec = CustomSpec(
            function_spec=function_spec,
        )

        # Pydantic's BaseModel is aware of all fields in both CustomPrimitive and Primitive.
        # It properly processes the attributes to the correct classes and performs type-checking.
        super().__init__(
            type=PrimitiveType.CUSTOM,
            implementation_type=ImplementationType.CUSTOM,
            dependencies=dependencies,
            context_keys=context_keys,
            inputs=inputs,  # type: ignore
            implementation_spec=spec,
        )

        initialize_primitive_within_task(self)
