from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import google.generativeai as genai

from config import Config
from database import DatabaseManager

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for session
app.config.from_object(Config)
CORS(app)

# Set database path
app.config['DATABASE_PATH'] = 'data/chat_history.db'

# Initialize database manager
db = DatabaseManager(app.config['DATABASE_PATH'])


# Chatbot logic using Gemini API
class HealthcareChatbot:
    def __init__(self):
        self.system_prompt = (
            "You are a professional healthcare assistant chatbot. Your role is to provide helpful, accurate, and safe health information while being empathetic and professional.\n\n"
            "Guidelines:\n"
            "- Provide general health information and guidance\n"
            "- Always recommend consulting healthcare professionals for specific medical concerns\n"
            "- Be empathetic and supportive in your responses\n"
            "- Use clear, easy-to-understand language\n"
            "- Never provide specific medical diagnoses\n"
            "- Focus on preventive care and wellness\n"
            "- If asked about emergencies, always recommend immediate medical attention\n\n"
            "Remember: You are an informational assistant, not a replacement for professional medical advice."
        )
        genai.configure(api_key=app.config['GEMINI_API_KEY'])
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-8b-latest")

    def get_response(self, user_message):
        try:
            prompt = f"{self.system_prompt}\nUser: {user_message}\nAssistant:"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I'm experiencing technical issues. Please try again later. (Error: {str(e)})"


chatbot = HealthcareChatbot()


@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')  # Make sure this file exists in the templates folder


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        session_id = session.get('session_id', str(uuid.uuid4()))

        bot_response = chatbot.get_response(user_message)

        db.save_message(session_id, user_message, bot_response)

        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/history', methods=['GET'])
def get_history():
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify([])
        history = db.get_chat_history(session_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': f'Error retrieving history: {str(e)}'}), 500


@app.route('/history', methods=['DELETE'])
def clear_history():
    try:
        session_id = session.get('session_id')
        if session_id:
            db.clear_history(session_id)
        return jsonify({'message': 'History cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Error clearing history: {str(e)}'}), 500


@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
