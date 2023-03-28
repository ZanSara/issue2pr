import sys
import json
import openai


def issue_to_pr(codebase, issue_content):
    issue_data = json.loads(issue_content)

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {
                "role": "system", 
                "content": """
                    You are a code assistant. You will be given a codebase and an issue. 
                    You should reply with a patch that will fix the issue.
                    Do not describe your output. Only output the git patch that fixes the issue. 
                    The output will be piped to a file and applied to the repository, so make sure the syntax is valid.
                """
            },
            {
                "role": "user", 
                "content": f"CODEBASE:\n\n{codebase}\n\nISSUE:\n\n{issue_data}\n\nPATCH:"
            }
        ]
    )
    reply = response["choices"][0]["message"]["content"]
    reply = reply.replace('"', "\"")  # Bash
    return reply


if __name__ == "__main__":
    openai.api_key = sys.argv[1]
    print(issue_to_pr(issue_content=sys.argv[2], codebase=sys.argv[3]))
