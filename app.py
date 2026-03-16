import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI tutor for an Introduction to Land Surveying course.

Rules:
- Help students understand surveying concepts.
- Do NOT give direct answers to quiz or test questions.
- Instead explain the concept and guide the student.
"""

@app.route("/")
def home():
    return "Survey Tutor API Running"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    return jsonify({"response": response.output_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
