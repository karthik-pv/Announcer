from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, disconnect, emit
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

VALID_PASSWORD = os.getenv("SOCKET_PASSWORD")
authenticated_clients = set()  # Set of session IDs that passed auth


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    password = data.get("password", "")
    if password == VALID_PASSWORD:
        token = str(uuid.uuid4())  # simple random token
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False, "error": "Invalid password"}), 401


@socketio.on("connect")
def handle_connect():
    print("Client connected:", request.sid)


@socketio.on("register_token")
def handle_register_token(data):
    token = data.get("token")
    # Simple validation: just accept any non-empty token
    # In production, you'd validate token from a database/session store
    if token:
        print(f"Registered authenticated client: {request.sid}")
        authenticated_clients.add(request.sid)
    else:
        print(f"Client {request.sid} did not provide valid token. Disconnecting.")
        disconnect()


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected:", request.sid)
    authenticated_clients.discard(request.sid)


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    data = request.data.decode("utf-8").strip()
    print("Webhook received:", data)
    # Only send to authenticated clients
    for sid in authenticated_clients:
        socketio.emit("new_alert", {"message": data}, to=sid)
    return {"res": "success"}


if __name__ == "__main__":
    socketio.run(app, debug=True)
