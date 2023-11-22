

# This is the instruction to be passed to the LLM

INSTRUCTION = """

You write python code, write the simplest and most effective Python function to answer the following.

Question: {question}

Follow these instructions to write the function:

- The function must be called 'runner' 
- code should only have the necessary imports and the function runner
- The function shall return a response to the question
- Only import the fewest possible pip modules from this list: ({modules_metadata}), 
- Import the minimum number of modules necessary
- The function takes only one argument called 'input' as as follows:

input={input_dictionary_string}

"""