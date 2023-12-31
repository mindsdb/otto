<img src="https://github.com/mindsdb/otto/assets/5898506/c1205022-7f73-41cc-82ea-8075801bdbd4" alt="description" style="width: 20%;" />


# Otto: The minimalistic Framework to build AI Assistants 


Welcome to Otto, the most minimalistic library for building intelligent AI Assistants, adept for also handling multitenancy and secure authentication.

```
pip install ottoai
```


## Example

Turn the Github SDK into an agent that can answer questions from Github live data using pandas to calculate results.

```Python
import os
import openai
import logger
logging.basicConfig(level=logging.DEBUG)
import json

# create an assistant
eve = Assistant(name="eve", personality="Like Scarlett Johansson with John Oliver's wits", llm_engine=openai, model="gpt-4-1106-preview")

# Make your agent capable of answering questions and do all things Github, by simply passing the sdk module
# Remember. Just pass objects as skills, and Otto will figure out the rest. 
eve.add_pip_skill(pip_module='PyGithub')

# Start a conversation and add user specific context (variable names must be interpretable, Otto will take care of the rest)
# In this case the assistant will need access token to github, this is so you can pass context dynamically (solving for multitenancy)
eve.set_user_context_variables({"github_api_token":os.getenv("GITHUB_TOKEN")}) 

# ask a question
response = eve.question("Who were the last 5 people to star the mindsdb/otto repo?")
print(json.dumps(response, indent=4))



```

As simple as that, no need to build tools or chaining, just pass objects as skills, otto figures out the rest.

