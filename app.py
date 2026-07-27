import os
import json
import base64
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.github.ai/inference"
)


def encode_image_bytes(file_bytes):
    return base64.b64encode(file_bytes).decode("utf-8")


def solve_circuit(image_base64):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """This image shows a circuit diagram with a question. Carefully analyze the circuit and ACTUALLY SOLVE it — perform the real calculation with actual numbers, not just a description of the method.

Respond with ONLY a valid JSON object (no markdown, no code fences, no extra text before or after) in exactly this format:

{
  "components": "brief description of components, their values, and topology",
  "question": "the exact question being asked",
  "steps": [
    {
      "title": "short title for this step, e.g. 'Combine series resistors'",
      "explanation": "one or two sentences explaining what is being done in this step, plain text, no LaTeX symbols",
      "highlights": ["key computed result(s) for this step as short strings, e.g. 'Rs = 4 Ω', 'I = 2.5 A'"]
    }
  ],
  "final_answer": "the final computed answer(s) with units and real numbers, e.g. '2.5 A', or a semicolon-separated list for multi-part answers"
}

Break the solution into as many logical steps as the problem actually needs (e.g. combine series resistors, combine parallel groups, find total current, find branch currents, find voltage drops, find power — mirror how a textbook worked solution presents it, one stage per step). Each step's "highlights" must contain the actual computed numeric result(s) from that step, not just the general formula. Never put vague descriptions in final_answer or highlights — always real, computed numbers."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ]
    )

    raw_output = response.choices[0].message.content

    # Strip markdown code fences if present (e.g. ```json ... ```)
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    result = json.loads(cleaned)

    # final_answer might be a string OR a nested object (for multi-part questions)
    # Flatten it into a readable string either way so the template always works
    if isinstance(result["final_answer"], dict):
        lines = []
        for key, value in result["final_answer"].items():
            if isinstance(value, dict):
                sub_lines = [f"{k.replace('_', ' ')}: {v}" for k, v in value.items()]
                lines.append(f"{key.replace('_', ' ')}: " + ", ".join(sub_lines))
            else:
                lines.append(f"{key.replace('_', ' ')}: {value}")
        result["final_answer"] = "; ".join(lines)

    # Safety net: if the model ignores instructions and returns steps as a plain string,
    # wrap it into the expected list-of-objects shape so the template doesn't break
    if isinstance(result.get("steps"), str):
        result["steps"] = [{"title": "Solution", "explanation": result["steps"], "highlights": []}]

    return result


@app.route("/")
def home():
    return render_template("index.html", result=None, error=None, image_data=None)


@app.route("/solve", methods=["POST"])
def solve():
    # Case 1: no file selected at all
    if "image" not in request.files or request.files["image"].filename == "":
        return render_template("index.html", result=None, error="Please choose an image file before clicking Solve.", image_data=None)

    uploaded_file = request.files["image"]

    # Case 2: check it's actually an image by file extension
    allowed_extensions = (".jpg", ".jpeg", ".png", ".webp")
    if not uploaded_file.filename.lower().endswith(allowed_extensions):
        return render_template("index.html", result=None, error="That file doesn't look like an image. Please upload a JPG, PNG, or WEBP.", image_data=None)

    file_bytes = uploaded_file.read()

    # Case 3: check file isn't empty or absurdly large (limit ~10MB)
    if len(file_bytes) == 0:
        return render_template("index.html", result=None, error="The uploaded file appears to be empty. Please try again.", image_data=None)
    if len(file_bytes) > 10 * 1024 * 1024:
        return render_template("index.html", result=None, error="That image is too large. Please upload something under 10MB.", image_data=None)

    image_base64 = encode_image_bytes(file_bytes)
    image_data_uri = f"data:image/jpeg;base64,{image_base64}"

    # Case 4: the API call itself might fail (network, rate limit, bad token, malformed JSON, etc.)
    try:
        result = solve_circuit(image_base64)
    except json.JSONDecodeError:
        return render_template("index.html", result=None, error="The AI returned an unexpected response. Please try again — sometimes this happens on complex or unclear images.", image_data=None)
    except Exception as e:
        return render_template("index.html", result=None, error=f"Something went wrong while contacting the AI service: {str(e)}", image_data=None)

    return render_template("index.html", result=result, error=None, image_data=image_data_uri)


if __name__ == "__main__":
    app.run(debug=True)