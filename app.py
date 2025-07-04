from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Set to frontend domain in production

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory user store (for testing only)
users = {}

@app.route("/")
def home():
    return "AI Finance Assistant Backend is running!"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    users[username] = password
    return jsonify({"message": "Signup successful"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if users.get(username) == password:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

def generate_response(message):
    prompt = f"""
You are a helpful and knowledgeable AI finance assistant.
Provide personalized budgeting advice and money-saving tips when the user asks finance-related questions.

User: {message}
Assistant:"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify(reply="Please enter a valid message."), 400

    response = generate_response(user_msg)
    return jsonify(reply=response)

if __name__ == "__main__":
    app.run(debug=True)
