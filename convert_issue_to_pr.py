import os
import sys
import json
import subprocess
import openai

SYSTEM_PROMPT = """
You are a Bash interactive utility called issue2pr. You are given a codebase and an issue.
Respond with the content of a patch file that will fix the issue.
Do not describe your output. Do not apologize in case of mistakes. Use plaintext, no markdown.
Do not prepend the 'diff' command used to create the patch. Do not add any closing quotes.
DO NOT add anything that makes the patch file invalid.

Always respond with ONLY THE OUTPUT OF 'diff -u', with NO ADDITIONAL TEXT OR FORMATTING.

This is EXTREMELY IMPORTANT and will make the system fail if you do not comply.
Only respond with the content of the git patch that fixes the issue.
If the patch is wrong, you will receive the error that was generated. You need to keep
behaving as a Bash utility and reply only with a new patch that addresses the error,
as before."""


def issue_to_pr(codebase, issue_content):
    issue_data = json.loads(issue_content)

    codebase_content = ""
    files_to_load = os.listdir(codebase)
    while files_to_load:
        file_to_load = files_to_load.pop()
        print(f"Processing {file_to_load}...")
        
        if os.path.isdir(file_to_load) and ".git" != file_to_load:
            print(f"   is a dir")
            files_to_load += [file_to_load + "/" + filename for filename in os.listdir(codebase + "/" + file_to_load)]
        
        elif os.path.isfile(file_to_load) and not "convert_issue_to_pr.py" in file_to_load and not "explain_pr.py" in file_to_load:
            print(f"   is a file")
            codebase_content += "Another file? Y\nAdd a file: " + codebase + "/" + file_to_load + "\n\n"
            with open(codebase + "/" + file_to_load, 'r') as code_file:
                codebase_content += f"{code_file.read()}\n\n"

    prompt = f"""
> issue2pr
1. Load your codebase
{codebase_content}Another file? N

2. Describe the issue:
{issue_data["title"]}
{issue_data["body"]}

Solving your issue...
Patch to apply:
"""
    print("\n#---------#\n"+prompt+"\n#---------#\n")
    
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    for i in range(3):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
        reply = response["choices"][0]["message"]["content"]

        print("\n---------\n"+reply+"\n---------\n")

        reply = reply.replace("--- a/", "--- /home/runner/work/test-issue2pr/test-issue2pr/")
        reply = reply.replace("+++ b/", "+++ /home/runner/work/test-issue2pr/test-issue2pr/")

        clean_reply = "\n".join([line for line in reply.split("\n") if not line.startswith("```") and not line.startswith("diff -u")])

        
        with open("changes.patch", "w") as patch_file:
            patch_file.write(reply + "\n")

        apply_patch="cd / & patch -i changes.patch"
        try:
            apply_command = subprocess.run(apply_patch, shell=True, check=True)
            break
        except:
            pass
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "git: the patch is invalid.\n Solving your issue...\nPatch to apply:"})

        print("FAILED!")

    reply = reply.replace('"', "\"")  # Bash
    return reply


if __name__ == "__main__":
    openai.api_key = sys.argv[1]
    print(issue_to_pr(issue_content=sys.argv[2], codebase=sys.argv[3]))
