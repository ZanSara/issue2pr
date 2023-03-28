import sys
import json
import argparse
import openai


def issue_to_pr(issue_content):
    issue_data = json.loads(issue_content)

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide a very concise answer."},
            {"role": "user", "content": "How do people greet each other in French?"},
        ]
    )
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--openai-api-key', required=True)
    parser.add_argument('-c','--issue-content', required=True)
    args = vars(parser.parse_args())

    openai.api_key = args["issue_content"]

    print(issue_to_pr(issue_content=args["issue_content"]))
