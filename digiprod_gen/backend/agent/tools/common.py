import inspect
import logging

from typing import Callable, Union, Optional, Type, Any, List
from langchain_core.runnables import Runnable


from langchain_core.callbacks import (
    CallbackManagerForToolRun,
    Callbacks,
)
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.tools import BaseTool, StructuredTool, Tool
from digiprod_gen.backend.agent.models.memory import MemoryId, MemoryAddResponse
from digiprod_gen.backend.agent.memory import global_memory_container


class CustomStructuredTool(StructuredTool):
    required_memory_ids: List[MemoryId] = []
    adds_memory_ids: List[MemoryId] = []

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Use the tool."""
        if self.func:
            required_ids_not_existend = []
            for required_memory_id in self.required_memory_ids:
                if required_memory_id not in global_memory_container:
                    required_ids_not_existend.append((required_memory_id))
            if len(required_ids_not_existend) > 0:
                return {"response": f"Failure. Required Ids {required_ids_not_existend} do not exist in memory yet. Call a function to fill memory."}
            try:
                response = self.func(*args, **kwargs)
            except Exception as e:
                logging.warning(str(e))
                if self.adds_memory_ids:
                    return [{"response": MemoryAddResponse(uuid=memory_id, success=False)} for memory_id in
                            self.adds_memory_ids]
                else:
                    return {"response": "Failure"}
            if self.adds_memory_ids:
                if len(self.adds_memory_ids) > 1:
                    return [{"response": MemoryAddResponse(uuid=memory_id, success=True)} for memory_id in self.adds_memory_ids]
                return {"response": MemoryAddResponse(uuid=self.adds_memory_ids[0], success=True, data=response)}
            else:
                return response
        raise NotImplementedError("Tool does not support sync")

def tool(
    *args: Union[str, Callable, Runnable],
    return_direct: bool = False,
    args_schema: Optional[Type[BaseModel]] = None,
    infer_schema: bool = True,
    required_memory_ids: List[MemoryId] = [],
    adds_memory_ids: List[MemoryId] = [],
    ):
    """Copy of langchain function except change of using CustomStructuredTool instead of StructuredTool
    Make tools out of functions, can be used with or without arguments.

    Args:
        *args: The arguments to the tool.
        return_direct: Whether to return directly from the tool rather
            than continuing the agent loop.
        args_schema: optional argument schema for user to specify
        infer_schema: Whether to infer the schema of the arguments from
            the function's signature. This also makes the resultant tool
            accept a dictionary input to its `run()` function.

    Requires:
        - Function must be of type (str) -> str
        - Function must have a docstring

    Examples:
        .. code-block:: python

            @tool
            def search_api(query: str) -> str:
                # Searches the API for the query.
                return

            @tool("search", return_direct=True)
            def search_api(query: str) -> str:
                # Searches the API for the query.
                return
    """

    def _make_with_name(tool_name: str) -> Callable:
        def _make_tool(dec_func: Union[Callable, Runnable]) -> BaseTool:
            if isinstance(dec_func, Runnable):
                runnable = dec_func

                if runnable.input_schema.schema().get("type") != "object":
                    raise ValueError("Runnable must have an object schema.")

                async def ainvoke_wrapper(
                    callbacks: Optional[Callbacks] = None, **kwargs: Any
                ) -> Any:
                    return await runnable.ainvoke(kwargs, {"callbacks": callbacks})

                def invoke_wrapper(
                    callbacks: Optional[Callbacks] = None, **kwargs: Any
                ) -> Any:
                    return runnable.invoke(kwargs, {"callbacks": callbacks})

                coroutine = ainvoke_wrapper
                func = invoke_wrapper
                schema: Optional[Type[BaseModel]] = runnable.input_schema
                description = repr(runnable)
            elif inspect.iscoroutinefunction(dec_func):
                coroutine = dec_func
                func = None
                schema = args_schema
                description = None
            else:
                coroutine = None
                func = dec_func
                schema = args_schema
                description = None

            if infer_schema or args_schema is not None:
                tool_instance = CustomStructuredTool.from_function(
                    func,
                    coroutine,
                    name=tool_name,
                    description=description,
                    return_direct=return_direct,
                    args_schema=schema,
                    infer_schema=infer_schema,
                )
                tool_instance.required_memory_ids = required_memory_ids
                tool_instance.adds_memory_ids = adds_memory_ids
                return tool_instance
            # If someone doesn't want a schema applied, we must treat it as
            # a simple string->string function
            if func.__doc__ is None:
                raise ValueError(
                    "Function must have a docstring if "
                    "description not provided and infer_schema is False."
                )
            tool_instance = CustomStructuredTool(
                name=tool_name,
                func = func,
                description=f"{tool_name} tool",
                return_direct=return_direct,
                coroutine=coroutine,
            )

            tool_instance.required_memory_ids = required_memory_ids
            tool_instance.adds_memory_ids = adds_memory_ids
            return tool_instance

        return _make_tool

    if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], Runnable):
        return _make_with_name(args[0])(args[1])
    elif len(args) == 1 and isinstance(args[0], str):
        # if the argument is a string, then we use the string as the tool name
        # Example usage: @tool("search", return_direct=True)
        return _make_with_name(args[0])
    elif len(args) == 1 and callable(args[0]):
        # if the argument is a function, then we use the function name as the tool name
        # Example usage: @tool
        return _make_with_name(args[0].__name__)(args[0])
    elif len(args) == 0:
        # if there are no arguments, then we use the function name as the tool name
        # Example usage: @tool(return_direct=True)
        def _partial(func: Callable[[str], str]) -> BaseTool:
            return _make_with_name(func.__name__)(func)

        return _partial
    else:
        raise ValueError("Too many arguments for tool decorator")
