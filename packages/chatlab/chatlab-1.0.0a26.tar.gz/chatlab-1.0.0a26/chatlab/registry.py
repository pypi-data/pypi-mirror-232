"""Registry of functions for use by ChatCompletions.

Example usage:

    from chatlab import FunctionRegistry
    from pydantic import BaseModel

    registry = FunctionRegistry()

    class Parameters(BaseModel):
        name: str

    from datetime import datetime
    from pytz import timezone, all_timezones, utc
    from typing import Optional
    from pydantic import BaseModel

    def what_time(tz: Optional[str] = None):
        '''Current time, defaulting to the user's current timezone'''
        if tz is None:
            pass
        elif tz in all_timezones:
            tz = timezone(tz)
        else:
            return 'Invalid timezone'
        return datetime.now(tz).strftime('%I:%M %p')

    class WhatTime(BaseModel):
        timezone: Optional[str]

    import chatlab
    registry = chatlab.FunctionRegistry()

    chat = chatlab.Chat(
        function_registry=registry,
    )

    await chat("What time is it?")

"""

import asyncio
import inspect
import json
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Type, Union, get_args, get_origin, overload

from pydantic import BaseModel

from .decorators import ChatlabMetadata


class FunctionArgumentError(Exception):
    """Exception raised when a function is called with invalid arguments."""

    pass


class UnknownFunctionError(Exception):
    """Exception raised when a function is called that is not registered."""

    pass


# Allowed types for auto-inferred schemas
ALLOWED_TYPES = [int, str, bool, float, list, dict, List, Dict]

JSON_SCHEMA_TYPES = {
    int: 'integer',
    float: 'number',
    str: 'string',
    bool: 'boolean',
    list: 'array',
    dict: 'object',
    List: 'array',
    Dict: 'object',
}


def is_optional_type(t):
    """Check if a type is Optional."""
    return get_origin(t) is Union and len(get_args(t)) == 2 and type(None) in get_args(t)


def is_union_type(t):
    """Check if a type is a Union."""
    return get_origin(t) is Union


