<img src="https://github.com/mindsdb/otto/assets/5898506/c1205022-7f73-41cc-82ea-8075801bdbd4" alt="description" style="width: 20%;" />


# Otto: The minimalistic Agent Framework


Welcome to Otto, the most minimalistic library for building intelligent AI Agents straight from Python Objects adept for also handling agent multitenancy and secure authentication.

```
pip install ottoai
```

An agent that learns how to answer questions about Github straight from the github python SDK!

```Python
import ottoai
import openai
from github import Github, Auth


# setup your openAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# create an agent
otto = ottoai.Agent(llm_engine=openai, model="model="gpt-3.5-turbo-0613")

# create a Github object from Github official SDK
github_sdk_object = Github(auth=Auth.Token(os.getenv("GITHUB_TOKEN")))

# Make your agent capable of answering questions, act over anything regarding Github, by simply passing the object
otto.add_skill(github_sdk_object)

# Ask some questions
print(otto.ask("Who was the last person to star the mindsdb/mindsdb repo?"))

```

As simple as that, no need to build tools or chaining, just pass objects as skills, otto figures out the rest.

