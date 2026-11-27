The agent.py file defines a coding agent powered by Gemini.
It sets up a secure filesystem sandbox constrained by WORKING_DIR.
Key tools provided are list_files, read_file, write_file, and run_command.
All filesystem operations are validated to prevent unauthorized access.
The agent uses a structured system prompt to guide its behavior.
Tool schemas define how the model interacts with the local system.
The run_tool function maps tool names to their corresponding logic.
The main loop maintains a history of interaction steps for context.
It uses Google GenAI client for API calls and model interaction.
Finally, the agent CLI provides an interface to chat and execute tasks.