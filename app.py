from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# Load environment variables from .env
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Change to specific origin in production

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Temporary in-memory user store (NOT for production)
users = {}

@app.route("/")
def index():
    return jsonify(message="✅ AI Finance Assistant Backend is running!")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify(error="Username and password are required."), 400

    if username in users:
        return jsonify(error="User already exists."), 400

    users[username] = password
    return jsonify(message="Signup successful."), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify(error="Username and password are required."), 400

    if users.get(username) != password:
        return jsonify(error="Invalid credentials."), 401

    return jsonify(message="Login successful."), 200

def generate_response(message):
    """
    Calls OpenAI to generate a finance assistant response.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and knowledgeable AI finance assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify(reply="Please enter a valid message."), 400

    ai_reply = generate_response(message)
    return jsonify(reply=ai_reply), 200

if __name__ == "__main__":
    app.run(debug=True)
