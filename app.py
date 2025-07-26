from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import jwt
import datetime
from functools import wraps

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app)
openai.api_key = os.getenv("OPENAI_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET") or "my-secret"  # Make sure to set in your .env

# Dummy user store (replace with DB in production)
users = {
    "Godwin": {
        "password": "admin123",
        "is_admin": True
    }
}

# JWT authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 403
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded
        except Exception:
            return jsonify({"message": "Token is invalid"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return jsonify(message="✅ AI Finance Assistant Backend is running!")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify(error="Username and password required."), 400
    if username in users:
        return jsonify(error="User already exists."), 400

    users[username] = {"password": password, "is_admin": False}

    token = jwt.encode({
        "username": username,
        "role": "user",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify(message="Signup successful", token=token, is_admin=False), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = users.get(username)
    if user and user["password"] == password:
        token = jwt.encode({
            "username": username,
            "role": "admin" if user["is_admin"] else "user",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, JWT_SECRET, algorithm="HS256")

        return jsonify(message="Login successful", token=token, is_admin=user["is_admin"])

    return jsonify(error="Invalid credentials"), 401

@app.route("/admin/data", methods=["GET"])
@token_required
def admin_data():
    if request.user["role"] != "admin":
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify(message="👑 Welcome to the Admin Dashboard!")

@app.route("/user/profile", methods=["GET"])
@token_required
def user_profile():
    return jsonify(username=request.user["username"], is_admin=(request.user["role"] == "admin"))

@app.route("/transactions", methods=["GET"])
@token_required
def get_transactions():
    return jsonify([
        {"date": "2025-07-10", "amount": 5000},
        {"date": "2025-07-11", "amount": 2500},
        {"date": "2025-07-12", "amount": 7000}
    ])

@app.route("/insights", methods=["GET"])
@token_required
def get_insights():
    return jsonify({
        "prediction": "You may exceed your weekly budget by ₦5,000."
    })

@app.route("/chat", methods=["POST"])
@token_required
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify(reply="Please enter a valid message."), 400

    ai_reply = generate_response(message)
    return jsonify(reply=ai_reply), 200

# OpenAI response generator
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
