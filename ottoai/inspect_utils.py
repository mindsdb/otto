import inspect
import json
from typing import Any

class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that converts not-serializable objects to strings."""
    def default(self, o):
        if isinstance(o, inspect._empty):
            return 'None'  # You can choose to return 'None' or any other placeholder
        return str(o)

def generate_openai_function_spec(obj: Any) -> str:
    """
    Generate an OpenAI-compatible function spec JSON from an SDK module object.

    Args:
        obj: An instantiated object of an SDK module.
        
    Returns:
        A JSON string containing the function specifications.
    """
    function_specs = {"functions": []}
    
    for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        
        method_spec = {
            "name": name,
            "docs": inspect.getdoc(method) or "",
            "args": [],
            "return_type": str(inspect.signature(method).return_annotation)
        }
        
        sig = inspect.signature(method)
        for param_name, param in sig.parameters.items():
            arg_spec = {
                "name": param_name,
                "type": str(param.annotation) if param.annotation is not inspect._empty else 'Any',
                "default": param.default if param.default is not inspect.Parameter.empty else None
            }
            method_spec["args"].append(arg_spec)
        
        function_specs["functions"].append(method_spec)
    
    # Use the custom JSON encoder
    return json.dumps(function_specs, indent=4, cls=EnhancedJSONEncoder)

# Example usage
# Assuming `some_sdk_object` is an instantiated object from an SDK module
# print(generate_openai_function_spec(some_sdk_object))
