"""Expose Python OpenRPC methods to a CLI."""
import json
from typing import Any, Callable

from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument
from openrpc import ContentDescriptor, Method, OpenRPC, ParamStructure, RPCServer


def cli(rpc: RPCServer) -> int:
    """Generate a CLI for RPC methods."""
    openrpc = OpenRPC(**rpc.discover())
    application = Application(name=openrpc.info.title)
    for method in openrpc.methods:
        attributes = {
            "name": method.name,
            "description": method.description,
            "arguments": [
                argument(
                    param.name, optional=_is_optional(param), default=_default(param)
                )
                for param in method.params
            ],
            "handle": _get_handler(rpc, method),
        }
        command = type(f"{method.name}Command", (Command,), attributes)
        application.add(command())
    return application.run()


def _get_handler(rpc: RPCServer, method: Method) -> Callable:
    def _handle(self: Command) -> None:
        if method.param_structure is ParamStructure.BY_NAME:
            params = ", ".join(
                f'"{param.name}": {_param_str(self.argument(param.name), param)}'
                for param in method.params
            )
            params = "{" + params + "}"
        else:
            params = ", ".join(
                _param_str(self.argument(param.name), param) for param in method.params
            )
            params = "[" + params + "]"
        req = '{"id": 1, "method": "%s", "params": %s, "jsonrpc": "2.0"}' % (
            method.name,
            params,
        )
        # Response is never None because we don't use notifications.
        response = rpc.process_request(req) or ""
        parsed_response = json.loads(response)
        if "result" in parsed_response:
            self.line(f"Result: <info>{parsed_response['result']}<info>")
        else:
            self.line(f"Error: <error>{parsed_response['error']}<error>")

    return _handle


def _param_str(value: Any, param: ContentDescriptor) -> str:
    if isinstance(param.schema_, bool):
        return str(value)
    if param.schema_.type == "string":
        return f'"{value}"'
    return str(value)


def _is_optional(param: ContentDescriptor) -> bool:
    if isinstance(param.schema_, bool):
        return False
    return "default" in param.schema_.model_fields_set or not param.required


def _default(param: ContentDescriptor) -> Any:
    if isinstance(param.schema_, bool):
        return None
    return param.schema_.default
