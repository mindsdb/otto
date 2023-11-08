

# This is the instruction to be passed to the LLM

INSTRUCTION = """

You write python code and code alone, try to find the simplest solution to the question.
Write a Python function called 'runner' that answers the following question:

{question}

Follow these instructions to write the function:

- make sure the function returns a readable string
- do not make imports other than ({modules_metadata}), and of those only use the minimum necessary
- the function takes only one argument called 'input' as as follows:

input={input_dictionary_string}

"""