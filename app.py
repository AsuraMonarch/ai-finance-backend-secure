from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import uuid  # to create dummy tokens

# Define your admin user
ADMIN_USERNAME = "Godwin"

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

openai.api_key = os.getenv("OPENAI_API_KEY")

# Updated user store
users = {
    "Godwin": {
        "password": "admin123",
        "is_admin": True
    }
}
sessions = {}  # token -> username

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

    users[username] = {"password": password, "is_admin": False}

    token = str(uuid.uuid4())
    sessions[token] = username

    return jsonify(message="Signup successful.", token=token, is_admin=False), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify(error="Username and password are required."), 400

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify(error="Invalid credentials."), 401

    token = str(uuid.uuid4())
    sessions[token] = username

    return jsonify(message="Login successful.", token=token, is_admin=user["is_admin"]), 200

@app.route("/user/profile", methods=["GET"])
def user_profile():
    token = request.headers.get("Authorization")
    username = sessions.get(token)

    if not username:
        return jsonify(error="Unauthorized"), 401

    user = users.get(username)
    return jsonify(username=username, is_admin=user["is_admin"])

@app.route("/admin/data", methods=["GET"])
def admin_data():
    token = request.headers.get("Authorization")
    username = sessions.get(token)

    if not username:
        return jsonify(error="Unauthorized"), 401

    user = users.get(username)
    if not user.get("is_admin"):
        return jsonify(error="Access denied"), 403

    return jsonify(message="👑 Welcome to the Admin Dashboard!")

@app.route("/transactions", methods=["GET"])
def get_transactions():
    return jsonify([
        {"date": "2025-07-10", "amount": 5000},
        {"date": "2025-07-11", "amount": 2500},
        {"date": "2025-07-12", "amount": 7000}
    ])

@app.route("/insights", methods=["GET"])
def get_insights():
    return jsonify({
        "prediction": "You may exceed your weekly budget by ₦5,000."
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify(reply="Please enter a valid message."), 400

    ai_reply = generate_response(message)
    return jsonify(reply=ai_reply), 200

def generate_response(message):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI finance assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
