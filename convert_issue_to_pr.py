import os
import sys
import json
import subprocess
import openai

SYSTEM_PROMPT = """
You are be given a codebase and an issue. Output a patch that will fix the issue.
Do not describe your output. Do not apologize in case of mistakes. 
Always output ONLY THE PATCH, with NO ADDITIONAL TEXT.
This is extremely important and will make the system fail if you do not comply.
Only output the git patch that fixes the issue.
The output will be piped directly to a file and applied to the repository, 
so make sure the syntax is fully valid and includes only the patch. 
If the patch is wrong, you will receive the error that was generated and you 
should output a new patch that addresses the error.
"""


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
            codebase_content += "FILE: " + codebase + "/" + file_to_load + ":\n\n"
            with open(codebase + "/" + file_to_load, 'r') as code_file:
                codebase_content += f"{code_file.read()}\n\n\n"

    prompt = f"CODEBASE:\n\n{codebase_content}\n\nISSUE:\n\n{issue_data}"
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
        
        with open("changes.patch", "w") as patch_file:
            patch_file.write(reply)

        apply_patch="git apply --ignore-space-change --ignore-whitespace changes.patch"
        try:
            apply_command = subprocess.run(apply_patch, shell=True, check=True)
            break
        except:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "error: the patch is invalid."})

        print("FAILED!")

    reply = reply.replace('"', "\"")  # Bash
    return reply


if __name__ == "__main__":
    openai.api_key = sys.argv[1]
    print(issue_to_pr(issue_content=sys.argv[2], codebase=sys.argv[3]))
