from templates import INSTRUCTION
from helpers import llm_completion, create_string, extract_python_code_from_md, get_runner_function

import logging
import os
import json




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
        
        response = self._generate_code_for_question(text)
        return response

    def _generate_code_for_question(self, question, retries_until_figured = 10):
        
        arg_data = {
            "context_variables": self.user_context_variables
        }
        
        
        arguments_dictionary_str =  create_string(arg_data)
        
        modules_metadata = ", ".join(self.assistant.pip_skills)

        instruction =INSTRUCTION.format(modules_metadata = modules_metadata, input_dictionary_string = arguments_dictionary_str, question=question)
        
        logging.debug("Generated Instruction: " + instruction)
        
        messages = [{"role": "system", "content": instruction}]
        error = 1
        for _ in range(retries_until_figured):
            try:
                resp = self.assistant._m(messages) 
                code = resp['choices'][0]['message']['content']
       
                function_code = extract_python_code_from_md(code)
                if function_code is not None:
                    code = function_code
        
                logging.debug("Generated Code: " + code)
                runner_function = get_runner_function(code)

                result = runner_function(input=arg_data)
                break
            except Exception as e:
                logging.debug("Exception occurred: " + str(e))
                logging.debug("Trying again: " + str(error))
                error += 1
                
                continue
        logging.debug("Result: " + str(result))
        
        return result



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
    #eve.add_skill(pip_module="pandas")

    # Start a conversation and add user specific context (variable names must be interpretable, Otto will take care of the rest)
    # In this case the assistant will need access token to github, this is so you can pass context dynamically (solving for multitenancy)
    conversation = eve.start_conversation(user_name = "Bob", user_context_variables = {"github_api_token":os.getenv("GITHUB_TOKEN")} ) 

    # ask a question
    response = conversation.message("Who were the first 5 people to star the mindsdb/otto repo?")
    print(json.dumps(response, indent=4))



