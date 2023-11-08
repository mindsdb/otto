from inspect_helpers import generate_openai_function_spec, inspect_object
from agent_helpers import llm_completion
from constants import LLM_INIT_FUNCTION_MESSAGES
import inspect
import json
import re


class Assistant:
    """
    The Assistant class is responsible for managing the skills and conversations.
    """
    def __init__(self, name: str, personality: str, llm_engine, model: str):
        """
        Initialize the assistant with a name, personality, language model engine, and model.
        """
        self.name = name
        self.personality = personality
        self.llm_engine = llm_engine
        self.model = model
        self.pip_skills = []
         
    
    def _m(self, messages):
        return llm_completion(model=self.model, messages=messages)
        


    def add_skill(self, pip_module):
        """
        Add a new skill to the assistant.
        """
        
        self.pip_skills.append(pip_module)
            
        
        

    def start_conversation(self, user_name: str, user_context_variables: dict):
        """
        Start a new conversation with the user.
        """
        return Conversation(self, user_name, user_context_variables)



class Conversation:
    """
    The Conversation class is responsible for managing the conversation between the user and the assistant.
    """
    def __init__(self, assistant: Assistant, user_name: str, user_context_variables: dict):
        """
        Initialize the conversation with the assistant, the user's name and context variables.
        """
        self.assistant = assistant
        self.user_name = user_name
        self.user_context_variables = user_context_variables

    def message(self, text: str):
        """
        Send a message to the assistant and return the assistant's response.
        """
        question = ManageQuestion(
            assistant = self.assistant,
            conversation = self
        )
        response = question.generate_code_for_question(text)
        return response

INSTRUCTION = """
You write python code and code alone  
Write a Python function called 'runner' that answers the following question:

{question}

Follow these instructions to write the function:

- make sure the function returns a readable string
- do not make imports other than ({modules_metadata})
- the function takes only one argument called 'input' as as follows:

input={input_dictionary_string}


"""

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
    
class ManageQuestion:

    def __init__(self, assistant: Assistant, conversation: Conversation) -> None:
        self.assistant = assistant
        self.conversation = conversation

    def generate_code_for_question(self, question):
        
        arg_data = {
            "context_variables": self.conversation.user_context_variables
        }
        
        
        arguments_dictionary_str =  create_string(arg_data)
        
        modules_metadata = ", ".join(self.assistant.pip_skills)

        instruction =INSTRUCTION.format(modules_metadata = modules_metadata, input_dictionary_string = arguments_dictionary_str, question=question)
        
        print(instruction)
        
        messages = [{"role": "system", "content": instruction}]

        resp = self.assistant._m(messages) 
        code = resp['choices'][0]['message']['content']
       
        function_code = extract_python_code_from_md(code)
        if function_code is not None:
            code = function_code
        
        print(code)
        runner_function = get_runner_function(code)

        print(runner_function(input=arg_data))
        # return function

    
if __name__ == "__main__":
    import github
    import pandas 
    import os
    import openai
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import json

    # create an assistant
    eve = Assistant(name="eve", personality="Like Scarlett Johansson with John Oliver's wits", llm_engine=openai, model="gpt-4")

    # Make your agent capable of answering questions and do all things Github, by simply passing the sdk module
    # Remember. Just pass objects as skills, and Otto will figure out the rest. 
    eve.add_skill(pip_module='PyGithub')
    eve.add_skill(pip_module="pandas")

    # Start a conversation and add user specific context (variable names must be interpretable, Otto will take care of the rest)
    # In this case the assistant will need access token to github, this is so you can pass context dynamically (solving for multitenancy)
    conversation = eve.start_conversation(user_name = "Bob", user_context_variables = {"github_api_token":os.getenv("GITHUB_TOKEN")} ) 

    # ask a question
    response = conversation.message("Who were the first 5 people to star the mindsdb/mindsdb repo?")
    print(json.dumps(response, indent=4))



