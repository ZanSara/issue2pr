import os
import sys
import json
import subprocess
import openai

SYSTEM_PROMPT = """
You are a contributor to an open source library.
You have created a patch that will fix one specific issue.
Given the description of the issue and the patch file, write
down an explanation for the maintaners that can help them 
understand in detail your changes and review them.

Use a professional and helpful tone. Explain the patch in detail
but never repeat yourself. Be as clear and concise as possible.
You can use markdown to highlight code and structure your reply.
"""

def explain_pr(issue_content, patch_path="changes.patch"):
    issue_data = json.loads(issue_content)
    patch = ""
    with open(patch_path, 'r') as patch_file:
        patch = patch_file.read()

    prompt = f"ISSUE:\n\n{issue_data}\n\nPATCH:{patch}\n\nEXPLANATION:"
    print("\n#---------#\n"+prompt+"\n#---------#\n")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
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
