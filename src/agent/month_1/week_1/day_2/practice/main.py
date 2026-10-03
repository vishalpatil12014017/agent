import json

from pydantic import BaseModel, Field
from litellm import completion, utils
from agent.constant import LLM_MODEL, GEMINI_API_KEY
print(LLM_MODEL)

# ==========================================
# 1. DEFINE TOOL INPUT SCHEMAS WITH PYDANTIC
# ==========================================
# Think of this exactly like z.object({...}) in Zod
class WeatherSearch(BaseModel):
    city: str = Field(description="The city to get weather for, e.g. Mumbai, Tokyo")
    unit: str = Field(default="celsius", description="Temperature unit: 'celsius' or 'fahrenheit'")

class CurrencyConvert(BaseModel):
    amount: float = Field(description="The amount of money to convert")
    from_currency: str = Field(description="3-letter source currency code, e.g. USD, EUR, INR")
    to_currency: str = Field(description="3-letter target currency code, e.g. USD, EUR, INR")

# ==========================================
# 2. AUTO-GENERATE TOOL SCHEMAS
# ==========================================
# No more manual JSON dictionaries! 
# We use LiteLLM's helper or standard schema dumping:
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city with unit preference",
            "parameters": WeatherSearch.model_json_schema()  # <-- AUTO-GENERATED!
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert money between currencies",
            "parameters": CurrencyConvert.model_json_schema()  # <-- AUTO-GENERATED!
        }
    }
]

# Let's inspect what Pydantic generated for us:
print("🔍 Pydantic Auto-Generated Schema for CurrencyConvert:")
print(json.dumps(CurrencyConvert.model_json_schema(), indent=2))
print("=" * 60)

# ==========================================
# 3. TEST WITH GEMINI
# ==========================================
prompt = "How much is 1500 USD in INR, and what is the weather in Mumbai in celsius?"

messages = [
    {"role": "user", "content": prompt}
]

response = completion(
    model=LLM_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message

# ==========================================
# 4. VALIDATE MODEL OUTPUT WITH PYDANTIC
# ==========================================
print("\n🤖 Gemini Decided to Call the following tools:")

if message.tool_calls:
    for tc in message.tool_calls:
        tool_name = tc.function.name
        raw_args = json.loads(tc.function.arguments)
        
        print(f"\n👉 Tool: {tool_name}")
        print(f"   Raw JSON from LLM: {raw_args}")

        # VALIDATION STEP: Pass raw JSON into Pydantic model
        # If the LLM passed a string instead of a number, Pydantic catches it!
        if tool_name == "get_weather":
            validated = WeatherSearch(**raw_args)
            print(f"   ✅ Pydantic Validated Object: city='{validated.city}', unit='{validated.unit}'")
        elif tool_name == "convert_currency":
            validated = CurrencyConvert(**raw_args)
            print(f"   ✅ Pydantic Validated Object: amount={validated.amount}, from={validated.from_currency}, to={validated.to_currency}")