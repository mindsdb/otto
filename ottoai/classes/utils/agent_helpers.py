import logging
import sys
import os
import json

# Import litellm, but its verbose, and no one really wants that
# so we will turn off stout
original_stdout = sys.stdout 
# Redirect stdout to null
sys.stdout = open(os.devnull, 'w')
from litellm import completion as llm_completion
sys.stdout = original_stdout
# back to normal

from collections.abc import Iterable
from inspect_helpers import generate_openai_function_spec, get_castable_attributes, is_iterable_not_str

# constants
from constants import LLM_INIT_FUNCTION_MESSAGES, NOT_FOUND_STRING



def get_method_and_args(object, messages, llm_model = 'gpt-4',  max_functions_per_request=40, completion_function = llm_completion):

    
    llm_messages_init = messages.copy()

    
    object_functions = generate_openai_function_spec(object)
    message_content = None
    finish_reason =  None

    def get_possible_functions(functions, llm_messages):
        
        global message_content, finish_reason
        possible_functions = {}
        
        while len(functions) > 0:
            
            remaining_functions = []
            if len(functions) > max_functions_per_request:
                first_functions = functions[:max_functions_per_request]
                remaining_functions = functions[max_functions_per_request:]
                functions = first_functions

            logging.debug("Functions: %s", json.dumps(functions, indent=4))

            response = completion_function(
                model=llm_model,
                messages=llm_messages,
                functions= functions,
                function_call="auto",  # auto is default, but we'll be explicit
            )

            

            if len(response["choices"]) == 0: 
                continue
            
            logging.debug("possible Function Names: %s", json.dumps([i["name"] for i in functions], indent=4))
            logging.debug("Response: %s", json.dumps(response, indent=4))

            response_message = response["choices"][0]["message"]
            message_content = response_message['content']
            finish_reason =  response["choices"][0]['finish_reason']

            if "function_call" in response_message:
                function_name = response_message["function_call"]["name"]
                
                possible_functions[function_name] = response_message["function_call"]["arguments"]
                #function_response = function_to_call(**function_args)

            functions = remaining_functions
        
        return possible_functions


    possible_functions = get_possible_functions(object_functions,llm_messages_init)

    
    if len(possible_functions) > 1:
        logging.debug("More than one possible functions found: %s", json.dumps(possible_functions, indent=4))
        possible_functions=get_possible_functions([funct for funct in object_functions if funct["name"] in possible_functions], llm_messages_init)
    
    logging.debug("Final selected function: %s", json.dumps(possible_functions, indent=4) )
    response = possible_functions
    response['content'] = message_content
    response['finish_reason'] = finish_reason
    return possible_functions

    

class IterResponseCommands:

    def __init__(self, iterable_object: Iterable):
        """
        Initialize the IterResponseCommands class.

        Parameters:
        iterable_object (iterable): The iterable object to be processed.
        """
        self.iterable_object = iterable_object

    def iterate_over_items(self):
        """
        Retrieve an item from the iterable object at a time, everytime this is called, it moves the pointer.

        Parameters:

        Returns:
        The item at the specified index in the iterable object.
        """
        
        for row in iter(self.iterable_object):
            yield row
        
        #return self.iterable_object[0]

    def run_python_code_over_list_of_dicts(self, limit: int = 100, code_string: str = ''):
        """
        Run a piece of Python code over a list of dictionaries.

        Parameters:
        limit (int): The maximum number of items to process from the iterable object.
        code_string (str): The Python code to be executed, code must have a variable called result, where results are stored and should include no modules.

        Returns:
        The result of the executed Python code, or an error message if an exception occurred.
        """
        list_of_dicts = []
        count = 0
        for row_object in self.iterable_object:
            
            attributes = get_castable_attributes(row_object)
            list_of_dicts.append(attributes)
            count +=1
            if count == limit:
                break
            
       
        local_vars = {"list_of_dicts": list_of_dicts}
        global_vars = {}
        try:
            exec(code_string, global_vars, local_vars)
        except Exception as e:
            return {"error": str(e)}
        return local_vars.get("result", None)



# def send_to_llm_and_call_results(object, llm_messages):

#     method_and_params = get_method_and_args(object, messages=llm_messages)
#     method_name = list(method_and_params.keys())[0]
#     method_args = json.loads(method_and_params[method_name])

#     function_to_call = getattr(github_sdk_object, method_name)
#     function_result = function_to_call(**method_args)

#     logging.debug(f"Function result: {function_result}")
#     llm_messages += [
#         {"role": "system", "content": "call function: {method_name} with params: {params}".format(method_name=method_name, params=str(method_args))},
#         {"role": "system", "content": "Function returned: {iter_item}".format(iter_item=type(function_result))}
#     ]

#     return function_result


# def iterate_over_object_until_answer(object, question):

#     question = "Who was the last person to star the mindsdb/mindsdb repo?"
#     llm_messages = LLM_INIT_FUNCTION_MESSAGES + [
#             {"role": "user", "content": question},
#     ]

#     logging.debug("Question: %s", question)
#     logging.debug("LLM Init Messages: %s", json.dumps(llm_messages, indent=4))


#     while True:
#         object_to_pass = object
#         function_result = send_to_llm_and_call_results(object_to_pass, question)



        



if __name__ == "__main__":
    pass
    # Assuming `some_sdk_object` is an instantiated object from an SDK module
    # from github import Github, Auth
    # import os
    # logging.basicConfig(level=logging.DEBUG)
    # github_sdk_object = Github(auth=Auth.Token(os.getenv("GITHUB_TOKEN")))
    # question = "Who was the last person to star the mindsdb/mindsdb repo?"
    # llm_messages = LLM_INIT_FUNCTION_MESSAGES + [
    #         {"role": "user", "content": question},
    # ]
    # method_and_params = get_method_and_args(github_sdk_object, question, messages=llm_messages)
    # method_name = list(method_and_params.keys())[0]
    # method_args = json.loads(method_and_params[method_name])
    # function_to_call = getattr(github_sdk_object, method_name)
    # function_result = function_to_call(**method_args)

    # logging.debug(f"Function result: {function_result}")
    # if is_iterable_not_str(function_result):
    #     llm_messages = LLM_INIT_FUNCTION_MESSAGES + [
    #         {"role": "user", "content": question},
    #         {"role": "system", "content": "call function: {method_name} with params: {params}".format(method_name=method_name, params=str(method_args))},
    #         {"role": "system", "content": "Function was called and it resulted in iterable object: {iter_item}".format(iter_item=type(function_result))}
    #     ]
    #     iterable_object = IterResponseCommands(function_result)
    #     method_and_params = get_method_and_args(iterable_object, question, messages=llm_messages)
        
    #     method_name = list(method_and_params.keys())[0]
    #     method_args = json.loads(method_and_params[method_name])
    #     function_to_call = getattr(iterable_object, method_name)
    #     function_result2 = function_to_call(**method_args)

    #     llm_messages = llm_messages + [
    #         {'role': 'system', 'content': "call function: {method_name} with params: {params}".format(method_name=method_name, params=str(method_args))},
    #         {"role": "system", "content": "Function was called and it resulted in: {iter_item}".format(iter_item=type(function_result))}
    #     ]

    #     method_and_params = get_method_and_args(function_result2, question, messages=llm_messages)
        
        
    #     for row_object in function_result:
            
    #         attributes = get_castable_attributes(row_object)
    #         logging.debug("Attributes of object: %s", json.dumps(attributes, indent=4))
    #         break
    #     #get_method_and_args(next(iter(function_result)), "Who was the last person to star the mindsdb/mindsdb repo?")
    