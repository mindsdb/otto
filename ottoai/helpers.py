
import sys
import os
import re

# Import litellm, but its verbose, and no one really wants that
# so we will turn off stout
original_stdout = sys.stdout 
# Redirect stdout to null
sys.stdout = open(os.devnull, 'w')
import litellm
litellm.telemetry = False
from litellm.proxy import proxy_server
proxy_server.local_logging = False
from litellm import completion as llm_completion
sys.stdout = original_stdout
# back to normal



def create_string(arg_data):

    arguments_dictionary_str =  "{\n"
    for key, value in arg_data.items():
        if isinstance(value, dict):
            arguments_dictionary_str += f"    '{key}': " + "{\n"
            for sub_key, sub_value in value.items():
                arguments_dictionary_str += f"        '{sub_key}': {sub_value},\n"
            arguments_dictionary_str += "    },\n"
        elif isinstance(value, (str, int, float)):
            arguments_dictionary_str += f"    '{key}': {value},\n"
        else:
            arguments_dictionary_str += f"    '{key}': {type(value)},\n"
    arguments_dictionary_str += "}\n"

    return arg_data

def extract_python_code_from_md(md_string):
    pattern = r'```python(.*?)```'
    matches = re.findall(pattern, md_string, re.DOTALL)
    python_code = '\n'.join([match.strip() for match in matches])
    return python_code

def get_runner_function(code_string):
    try:
        # Compile the code string
        code_object = compile(code_string, '<string>', 'exec')
        function_namespace = {}
        # Execute the code string
        exec(code_object, function_namespace)
        # Get the 'runner' function from the executed code
        runner_function = function_namespace.get('runner')
        if runner_function is None:
            raise RuntimeError("No function named 'runner' found in the code string.")
        return runner_function
    except Exception as e:
        raise RuntimeError("Failed to load the code string.") from e
    