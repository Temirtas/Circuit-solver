import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.github.ai/inference"
)

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

image_base64 = encode_image("test_circuit.jpg")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
    "type": "text",
    "text": """This image shows a circuit diagram with a question. Analyze it and respond with ONLY a valid JSON object (no markdown, no code fences, no extra text before or after) in exactly this format:

{
  "components": "brief description of components and topology, e.g. 'R1=2ohm, R2=1ohm in series with 12V source'",
  "question": "the question being asked, e.g. 'Find current I2'",
  "final_answer": "the final numeric answer with units, e.g. '3.5 A'",
  "steps": "step-by-step explanation of the solution, using plain text, no LaTeX symbols"
}"""
},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ]
        }
    ]
)

import json

raw_output = response.choices[0].message.content
print("--- RAW OUTPUT ---")
print(raw_output)

try:
    result = json.loads(raw_output)
    print("\n--- PARSED SUCCESSFULLY ---")
    print("Components:", result["components"])
    print("Question:", result["question"])
    print("Final Answer:", result["final_answer"])
    print("Steps:", result["steps"])
except json.JSONDecodeError as e:
    print("\n--- JSON PARSING FAILED ---")
    print("Error:", e)