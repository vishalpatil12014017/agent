from dotenv import load_dotenv
load_dotenv()

from litellm import completion
import json


# 1. Define the actual Python function we want our agent to have
def get_weather(city: str) -> str:
    """Mock weather function (in reality, you'd call a real weather API)"""
    if "mumbai" in city.lower():
        return "32°C, Sunny and humid"
    elif "london" in city.lower():
        return "15°C, Rainy"
    else:
        return "22°C, Partly cloudy"

# 2. Describe this tool to Gemini (This is the JSON schema menu!)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to look up weather for, e.g. Mumbai, Tokyo"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 3. Ask Gemini a question that REQUIRES the tool
user_prompt = "What's the weather like in pune right now?"

response = completion(
    model="gemini/gemini-3.5-flash-lite",
    messages=[{"role": "user", "content": user_prompt}],
    tools=tools,               # <-- We give Gemini our tool menu!
    tool_choice="auto"          # <-- Let Gemini decide whether to use it
)

# 4. Inspect what Gemini gave back
message = response.choices[0].message

print("--- What Gemini returned ---")
print("Text content:", message.content)
print("Tool calls:", message.tool_calls)


# 5. Check if Gemini requested any tool calls
if message.tool_calls:
    for tool_call in message.tool_calls:
        # Check which function Gemini wants to run
        if tool_call.function.name == "get_weather":
            # Parse the JSON arguments string from Gemini (like JSON.parse in JS)
            args = json.loads(tool_call.function.arguments)
            
            # Execute your actual local Python function!
            weather_data = get_weather(city=args["city"])
            print(f"\n⚡ Executed local function: get_weather({args['city']}) -> {weather_data}")

            # 6. Append Gemini's tool call AND your tool's result to conversation history
            messages = [
                {"role": "user", "content": user_prompt},
                message,  # Gemini's request to run the tool
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": weather_data  # The observation!
                }
            ]

            # 7. Call Gemini a 2nd time so it can synthesize the final answer
            final_response = completion(
                model="gemini/gemini-3.5-flash-lite",
                messages=messages
            )
            
            print("\n🤖 Final Agent Response:")
            print(final_response.choices[0].message.content)
