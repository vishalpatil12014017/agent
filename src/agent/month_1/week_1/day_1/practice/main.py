from dotenv import load_dotenv
load_dotenv()  # Loads GEMINI_API_KEY from your .env file!

import os
from litellm import completion

# 1. Ask Gemini a question
response = completion(
    model="gemini/gemini-3.5-flash-lite",
    messages=[
        {"role": "user", "content": "Users name is vishal greet him and ask him how many projects he has completed till now"}
    ]
)

# 2. Extract and print the answer
reply = response.choices[0].message.content
print("\n🤖 AI Response:\n")
print(reply)