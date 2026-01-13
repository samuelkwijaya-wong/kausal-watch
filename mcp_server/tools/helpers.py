from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, Self, cast

from pydantic import BaseModel

from asgiref.sync import sync_to_async

from kausal_common.strawberry.views import get_base_context

from aplans.schema_context import WatchGraphQLContext

if TYPE_CHECKING:
    from strawberry.types import ExecutionResult

    from starlette.requests import Request as StarletteRequest


def get_schema_execution_context():
    from mcp.server.lowlevel.server import request_ctx

    context = request_ctx.get()
    req = cast('StarletteRequest', context.request)
    base_ctx = get_base_context(req, None)
    schema_ctx = WatchGraphQLContext(**base_ctx)
    return schema_ctx


async def execute_schema_query(query: str, variables: dict[str, Any] | None = None) -> ExecutionResult:
    from aplans.schema import schema
    schema_ctx = get_schema_execution_context()
    res = await sync_to_async(schema.execute_sync)(query, context_value=schema_ctx, variable_values=variables)
    return res


class OperationMeta(Protocol):
    document: str


class Operation[ArgT: BaseModel, MetaT: OperationMeta](Protocol):
    Arguments: ArgT
    Meta: type[MetaT]

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self: ...



async def execute_operation[T: Operation[Any, Any]](operation_class: type[T], args: BaseModel | None = None) -> T:
    """
    Execute a turms-generated GraphQL operation and return the validated result.

    Args:
        operation_class: A turms-generated Pydantic model with Meta.document and Arguments inner classes.
        args: The arguments to pass to the operation.

    Returns:
        The validated operation result as an instance of the operation class.

    Raises:
        RuntimeError: If the GraphQL execution returns errors.

    """
    # Build the arguments and serialize to dict
    if args is None:
        variables_dict = {}
    else:
        assert isinstance(args, operation_class.Arguments)
        variables_dict = args.model_dump(by_alias=True, exclude_none=True)

    # Execute the query
    result = await execute_schema_query(
        query=operation_class.Meta.document,
        variables=variables_dict,
    )

    if result.errors:
        error_msgs = '; '.join(str(e) for e in result.errors)
        raise RuntimeError(f"GraphQL errors: {error_msgs}")

    # Validate and return the result
    return operation_class.model_validate(result.data)
