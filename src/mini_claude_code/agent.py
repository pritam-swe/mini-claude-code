import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.1-flash-lite"

client = genai.Client(api_key=GEMINI_API_KEY)

WORKING_DIR = Path.cwd().resolve()

MAX_TOOL_ROUNDS = 10


SYSTEM_PROMPT = """
You are a coding agent running in the user's terminal.

You can:
- List files
- Read files
- Write files
- Run shell commands

Use your tools to complete the user's task.
Inspect relevant files before modifying them.
Do not claim that an operation succeeded unless the tool confirms it.
Briefly summarize what you did.

The working directory is the folder from which the user launched you.
"""

# --------------------------------------------------
# Filesystem safety
# --------------------------------------------------

def resolve_path(path):
    target = (WORKING_DIR / path).resolve()

    if not target.is_relative_to(WORKING_DIR):
        raise PermissionError("Access outside the working directory is not allowed.")

    return target



def list_files(path="."):
    target = resolve_path(path)
    if not target.is_dir():
        raise NotADirectoryError(path)

    entries = []
    with os.scandir(target) as directory:
        for entry in directory:
            suffix = "/" if entry.is_dir(follow_symlinks=False) else ""
            entries.append(entry.name + suffix)        
    return "\n".join(sorted(entries)) or "(empty directory)"


def read_file(path):
    target = resolve_path(path)
    if not target.is_file():
        raise FileNotFoundError(path)
    return target.read_text(encoding="utf-8")


def write_file(path, content):
    target = resolve_path(path)

    if target.exists():
        answer = input(f"  Overwrite '{path}'? [y/N] ")

        if answer.strip().lower() != "y":
            return "The user declined to overwrite this file."

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"Saved {path} ({len(content)} characters)"


def run_command(command):
    answer = input(f"  Run '{command}'? [y/N] ")

    if answer.strip().lower() != "y":
        return "The user declined to run this command."
    
    result = subprocess.run(
        command, 
        shell=True, 
        cwd=WORKING_DIR,
        capture_output=True,
        text=True, 
        timeout=120
    )
    output = (result.stdout + result.stderr).strip()
    return (
        f"Exit code: {result.returncode}\n{output}"
        if output
        else f"(no output, exit code {result.returncode})"
    )


TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "list_files",
        "description": (
            "List the files in a directory. Folders end with /."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string", 
                    "description": "Directory to list, e.g. '.'"
                },
            },
            "required": ["path"],
        },
        },

    {
        "type": "function",
        "name": "read_file",
        "description": (
            "Read a text file and return its contents."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string", 
                    "description": "Path of the file to read"
                },
            },
            "required": ["path"],
        },
        },
 
    {
        "type": "function",
        "name": "write_file",
        "description": (
            "Create or overwrite a text file with the given content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string", 
                    "description": "Path of the file to write",
                },
                "content": {
                    "type": "string", 
                    "description": "Full contents of the file"
                }
            },
            "required": ["path","content"],
        },
        },


    {
        "type": "function",
        "name": "run_command",
        "description": (
            "Run a shell command and return its output. The user approves it first."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string", 
                    "description": "The shell command to run",
                }
            },
            "required": ["command"],
        },
        },


]


def run_tool(function_call):
    name = function_call.name
    arguments = function_call.arguments
    print(f"\n  tool: {name}({arguments})")
    
    function = TOOLS.get(name)

    if function is None:
        return {"error": f"Unknown tool: {name}"}

    try:
        result = function(**arguments)
        # print(f"  Result: {result}")
        return {"result": result}

    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(f"  Tool error: {error_message}")
        return {"error": error_message}



def run_agent(history):
    while True:
        interaction = client.interactions.create(
            model=MODEL,
            system_instruction=SYSTEM_PROMPT,
            input=history,
            store=False,
            tools=TOOL_SCHEMAS,
        )

        function_results = []
        for step in interaction.steps:
            history.append(step.model_dump())
        # No tool calls means the model is done and answered in plain text
            if step.type == "function_call":
                # result = TOOLS[step.name](**step.arguments)
                result = run_tool(step)
                print(f"Called {step.name}({step.arguments})")

                # Prepare the function result for Gemini.
                fn_result = {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(result)}]
                }

                function_results.append(fn_result)
                history.append(fn_result)

        if not function_results:
            # print(f"Bot: {interaction.output_text}")
            return interaction.output_text
            
       
def main():
    print("Mini agent ready. Type 'exit' to quit.")
    
    history = []      
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ("exit", "quit"):
                print("Bye")
                break
            history.append({"type": "user_input", 
                            "content": [
                                {
                                    "type":"text",
                                    "text": user_input
                                }
                            ]})
            reply = run_agent(history=history)
            print(f"\nAgent: {reply}")
    except Exception as error:
        print(f"\nAgent error: {type(error).__name__}: {error}")

    finally:
        client.close()

if __name__ == "__main__":
    main()
