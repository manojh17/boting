# import threading
# import subprocess
# import time
# from flask import Flask, jsonify

# app = Flask(__name__)

# # -------------------- FLASK ROUTES --------------------
# @app.route('/')
# def home():
#     return "✅ Flask is running successfully. Bot will start soon!"

# @app.route('/status')
# def status():
#     return jsonify({"status": "Flask running", "bot": "Starting soon..."})

# # -------------------- RUN FLASK --------------------
# def run_flask():
#     """Run Flask server (blocking)."""
#     app.run(host='0.0.0.0', port=8080)

# # -------------------- RUN BOT --------------------
# def run_bot():
#     """Run the bb.py file once Flask is up."""
#     time.sleep(5)  # Wait for Flask to start fully
#     print("🚀 Starting Telegram bot (bbbot2.py)...")
#     subprocess.run(["python", "bbbot2.py"], check=True)

# # -------------------- MAIN --------------------
# if __name__ == "__main__":
#     # Start Flask in a separate thread (so main thread continues)
#     flask_thread = threading.Thread(target=run_flask)
#     flask_thread.start()

#     # Start bot AFTER Flask successfully launched
#     run_bot()

import threading
import subprocess
import time
import requests
from flask import Flask, jsonify
import os

app = Flask(__name__)

# -------------------- CONFIG --------------------
PORT = int(os.environ.get("PORT", 8080))
SELF_URL = f"https://boting-77os.onrender.com"  # Change to your deployed URL when hosted

# -------------------- FLASK ROUTES --------------------
@app.route('/')
def home():
    return "✅ Flask server is alive and the Telegram bot is running!"

@app.route('/status')
def status():
    return jsonify({"status": "Flask alive", "bot": "Running"})

# -------------------- KEEP ALIVE --------------------
def keep_alive():
    """Pings the app URL every few minutes to prevent sleep."""
    while True:
        try:
            time.sleep(300)  # every 5 minutes
            print(f"🌐 Pinging {SELF_URL} to keep alive...")
            requests.get(SELF_URL, timeout=10)
        except Exception as e:
            print(f"⚠️ Keep-alive ping failed: {e}")

# -------------------- RUN FLASK --------------------
def run_flask():
    """Run Flask web server."""
    app.run(host='0.0.0.0', port=PORT)

# -------------------- RUN BOT --------------------
def run_bot():
    """Run bb.py Telegram bot after Flask starts."""
    time.sleep(5)  # wait for Flask to start completely
    print("🤖 Starting Telegram bot (bb.py)...")
    subprocess.run(["python", "bbbot2.py"], check=True)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    # Start Flask first
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start keep-alive pinger
    keepalive_thread = threading.Thread(target=keep_alive, daemon=True)
    keepalive_thread.start()

    # Start bot after Flask is running
    run_bot()

