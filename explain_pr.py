import os
import sys
import json
import subprocess
import openai

SYSTEM_PROMPT = lambda issue, diff: f"""
You are a contributor to an open source library called `math-in-python`.
You just opened a PR to fix this issue:

```
{issue}
```

Your PR is the following:

```
{diff}
```

Write down an explanation for the maintaners that can help them 
understand in detail your changes and review them.

Use a professional tone. 
Explain the PR in detail but never repeat yourself. 
Be as clear and concise as possible.
You can use markdown to structure your reply.
"""

def explain_pr(issue_content, patch_path="changes.patch"):
    issue_data = json.loads(issue_content)
    patch = ""
    with open(patch_path, 'r') as patch_file:
        patch = patch_file.read()

    prompt = SYSTEM_PROMPT(f"# {issue_data['title']}\n\n{issue_data['body']}", patch)
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = response["choices"][0]["message"]["content"]
    print("\n---------\n"+reply+"\n---------\n")
    
    reply = reply.replace('"', "\"")  # Bash
    return reply


if __name__ == "__main__":
    openai.api_key = sys.argv[1]
    print(explain_pr(issue_content=sys.argv[2]))
