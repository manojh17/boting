import threading
import subprocess
import time
from flask import Flask, jsonify

app = Flask(__name__)

# -------------------- FLASK ROUTES --------------------
@app.route('/')
def home():
    return "✅ Flask is running successfully. Bot will start soon!"

@app.route('/status')
def status():
    return jsonify({"status": "Flask running", "bot": "Starting soon..."})

# -------------------- RUN FLASK --------------------
def run_flask():
    """Run Flask server (blocking)."""
    app.run(host='0.0.0.0', port=8080)

# -------------------- RUN BOT --------------------
def run_bot():
    """Run the bb.py file once Flask is up."""
    time.sleep(5)  # Wait for Flask to start fully
    print("🚀 Starting Telegram bot (bbbot2.py)...")
    subprocess.run(["python", "bbbot2.py"], check=True)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    # Start Flask in a separate thread (so main thread continues)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start bot AFTER Flask successfully launched
    run_bot()
