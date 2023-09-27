import base64
import inspect
from typing import Any, Callable, List, Optional, Tuple, Type, Union

from runllm.constants.enums import FunctionType, ImplementationType, PrimitiveType
from runllm.constants.types import input_types, output_types
from runllm.context import ContextKey
from runllm.exceptions import InvalidUserArgumentException
from runllm.primitives.custom_primitive import CustomPrimitive
from runllm.primitives.embed import EmbedPrimitive
from runllm.primitives.generate import GeneratePrimitive
from runllm.primitives.primitive import Primitive
from runllm.primitives.read import ReadPrimitive
from runllm.primitives.retrieve import RetrievePrimitive
from runllm.primitives.spec import FunctionSpec
from runllm.primitives.write import WritePrimitive
from runllm.utils.function_packaging import serialize_user_code

UserFunction = Callable[..., Any]
OutputPrimitiveFunction = Callable[..., Primitive]
DecoratedFunction = Callable[[UserFunction], OutputPrimitiveFunction]


def _typecheck_common_decorator_arguments(
    description: Optional[str],
    file_dependencies: Optional[List[str]],
    requirements: Optional[Union[str, List[str]]],
) -> None:
    """
    Raises an InvalidUserArgumentException if any issues are found.
    """
    if description is not None and not isinstance(description, str):
        raise InvalidUserArgumentException("A supplied description must be of string type.")

    if file_dependencies is not None:
        if not isinstance(file_dependencies, list):
            raise InvalidUserArgumentException("File dependencies must be specified as a list.")
        if any(not isinstance(file_dep, str) for file_dep in file_dependencies):
            raise InvalidUserArgumentException("Each file dependency must be a string.")

    if requirements is not None:
        is_list = isinstance(requirements, list)
        if not isinstance(requirements, str) and not is_list:
            raise InvalidUserArgumentException(
                "Requirements must either be a path string or a list of pip requirements specifiers."
            )
        if is_list and any(not isinstance(req, str) for req in requirements):
            raise InvalidUserArgumentException("Each pip requirements specifier must be a string.")


def _type_check_decorated_function_arguments(
    target_types: Union[Type[Primitive], Tuple[Type[Primitive], ...]],
    input_val: Union[Primitive, ContextKey],
) -> None:
    """
    Check the types of input values against the specified target types or ContextKey.

    Args:
        target_types (Union[Type[Primitive], Tuple[Type[Primitive], ...]]):
            The expected target types for the input values or tuple of target types.
        *inputs (Union[Primitive, ContextKey]):
            Input values to be type-checked.

    Raises:
        InvalidUserArgumentException: If any input value is not of the expected target type or ContextKey.

    Returns:
        None
    """
    if not (isinstance(input_val, target_types) or isinstance(input_val, ContextKey)):
        raise InvalidUserArgumentException(
            f"Input data is of the wrong type. Expected {target_types} or ContextKey."
        )


