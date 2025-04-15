# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# from functools import wraps
# import logging
# from typing import Dict, Any, Union

# # Load .env file
# load_dotenv(dotenv_path=".env")

# app = Flask(__name__)
# CORS(app)  # Allow frontend to communicate with backend

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Fetch API key from environment
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     logger.error("❌ Google Gemini API key is missing! Set it in the .env file.")
#     raise ValueError("Google Gemini API key is missing!")

# # Configure Google Gemini AI client
# genai.configure(api_key=GEMINI_API_KEY)


# # Error handling decorator
# def handle_errors(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         try:
#             return f(*args, **kwargs)
#         except Exception as e:
#             logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
#             return jsonify({"error": "An unexpected error occurred"}), 500

#     return wrapper


# @app.route('/chat', methods=['POST'])
# @handle_errors
# def chat():
#     """Handles AI chatbot responses using Google Gemini AI API for allergy-related queries."""
#     data: Dict[str, Any] = request.get_json()
#     if not data or "message" not in data:
#         return jsonify({"error": "Missing message parameter"}), 400

#     user_message: str = data.get("message", "").strip()

#     if not user_message:
#         return jsonify({"error": "Message cannot be empty"}), 400

#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash")  # Replace with the correct model name if needed
#         response = model.generate_content(
#             f"You are a helpful assistant specializing in allergy information. Provide to the point, friendly, and concise answers to the user's questions about food allergies and their symptoms.The response should be in bullet points only and answer should be short. User query: {user_message}"
#         )

#         if not response or not hasattr(response, "candidates") or not response.candidates:
#             logger.error("Invalid response structure from Gemini API")
#             return jsonify({"response": "I couldn't generate a response. Please try again."}), 500

#         ai_response = response.candidates[0].content.parts[0].text
#         return jsonify({"response": ai_response})

#     except Exception as e:
#         logger.error(f"Gemini API error: {str(e)}")
#         return jsonify({"response": "I'm having trouble responding right now. Please try again later."}), 500


# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint for monitoring"""
#     return jsonify({"status": "healthy", "service": "allergy-assistant"})


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")




from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from functools import wraps
import logging
from typing import Dict, Any, List

# Load .env file
load_dotenv(dotenv_path=".env")

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.error("❌ Google Gemini API key is missing! Set it in the .env file.")
    raise ValueError("Google Gemini API key is missing!")

# Configure Google Gemini AI client
genai.configure(api_key=GEMINI_API_KEY)


# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred"}), 500
    return wrapper


@app.route('/chat', methods=['POST'])
@handle_errors
def chat():
    """
    Handles AI chatbot responses using Google Gemini AI API for allergy-related queries,
    with support for conversation history.
    """
    data: Dict[str, Any] = request.get_json()
    user_message: str = data.get("message", "").strip()
    history: List[Dict[str, str]] = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    model = genai.GenerativeModel("gemini-1.5-flash")

    # Prepare chat history
    chat_history = [{"role": "user" if h["sender"] == "user" else "model", "parts": [h["message"]]} for h in history]
    chat_history.append({"role": "user", "parts": [user_message]})

    try:
        response = model.generate_content(
            chat_history + [{"role": "user", "parts": ["You are a helpful assistant specializing in allergy information. Provide to the point, friendly, and concise answers to the user's questions about food allergies and their symptoms.The response should be in bullet points only and answer should be short."]}],
            generation_config={
                "temperature": 0.5,
                "max_output_tokens": 150,  # limit the length of response
                "top_p": 0.9,
                "top_k": 20
            }
        )

        if not response or not hasattr(response, "candidates") or not response.candidates:
            logger.error("Invalid response structure from Gemini API")
            return jsonify({"response": "I couldn't generate a response. Please try again."}), 500

        ai_response = response.candidates[0].content.parts[0].text
        return jsonify({"response": ai_response})

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return jsonify({"response": "I'm having trouble responding right now. Please try again later."}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "service": "allergy-assistant"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
