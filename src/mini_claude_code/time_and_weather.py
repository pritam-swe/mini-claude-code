from google import genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
MODEL = "gemini-3.1-flash-lite"
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

## tool schema or declaration
weather_tool = {
    "type": "function",
    "name": "get_current_temp",
    "description": "Gets the current temperature for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. Kolkata"
            }
        },
        "required": ["location"]
    },
}

time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": (
        "Gets the current local date and time for a city. "
        "Pass the city name, not a country with multiple time zones."
        
        "If the tool returns an unknown-location error, "
        "do not guess another city or retry with unrelated locations. "
        "Ask the user to clarify the city and country."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, e.g. Delhi, London or Tokyo."
            }
        },
        "required": ["location"]
    },
}

# City-to-IANA-timezone mapping
TIMEZONE_MAP = {
    "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "london": "Europe/London",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
}

def get_current_temp(location: str):
    return {"location": location, "temperature": "22", "unit": "celsius"}

def get_current_time(location: str):
        normalized_location = location.strip().lower()
        timezone_name = TIMEZONE_MAP.get(normalized_location)
        try:
            if timezone_name:
                now = datetime.now(ZoneInfo(timezone_name))

            else:
                # timezone_name = "UTC"
                # now = datetime.now(timezone.utc)
                return {
                    "error": f"Unknown location: {location}. Please specify a supported city."
                }

            return {
                "location": location, 
                "timezone": timezone_name,
                "time": now.strftime("%H:%M:%S") , 
                "format": "24h",
                "date": now.strftime("%Y-%m-%d"),
                "day": now.strftime("%A"),
                "utc_offset": now.strftime("%z"),
            }
        except ZoneInfoNotFoundError:
            return {"error": f"Timezone data unavailable: {timezone_name}"}


available_functions = {
    "get_current_temp" : get_current_temp,
    "get_current_time" : get_current_time,
    
}


## stateless management
history = []

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

            while True:
                interaction = client.interactions.create(
                    model=MODEL,
                    input=history,
                    store=False, ## imp
                    tools=[weather_tool, time_tool],   ##array of all tools
                    )
                
                function_results = []
                for step in interaction.steps:
                    history.append(step.model_dump())
                    if step.type == "function_call":
                        result = available_functions[step.name](**step.arguments)
                        print(f"Called {step.name}({step.arguments}) → {result}")

                        fn_result = {
                            "type": "function_result",
                            "name": step.name,
                            "call_id": step.id,
                            "result": [{"type": "text", "text": json.dumps(result)}]
                        }
                        function_results.append(fn_result)
                        history.append(fn_result)
                        # print(fn_result)
                if not function_results:
                    print(f"Bot: {interaction.output_text}")
                    break


    except (KeyboardInterrupt, EOFError):
        print("\nBot: Goodbye!")
    finally:
        client.close()

if __name__ == '__main__':
    main()