def create_primitive(
    primitive_type: PrimitiveType,
    function_spec: FunctionSpec,
    *inputs: Union[Primitive, ContextKey],
) -> Primitive:
    """
    Create a primitive instance based on the provided primitive type and inputs.

    Args:
        primitive_type (PrimitiveType):
            The type of primitive being created.
        function_spec (FunctionSpec):
            The specification of the function associated with the primitive.
        *inputs (Primitive, ContextKey):
            Input primitives required for creating the specific primitive instance.

    Returns:
        Primitive:
            A new instance of the primitive based on the given type and inputs.

    Raises:
        InvalidUserArgumentException:
            If there are issues with input type compatibility for specific primitive types.
    """
    if primitive_type == PrimitiveType.READ:
        # ReadPrimitive takes in no inputs
        if len(inputs) != 0:
            raise InvalidUserArgumentException("ReadPrimitive takes in no inputs.")

        return ReadPrimitive(
            implementation_type=ImplementationType.CUSTOM,
            function_spec=function_spec,
        )

    if primitive_type == PrimitiveType.CUSTOM:
        return CustomPrimitive(
            function_spec,
            *inputs,
        )

    # All primitives other than READ and CUSTOM take in one input.
    if len(inputs) != 1:
        raise InvalidUserArgumentException(
            f"Primitive of type `{primitive_type}` takes in only one input."
        )

    if primitive_type == PrimitiveType.WRITE:
        _type_check_decorated_function_arguments((EmbedPrimitive, CustomPrimitive), inputs[0])
        return WritePrimitive(
            implementation_type=ImplementationType.CUSTOM,
            data=inputs[0],  # type: ignore
            function_spec=function_spec,
        )

    if primitive_type == PrimitiveType.EMBED:
        _type_check_decorated_function_arguments((ReadPrimitive, CustomPrimitive), inputs[0])
        return EmbedPrimitive(
            implementation_type=ImplementationType.CUSTOM,
            data=inputs[0],  # type: ignore
            function_spec=function_spec,
        )

    if primitive_type == PrimitiveType.RETRIEVE:
        _type_check_decorated_function_arguments(CustomPrimitive, inputs[0])
        return RetrievePrimitive(
            implementation_type=ImplementationType.CUSTOM,
            data=inputs[0],  # type: ignore
            function_spec=function_spec,
        )

    if primitive_type == PrimitiveType.GENERATE:
        _type_check_decorated_function_arguments(CustomPrimitive, inputs[0])
        return GeneratePrimitive(
            implementation_type=ImplementationType.CUSTOM,
            data=inputs[0],  # type: ignore
            function_spec=function_spec,
        )

    raise InvalidUserArgumentException(f"Unsupported primitive type `{primitive_type}`")


def _validate_function_input_type(func: Callable[..., Any], primitive_type: PrimitiveType) -> None:
    """
    Validates the input type of a given function based on the provided primitive type.

    Args:
        func (Callable): The function to validate.
        primitive_type (PrimitiveType): The primitive type being validated against.

    Raises:
        ValueError: If the primitive_type is not supported or if the function has incorrect number of input arguments.
        TypeError: If the parameter's annotation does not match the expected type.

    """
    if primitive_type == PrimitiveType.CUSTOM:
        return

    if primitive_type == PrimitiveType.READ and len(func.__code__.co_varnames) != 0:
        raise ValueError(f"Read primitives do not take in inputs.")

    if len(func.__code__.co_varnames) != 1:
        raise ValueError(f"Function '{func.__name__}' should have exactly one argument.")

    parameters = inspect.signature(func).parameters
    for param_name, param in parameters.items():
        param_annotation = param.annotation

        if param_annotation == inspect.Parameter.empty:
            raise TypeError(
                f"Argument '{param_name}' of function '{func.__name__}' must be type hinted"
            )

        if param_annotation != input_types[primitive_type]:
            raise TypeError(
                f"Argument '{param_name}' of function '{func.__name__}' has type '{param_annotation}', but expected type '{input_types[primitive_type]}'."
            )


def _validate_function_output_type(func: Callable[..., Any], primitive_type: PrimitiveType) -> None:
    """
    Validates the output type of a given function based on the provided primitive type.

    Args:
        func (Callable): The function to validate.
        primitive_type (PrimitiveType): The primitive type being validated against.

    Raises:
        TypeError: If the return type's annotation does not match the expected type.

    """
    if primitive_type == PrimitiveType.CUSTOM:
        return

    return_type = inspect.signature(func).return_annotation
    if return_type == inspect.Parameter.empty:
        raise TypeError(f"Return type of function '{func.__name__}' must be type hinted")
    if return_type != output_types[primitive_type]:
        raise TypeError(
            f"Function '{func.__name__}' has return type '{return_type}', but expected type '{output_types[primitive_type]}'."
        )


# Custom decorators


