import inspect
import json
from typing import Any
from collections.abc import Iterable
import logging


def inspect_object(obj):
    """
    Inspect an object to determine its module name, object path within the module, and pip module version.
    """
    import_module_name = obj.__name__ if inspect.ismodule(obj) else obj.__class__.__module__
    return import_module_name


def recursive_dict_str(input_dict):
    dict_str = "{\n"
    for key, value in input_dict.items():
        if isinstance(value, dict):
            dict_str += f"    '{key}': " + recursive_dict_str(value)
        elif isinstance(value, (str, int, float)):
            dict_str += f"    '{key}': {value},\n"
        else:
            dict_str += f"    '{key}': {type(value)},\n"
    dict_str += "}\n"
    return dict_str


def get_castable_attributes(obj):
    castable_attributes = {}
    for attr_name in dir(obj):
        attr_value = getattr(obj, attr_name)
        
        if isinstance(attr_value, (str, int, float)): 
            castable_attributes[attr_name] = attr_value
        if callable(attr_value):
            continue
    return castable_attributes


def is_iterable_not_str(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)



class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that converts not-serializable objects to strings."""
    def default(self, o):
        if isinstance(o, inspect._empty):
            return 'None'  # You can choose to return 'None' or any other placeholder


def python_type_to_json_schema(python_type: Any) -> str:
    """
    Map Python types to JSON Schema-compatible types.

    Args:
        python_type: The Python type to map.

    Returns:
        A string representing the corresponding JSON Schema type.
    """
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        None: "null",
        Any: "string"
        # Add more mappings if necessary
    }
    return type_mapping.get(python_type, "string")  # Default to "string" if no mapping exists


def parse_param_docstring(docstring: str) -> dict:
    """
    Parse the docstring to extract parameter descriptions.

    Args:
        docstring: The docstring of a method.

    Returns:
        A dictionary where keys are parameter names and values are descriptions.
    """
    descriptions = {}
    lines = docstring.split('\n')
    for line in lines:
        parts = line.strip().split(':', 1)
        if len(parts) == 2 and parts[0].strip().isidentifier():
            param, desc = parts
            descriptions[param.strip()] = desc.strip()
    return descriptions



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
        method_call = getattr(obj, name)
        if name.startswith("_") or not callable(method_call):
            continue
        
        method_docstring = inspect.getdoc(method) or ""
        param_descriptions = parse_param_docstring(method_docstring)
        


        method_spec =  {
            
            "name": name,
            "description": inspect.getdoc(method) or "",
            "parameters": {
                "type": "object",
                "properties": {
                    
                }
                
            },
            "return_type": str(inspect.signature(method).return_annotation)
        }
        
        sig = inspect.signature(method)
        required_params = []
        for param_name, param in sig.parameters.items():
            param_description = param_descriptions.get(param_name, "")
            param_type = param.annotation if param.annotation is not inspect._empty else Any
            
            arg_spec = {
                "type":  python_type_to_json_schema(param_type),
                "description": param_description,
                #"default": param.default if param.default is not inspect.Parameter.empty else None
            }
            

            enum_list = [value for value in inspect.getdoc(param).split() if value.startswith("'") and value.endswith("'")] if inspect.getdoc(param) else None
            
            if enum_list:
                arg_spec["enum"] = enum_list
            
            method_spec["parameters"]["properties"][param_name] = arg_spec
            if param.default is inspect.Parameter.empty:
                required_params.append(param_name)
        if len(required_params) > 0:
            method_spec['parameters']['required'] = required_params
        function_specs["functions"].append(method_spec)
    
    return function_specs['functions']
    # Use the custom JSON encoder
    return json.dumps(function_specs, indent=4, cls=EnhancedJSONEncoder)






if __name__ == "__main__":
    # Assuming `some_sdk_object` is an instantiated object from an SDK module
    logging.basicConfig(level=logging.DEBUG)
    from github import Github, Auth
    # github_sdk_object = Github(auth=Auth.Token(os.getenv("GITHUB_TOKEN")))
    # functions = generate_openai_function_spec(github_sdk_object)

    import github

    print(inspect_object(github))
    