def process_type(annotation, is_required=True):
    """Determine the JSON schema type of a type annotation."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if is_optional_type(annotation):
        return process_type(args[0], is_required=False)

    elif origin is Union:
        types = [process_type(t, is_required)[0]["type"] for t in args if t is not type(None)]  # noqa: E721
        return {"type": types}, is_required

    elif origin is list:
        item_type = process_type(args[0], is_required)[0]["type"]
        return {"type": "array", "items": {"type": item_type}}, is_required

    elif origin is Literal:
        values = get_args(annotation)
        return {"type": "string", "enum": values}, is_required

    elif issubclass(annotation, Enum):
        values = [e.name for e in annotation]
        return {"type": "string", "enum": values}, is_required

    elif origin is dict:
        return {"type": "object"}, is_required

    elif annotation in ALLOWED_TYPES:
        return {
            "type": JSON_SCHEMA_TYPES[annotation],
        }, is_required

    else:
        raise Exception(f"Type annotation must be a JSON serializable type ({ALLOWED_TYPES})")


def process_parameter(name, param):
    """Process a function parameter for use in a JSON schema."""
    prop_schema, is_required = process_type(param.annotation, param.default == inspect.Parameter.empty)
    if param.default != inspect.Parameter.empty:
        prop_schema["default"] = param.default
    return prop_schema, is_required


def generate_function_schema(
    function: Callable,
    parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None,
):
    """Generate a function schema for sending to OpenAI."""
    doc = function.__doc__
    func_name = function.__name__

    if not func_name:
        raise Exception("Function must have a name")
    if func_name == "<lambda>":
        raise Exception("Lambdas cannot be registered. Use `def` instead.")
    if not doc:
        raise Exception("Only functions with docstrings can be registered")

    schema = None
    if isinstance(parameter_schema, dict):
        schema = parameter_schema
    elif parameter_schema is not None:
        schema = parameter_schema.schema()
    else:
        schema_properties = {}
        required = []

        sig = inspect.signature(function)
        for name, param in sig.parameters.items():
            prop_schema, is_required = process_parameter(name, param)
            schema_properties[name] = prop_schema
            if is_required:
                required.append(name)

        schema = {"type": "object", "properties": {}, "required": []}
        if len(schema_properties) > 0:
            schema = {
                "type": "object",
                "properties": schema_properties,
                "required": required,
            }

    if schema is None:
        raise Exception(f"Could not generate schema for function {func_name}")

    return {
        "name": func_name,
        "description": doc,
        "parameters": schema,
    }


# Declare the type for the python hallucination
PythonHallucinationFunction = Callable[[str], Any]


class FunctionRegistry:
    """Registry of functions and their schemas for calling them.

    Example usage:

        from chatlab import FunctionRegistry

        from datetime import datetime
        from pytz import timezone, all_timezones, utc
        from typing import Optional
        from pydantic import BaseModel

        def what_time(tz: Optional[str] = None):
            '''Current time, defaulting to the user's current timezone'''
            if tz is None:
                pass
            elif tz in all_timezones:
                tz = timezone(tz)
                else:
                    return 'Invalid timezone'
            return datetime.now(tz).strftime('%I:%M %p')

        class WhatTime(BaseModel):
            timezone: Optional[str]

        import chatlab
        registry = chatlab.FunctionRegistry()
        registry.register(what_time, WhatTime)

        chat = chatlab.Chat(
            function_registry=registry,
        )

        await chat("What time is it?")
    """

    __functions: dict[str, Callable]
    __schemas: dict[str, dict]

    # Allow passing in a callable that accepts a single string for the python
    # hallucination function. This is useful for testing.
    def __init__(self, python_hallucination_function: Optional[PythonHallucinationFunction] = None):
        """Initialize a FunctionRegistry object."""
        self.__functions = {}
        self.__schemas = {}

        self.python_hallucination_function = python_hallucination_function

    def decorator(self, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None) -> Callable:
        """Create a decorator for registering functions with a schema."""

        def decorator(function):
            self.register_function(function, parameter_schema)
            return function

        return decorator

    @overload
    def register(
        self, function: None = None, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None
    ) -> Callable:
        ...

    @overload
    def register(self, function: Callable, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None) -> Dict:
        ...

    def register(
        self, function: Optional[Callable] = None, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None
    ) -> Union[Callable, Dict]:
        """Register a function for use in `Chat`s. Can be used as a decorator or directly to register a function.

        >>> registry = FunctionRegistry()
        >>> @registry.register
        ... def what_time(tz: Optional[str] = None):
        ...     '''Current time, defaulting to the user's current timezone'''
        ...     if tz is None:
        ...         pass
        ...     elif tz in all_timezones:
        ...         tz = timezone(tz)
        ...     else:
        ...         return 'Invalid timezone'
        ...     return datetime.now(tz).strftime('%I:%M %p')
        >>> registry.get("what_time")
        <function __main__.what_time(tz: Optional[str] = None)>
        >>> await registry.call("what_time", '{"tz": "America/New_York"}')
        '10:57 AM'

        """
        # If the function is None, assume this is a decorator call
        if function is None:
            return self.decorator(parameter_schema)

        # Otherwise, directly register the function
        return self.register_function(function, parameter_schema)

    def register_function(
        self, function: Callable, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None
    ) -> Dict:
        """Register a single function."""
        final_schema = generate_function_schema(function, parameter_schema)

        self.__functions[function.__name__] = function
        self.__schemas[function.__name__] = final_schema

        return final_schema

    def register_functions(self, functions: Union[Iterable[Callable], dict[str, Callable]]):
        """Register a dictionary of functions."""
        if isinstance(functions, dict):
            functions = functions.values()

        for function in functions:
            self.register(function)

    def get(self, function_name) -> Optional[Callable]:
        """Get a function by name."""
        if function_name == "python" and self.python_hallucination_function is not None:
            return self.python_hallucination_function

        return self.__functions.get(function_name)

    def get_schema(self, function_name) -> Optional[dict]:
        """Get a function schema by name."""
        return self.__schemas.get(function_name)

    def get_chatlab_metadata(self, function_name) -> ChatlabMetadata:
        """Get the chatlab metadata for a function by name."""
        function = self.get(function_name)

        if function is None:
            raise UnknownFunctionError(f"Function {function_name} is not registered")

        chatlab_metadata = getattr(function, "chatlab_metadata", ChatlabMetadata())
        return chatlab_metadata

    def api_manifest(self, function_call_option: Union[str, dict] = "auto"):
        """
        Get a dictionary containing function definitions and calling options.
        This is designed to be used with OpenAI's Chat Completion API, where the
        dictionary can be passed as keyword arguments to set the `functions` and
        `function_call` parameters.

        The `functions` parameter is a list of dictionaries, each representing a
        function that the model can call during the conversation. Each dictionary
        has a `name`, `description`, and `parameters` key.

        The `function_call` parameter sets the policy of when to call these functions:
            - "auto": The model decides when to call a function (default).
            - "none": The model generates a user-facing message without calling a function.
            - {"name": "<insert-function-name>"}: Forces the model to call a specific function.

        Args:
            function_call_option (str or dict, optional): The policy for function calls.
            Defaults to "auto".

        Returns:
            dict: A dictionary with keys "functions" and "function_call", which
            can be passed as keyword arguments to `openai.ChatCompletion.create`.

        Example usage:
            >>> registry = FunctionRegistry()
            >>> # Register functions here...
            >>> manifest = registry.api_manifest()
            >>> resp = openai.ChatCompletion.create(
                    model="gpt-4.0-turbo",
                    messages=[...],
                    **manifest,
                    stream=True,
                )

            >>> # To force a specific function to be called:
            >>> manifest = registry.api_manifest({"name": "what_time"})
            >>> resp = openai.ChatCompletion.create(
                    model="gpt-4.0-turbo",
                    messages=[...],
                    **manifest,
                    stream=True,
                )

            >>> # To generate a user-facing message without calling a function:
            >>> manifest = registry.api_manifest("none")
            >>> resp = openai.ChatCompletion.create(
                    model="gpt-4.0-turbo",
                    messages=[...],
                    **manifest,
                    stream=True,
                )
        """
        if len(self.function_definitions) == 0:
            # When there are no functions, we can't send an empty functions array to OpenAI
            return {}

        return {"functions": self.function_definitions, "function_call": function_call_option}

    async def call(self, name: str, arguments: Optional[str] = None) -> Any:
        """Call a function by name with the given parameters."""
        if name is None:
            raise UnknownFunctionError("Function name must be provided")

        function = self.get(name)
        parameters: dict = {}

        # Handle the code interpreter hallucination
        if name == "python" and self.python_hallucination_function is not None:
            function = self.python_hallucination_function
            if arguments is None:
                arguments = ""

            # The "hallucinated" python function takes raw plaintext
            # instead of a JSON object. We can just pass it through.
            if asyncio.iscoroutinefunction(function):
                return await function(arguments)
            return function(arguments)
        elif function is None:
            raise UnknownFunctionError(f"Function {name} is not registered")
        elif arguments is None or arguments == "":
            parameters = {}
        else:
            try:
                parameters = json.loads(arguments)
                # TODO: Validate parameters against schema
            except json.JSONDecodeError:
                raise FunctionArgumentError(f"Invalid Function call on {name}. Arguments must be a valid JSON object")

        if function is None:
            raise UnknownFunctionError(f"Function {name} is not registered")

        if asyncio.iscoroutinefunction(function):
            result = await function(**parameters)
        else:
            result = function(**parameters)
        return result

    def __contains__(self, name) -> bool:
        """Check if a function is registered by name."""
        if name == "python" and self.python_hallucination_function:
            return True
        return name in self.__functions

    @property
    def function_definitions(self) -> list[dict]:
        """Get a list of function definitions."""
        return list(self.__schemas.values())
