from utils.inspect_helpers import generate_openai_function_spec
from utils.agent_helpers import llm_completion
from utils.constants import LLM_INIT_FUNCTION_MESSAGES

class AgentSkill:

    def __init__(self, object_to_based_skill_on, llm_model, llm_complete_function = llm_completion):

        self.skill_object = object_to_based_skill_on
        self.skill_functions = generate_openai_function_spec(object_to_based_skill_on)
        
    
    def ask_stream(self, question):

        messages = LLM_INIT_FUNCTION_MESSAGES + [
            {'role': 'user', 'content': question}
        ]

        yield ''

    
    def ask(self, q):

        results = []
        for response in self.ask_stream(q):
            results.append(response)
        return ' '.join(results)


class Question:

    def __init__(self, question):
        self.question = question
        # we may neeed to keep a log of what has been tried so it doesnt do it again (dead loop)
        self.messages = LLM_INIT_FUNCTION_MESSAGES + [
            {'role': 'user', 'content': question}
        ] # history of messages to answer this question 


    def answer_stream(self):
        

        yield ''