# otto
A minimalistic framework for adding skills to LLMs, taking into account agent multi-tenancy.

```python

import ottoai

otto = ottoai.Project('folder or github repo')

otto.run_admin()

```

This will launch an agent that you can start a conversation with and start adding skills to.

```bash

Otto: "Hi! my name is Otto (you can change my name), can you describe what you want to do in this project?"
You: "I want to create a virtual assistant, that people can CC in conversations, and the assistant will help with whatever is requested."
Otto: "Perfect, let me create the boiler plate code for you."

" - We are going to add the following skill: email"
j

```



