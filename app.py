"""
app.py
Digital Didi - Multilingual AI Voice & Visual Guide for Rural First-Time Women Users
Accessing Pradhan Mantri Ujjwala Yojana 2.0 with Zero Prior Tech Literacy.
Supports 11 major Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi,
Gujarati, Kannada, Malayalam, Punjabi, Odia, and English).
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

from scheme_data import (
    get_scheme_data,
    get_walkthrough,
    get_languages,
    get_step,
    get_all_steps,
    check_eligibility,
    PMUY_SCHEME_FACTS
)
from gemini_client import default_gemini_client, translate_step, answer_question

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    """Renders the main multilingual voice & visual navigation interface."""
    lang = request.args.get("lang", "hi")
    scheme = get_scheme_data(lang=lang)
    languages = get_languages()
    return render_template("index.html", scheme=scheme, languages=languages, current_lang=lang)

@app.route("/api/languages", methods=["GET"])
def api_languages():
    """Returns the list of 11 supported Indian languages."""
    return jsonify({
        "status": "success",
        "languages": get_languages()
    })

@app.route("/api/scheme", methods=["GET"])
def api_scheme():
    """Returns localized scheme metadata and requirements."""
    lang = request.args.get("lang", "hi")
    return jsonify(get_scheme_data(lang=lang))

@app.route("/api/steps", methods=["GET"])
def api_steps():
    """Returns the 5 official PMUY application steps in the requested language."""
    lang = request.args.get("lang", "hi")
    return jsonify({
        "status": "success",
        "lang": lang,
        "steps": get_all_steps(lang=lang)
    })

@app.route("/api/walkthrough", methods=["GET"])
def api_walkthrough():
    """Returns the step-by-step 1-click sample walkthrough in the requested language."""
    lang = request.args.get("lang", "hi")
    return jsonify({
        "status": "success",
        "lang": lang,
        "steps": get_walkthrough(lang=lang)
    })

@app.route("/api/step/<int:step_num>", methods=["GET"])
@app.route("/api/step", methods=["GET", "POST"])
def api_step(step_num=None):
    """
    Returns official PMUY step guidance in English and translated into target language
    using pre-translated authoritative steps with translate_step() fallback.
    """
    if step_num is None:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            step_num = int(data.get("step_number", data.get("step", 1)))
            lang = data.get("lang", "en")
        else:
            step_num = int(request.args.get("step_number", request.args.get("step", 1)))
            lang = request.args.get("lang", "en")
    else:
        lang = request.args.get("lang", "en")

    english_step = get_step(step_num, "en")
    if lang == "en":
        translated_step = english_step
    else:
        # 1. First retrieve authoritative native step guidance (guarantees no English fallback)
        localized_step = get_step(step_num, lang)
        if localized_step and not localized_step.startswith("Invalid step number") and localized_step != english_step:
            translated_step = localized_step
        else:
            # 2. Dynamic Gemini translation fallback
            translated_step = translate_step(english_step, lang)

    return jsonify({
        "status": "success",
        "step_number": step_num,
        "english_text": english_step,
        "translated_text": translated_step,
        "lang": lang
    })

@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    Translates provided English scheme text into any supported Indian language
    using translate_step() with safe fallback.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    lang = data.get("lang", "hi")
    if not text:
        return jsonify({"status": "error", "message": "Text parameter is required"}), 400

    translated = translate_step(text, lang)
    return jsonify({
        "status": "success",
        "original_text": text,
        "translated_text": translated,
        "lang": lang
    })

@app.route("/api/ask", methods=["POST"])
def api_ask():
    """
    Answers user questions strictly grounded in PMUY scheme facts using Gemini,
    with safe fallback and polite out-of-scope redirection.
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", data.get("query", "")).strip()
    lang = data.get("lang", "hi")
    facts = data.get("facts", PMUY_SCHEME_FACTS)

    answer = answer_question(facts, question, lang)
    return jsonify({
        "status": "success",
        "question": question,
        "answer": answer,
        "lang": lang
    })

@app.route("/api/eligibility", methods=["POST"])
def api_eligibility():
    """
    Evaluates applicant eligibility based on answers to criteria questions.
    """
    data = request.get_json(silent=True) or {}
    result = check_eligibility(data)
    return jsonify({
        "status": "success",
        "eligibility": result
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Receives voice transcript or quick-option tap from user.
    Uses Gemini to generate sisterly guidance in the selected language.
    """
    data = request.get_json(silent=True) or {}
    user_query = data.get("query", "").strip()
    current_stage = data.get("stage", "welcome")
    lang = data.get("lang", "hi")

    response_data = default_gemini_client.ask(
        user_query=user_query,
        current_stage=current_stage,
        lang=lang
    )
    return jsonify({
        "status": "success",
        "data": response_data
    })

@app.route("/health", methods=["GET"])
def health():
    """Standard health check endpoint for cloud monitoring."""
    return jsonify({
        "status": "ok",
        "app": "digital-didi",
        "model": "gemini-3.8-flash",
        "languages_supported": 11
    })

if __name__ == "__main__":
    # Read the PORT strictly from environment variable PORT, defaulting to 5000
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    logger.info("Starting Digital Didi on port %d...", port)
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
