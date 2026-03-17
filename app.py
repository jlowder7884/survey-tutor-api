import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

SYSTEM_PROMPT = """
You are an AI tutor for a self-paced online course titled Introduction to Land Surveying.

Your role is to help students understand surveying concepts, vocabulary, history, and professional practices.

Rules:
- Help students understand surveying concepts clearly and patiently.
- Do NOT provide direct answers to quiz questions, test questions, or graded assignments.
- If a student asks for a direct answer to graded work, explain the concept, give a hint,
  provide a similar example, and ask a guiding question instead.
- Stay focused on land surveying, geospatial technology, and course topics.
- Be encouraging, professional, clear, and practical.
"""

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Land Surveying AI Tutor</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 900px;
      margin: 40px auto;
      padding: 0 16px;
      line-height: 1.5;
      background: #f7f9fc;
      color: #1f2937;
    }
    .card {
      background: white;
      border: 1px solid #d1d5db;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    h1 {
      margin-top: 0;
      color: #111827;
    }
    .note {
      background: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 12px 14px;
      margin-bottom: 20px;
      border-radius: 6px;
    }
    textarea {
      width: 100%;
      min-height: 120px;
      padding: 12px;
      font-size: 16px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      box-sizing: border-box;
      resize: vertical;
    }
    button {
      margin-top: 12px;
      padding: 10px 18px;
      font-size: 16px;
      border: none;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      cursor: pointer;
    }
    button:hover {
      background: #1d4ed8;
    }
    .response-box {
      margin-top: 24px;
      padding: 16px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      background: #f9fafb;
      white-space: pre-wrap;
    }
    .small {
      color: #6b7280;
      font-size: 14px;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Land Surveying AI Tutor</h1>

    <div class="note">
      This tutor can explain concepts, define terms, and help you study.
      It will not give direct answers to quizzes, tests, or graded assignments.
    </div>

    <form method="post" action="/ask">
      <label for="message"><strong>Ask a question:</strong></label>
      <textarea id="message" name="message" placeholder="Example: What is a boundary survey?">{{ message or "" }}</textarea>
      <br>
      <button type="submit">Ask Tutor</button>
    </form>

    <div class="small">
      Try asking: "What is a topographic survey?" or "Explain PLSS in simple terms."
    </div>

    {% if response %}
      <div class="response-box">
        <strong>Tutor Response:</strong>

{{ response }}
      </div>
    {% endif %}
  </div>
</body>
</html>
"""

def get_ai_response(message: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )
    return response.output_text

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML, response=None, message="")

@app.route("/ask", methods=["POST"])
def ask_form():
    message = request.form.get("message", "").strip()

    if not message:
        return render_template_string(
            HTML,
            response="Please enter a question.",
            message=""
        )

    try:
        answer = get_ai_response(message)
    except Exception as e:
        answer = f"Error contacting AI service: {str(e)}"

    return render_template_string(
        HTML,
        response=answer,
        message=message
    )

@app.route("/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Missing message"}), 400

    try:
        answer = get_ai_response(message)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
