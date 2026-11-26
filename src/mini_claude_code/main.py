from google import genai
import os
from dotenv import load_dotenv

MODEL = "gemini-3.1-flash-lite"
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

## stateless management
history = [
    # {
    #     "type": "user_input",
    #     "content": [{"type": "text", "text": "I'm Pritam, a software engineer."}]
    # }
]

def main():
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in ("exit", "quit", "q"):
                print("\nBot: Bye!")
                break
            
            history.append({
                "type": "user_input",
                "content": [
                    {
                        "type": "text", 
                        "text": user_input
                    }
                ]
            })

            #send complete conv history
            interaction = client.interactions.create(
                model=MODEL,
                input=history,
                store=False ## imp
            )

            reply = interaction.output_text

            print("Bot: ", reply)

            ## have to preserve all the model-generated steps
            for step in interaction.steps:
                history.append(step.model_dump())

    except (KeyboardInterrupt, EOFError):
        print("\nBot: Goodbye!")
    finally:
        client.close()

if __name__ == '__main__':
    main()