def custom(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
    primitive_type: PrimitiveType = PrimitiveType.CUSTOM,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a CustomPrimitive. There is no restriction on input/output types.
    The function definition must be type-decorated.

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the primitive function.
      If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the primitive function. If not provided,
      the decorator will attempt to extract it from the decorated function's docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the primitive function or a list of requirement strings.
    - primitive_type (PrimitiveType): The type of the primitive function, defaults to
      PrimitiveType.CUSTOM.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used to generate a CustomPrimitive in your task.

    Example Usage:
    ```python
    @custom(description="Custom prompt generator")
    def custom_prompt(query: str, docs: List[str]) -> List[str]:
        return [query] + docs
    ```
    """
    _typecheck_common_decorator_arguments(
        description,
        file_dependencies,
        requirements,
    )

    def inner_decorator(
        target: Union[UserFunction, Type], # type: ignore
    ) -> OutputPrimitiveFunction:
        nonlocal name
        nonlocal description
        if name is None or not isinstance(name, str):
            name = target.__name__
        if description is None:
            description = target.__doc__ or ""

        func = target
        # Validate type signatures of input/output
        # This is the recommended way to type check against a class object, but mypy complains.
        # We skip the arg-type check here.
        if isinstance(target, Type):  # type: ignore[arg-type]
            if not (hasattr(target, "run") and callable(getattr(target, "run"))):
                raise TypeError(
                    f"Decorated class '{target.__name__}' must have a function called 'run'."
                )
            if len(inspect.signature(target.__init__).parameters) != 1:  # type: ignore
                raise TypeError(
                    f"Decorated class '{target.__name__}' must have an __init__ function with no parameters other than self."
                )
            func = target.run  # type: ignore[union-attr]

        _validate_function_input_type(func, primitive_type)
        _validate_function_output_type(func, primitive_type)

        assert isinstance(name, str)
        assert isinstance(description, str)

        zip_file = serialize_user_code(target, name, file_dependencies, requirements)
        base64_encoded_file = base64.b64encode(zip_file).decode("utf-8")
        function_spec = FunctionSpec(
            type=FunctionType.FILE,
            file=base64_encoded_file,
        )

        def wrapped(
            *inputs: Union[Primitive, ContextKey],
        ) -> Primitive:
            """
            Creates the following files in the zipped folder structure:
             - user_code.py
             - code.pkl
             - requirements.txt
             - python_version.txt
             - <any file dependencies>
            """

            return create_primitive(
                primitive_type,
                function_spec,
                *inputs,
            )

        # This wrapped_class function is used to override a class.run() function.
        def wrapped_class(
            *inputs: Union[Primitive, ContextKey],
        ) -> Primitive:
            return wrapped(*inputs)

        # If a class is passed in, overwrite the __init__ method to do nothing.
        # and override the run method to return a primitive.
        # There are few mypy checks that don't agree with modifying the class functions
        # that are required for our decorator system to work, hence the ignore comments.
        if isinstance(target, Type):  # type: ignore[arg-type]
            target.__init__ = lambda self: None  # type: ignore
            target.run = wrapped_class  # type: ignore[union-attr]
            return target
        else:
            return wrapped

    if callable(name):
        # This only happens when the decorator is used without parenthesis, eg: @code.
        return inner_decorator(name)
    else:
        return inner_decorator


def read(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a custom ReadPrimitive. The decorated function must be type annotated.

    There should be no inputs to the decorated function.
    The output of the decorated function must be of type List[str].

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the read primitive
      function. If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the read primitive function. If not
      provided, the decorator will attempt to extract it from the decorated function's
      docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      read primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the read primitive function or a list of requirement strings.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used as a read primitive in your workflow.

    Example Usage:
    ```python
    @read(description="Read CSV File")
    def read_csv() -> List[str]:
        return pd.read_csv(file_path)['columnA'].to_list()
    ```
    """
    return custom(
        name=name,
        description=description,
        file_dependencies=file_dependencies,
        requirements=requirements,
        primitive_type=PrimitiveType.READ,
    )


def embed(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a custom EmbedPrimitive. The decorated function must be type annotated.

    The input to the decorated function must be of type List[str]
    The output to the decorated function must be of type List[Tuple[List[float], str]],
    where Tuple[List[float], str] is equivalent to a Vector.

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the embed primitive
      function. If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the embed primitive function. If not
      provided, the decorator will attempt to extract it from the decorated function's
      docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      embed primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the embed primitive function or a list of requirement strings.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used as an embed primitive in your workflow.

    Example Usage:
    ```python
    @embed(description="Word Embedding")
    def word_embedding(texts: List[str]) -> List[Tuple[List[float], str]]:
        # Perform word embedding using a pre-trained model
        # Return a list of embedding vectors for each input text
        embeddings = []
        for text in texts:
            # Perform word embedding and append the result to 'embeddings'
            # ...
        return embeddings
    ```
    """
    return custom(
        name=name,
        description=description,
        file_dependencies=file_dependencies,
        requirements=requirements,
        primitive_type=PrimitiveType.EMBED,
    )


def write(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a custom WritePrimitive. The decorated function must be type annotated.

    The inputs to the decorated function must be of type List[Tuple[List[float], str]] (List of Vectors)
    The output type of the decorated function must be None.

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the write primitive
      function. If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the write primitive function. If not
      provided, the decorator will attempt to extract it from the decorated function's
      docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      write primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the write primitive function or a list of requirement strings.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used as a write primitive in your workflow.

    Example Usage:
    ```python
    @write(description="Write Results to VectorDB")
    def write_to_csv(data: List[Tuple[List[float], str]]) -> None:
        # Write the data to a VectorDB
        # Connect to vectorDB
        vectorDB.write(data)
    ```
    """
    return custom(
        name=name,
        description=description,
        file_dependencies=file_dependencies,
        requirements=requirements,
        primitive_type=PrimitiveType.WRITE,
    )


def retrieve(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a custom RetrievePrimitive. The decorated function must be type annotated.

    The input to the decorated function must be of type str
    The output to the decorated function must be of type List[str]

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the retrieve primitive
      function. If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the retrieve primitive function. If not
      provided, the decorator will attempt to extract it from the decorated function's
      docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      retrieve primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the retrieve primitive function or a list of requirement strings.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used as a retrieve primitive in your workflow.

    Example Usage:
    ```python
    @retrieve(description="Retrieve Data from VectorDB")
    def retrieve_data_from_vector_db(query: str) -> List[str]:
        #Connect to vectorDB
        docs = vectorDB.similarity_search(query)
        return docs
    ```
    """
    return custom(
        name=name,
        description=description,
        file_dependencies=file_dependencies,
        requirements=requirements,
        primitive_type=PrimitiveType.RETRIEVE,
    )


def generate(
    name: Optional[Union[str, UserFunction]] = None,
    description: Optional[str] = None,
    file_dependencies: Optional[List[str]] = None,
    requirements: Optional[Union[str, List[str]]] = None,
) -> Union[DecoratedFunction, OutputPrimitiveFunction]:
    """
    Decorator for defining a custom GeneratePrimitive. The decorated function must be type annotated.

    The input to the decorated function must be of type str
    The output of the decorated function must be of type str

    Parameters:
    - name (Optional[Union[str, UserFunction]]): A custom name for the generate primitive
      function. If not provided, the name will be derived from the decorated function's name.
    - description (Optional[str]): A description of the generate primitive function. If not
      provided, the decorator will attempt to extract it from the decorated function's
      docstring.
    - file_dependencies (Optional[List[str]]): A list of file dependencies required by the
      generate primitive function.
    - requirements (Optional[Union[str, List[str]]]): Either a string specifying the
      requirements for the generate primitive function or a list of requirement strings.

    Returns:
    - Union[DecoratedFunction, OutputPrimitiveFunction]: A decorated function or class that
      can be used as a generate primitive in your workflow.

    Example Usage:
    ```python
    @generate(description="Generate Text from Model")
    def generate_text_from_model(query: str) -> str:
        # Generate text using a custom language model
        generated_text = model.generate(query)
        return generated_text
    ```
    """
    return custom(
        name=name,
        description=description,
        file_dependencies=file_dependencies,
        requirements=requirements,
        primitive_type=PrimitiveType.GENERATE,
    )
