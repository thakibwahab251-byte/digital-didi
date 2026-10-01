"""
gemini_client.py
Multilingual Interface to Google Gemini API using google-genai SDK.
Configured with the persona of 'Digital Didi' (डिजिटल दीदी) — a compassionate
rural elder sister who speaks 11 Indian languages.
Includes translate_step() and answer_question() with safe English fallback.
"""

import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

LANGUAGE_MAP = {
    "hi": "Hindi (हिन्दी)",
    "hindi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "tamil": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "telugu": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "bengali": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "marathi": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "gujarati": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "kannada": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "malayalam": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "punjabi": "Punjabi (ਪੰਜਾਬੀ)",
    "or": "Odia (ଓଡ଼ିଆ)",
    "odia": "Odia (ଓଡ଼ିଆ)",
    "oriya": "Odia (ଓଡ଼ିଆ)",
    "en": "English",
    "english": "English"
}

MODEL_NAME = "gemini-3.8-flash"


def _get_genai_client():
    """Helper to initialize and return Google GenAI client if API key is present."""
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("Gemini_API_Key")
        or os.getenv("GOOGLE_API_KEY")
    )
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.warning("Could not initialize google-genai Client: %s", e)
        return None


def _resolve_language_name(target_language):
    """Normalizes language code or name to standard Indic name."""
    if not target_language:
        return "Hindi (हिन्दी)"
    normalized = target_language.strip().lower()
    return LANGUAGE_MAP.get(normalized, target_language)


def _format_facts_to_string(english_facts):
    """Formats English facts (dict or str) into clean bullet points for Gemini."""
    if isinstance(english_facts, str):
        return english_facts
    if not isinstance(english_facts, dict):
        return str(english_facts or "")

    parts = []
    if "official_name" in english_facts:
        parts.append(f"Scheme Name: {english_facts['official_name']}")
    if "target_beneficiary" in english_facts:
        parts.append(f"Beneficiary: {english_facts['target_beneficiary']}")
    if "benefits" in english_facts:
        b_list = [f"- {b.get('title')}: {b.get('description')} ({b.get('cost_to_beneficiary')})" for b in english_facts["benefits"]]
        parts.append("Benefits:\n" + "\n".join(b_list))
    if "eligibility_criteria" in english_facts:
        e_list = [f"- {c.get('rule')}" for c in english_facts["eligibility_criteria"]]
        parts.append("Eligibility:\n" + "\n".join(e_list))
    if "required_documents" in english_facts:
        d_list = [f"- {d.get('name')}: {d.get('purpose')}" for d in english_facts["required_documents"]]
        parts.append("Required Documents:\n" + "\n".join(d_list))
    if "application_steps" in english_facts:
        s_list = [f"- Step {s.get('step_number')}: {s.get('spoken_text')}" for s in english_facts["application_steps"]]
        parts.append("Application Steps:\n" + "\n".join(s_list))
    if "official_helpline" in english_facts:
        parts.append(f"Toll-Free Helpline: {english_facts['official_helpline']}")
    if "emergency_leak_helpline" in english_facts:
        parts.append(f"Emergency Gas Leak Helpline: {english_facts['emergency_leak_helpline']}")
    if "official_website" in english_facts:
        parts.append(f"Official Website: {english_facts['official_website']}")

    return "\n\n".join(parts)


def translate_step(english_text, target_language):
    """
    Asks Gemini to translate the given English step text into the target Indian
    language (e.g. Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada,
    Malayalam, Punjabi, Odia) in a simple, spoken-friendly style suitable for
    someone who cannot read well.

    If the API key is missing or any call fails, falls back to returning the original
    English text so the application never crashes.

    Args:
        english_text (str): The English step guidance text to translate.
        target_language (str): The target Indian language name or code.

    Returns:
        str: Spoken-friendly translation in target_language, or english_text on fallback.
    """
    if not english_text:
        return ""

    lang_resolved = _resolve_language_name(target_language)
    if lang_resolved.lower() in ("english", "en"):
        return english_text

    client = _get_genai_client()
    if not client:
        logger.info("No Gemini API client available. Falling back to original English text for translate_step.")
        return english_text

    prompt = f"""You are translating instructions for a first-time rural woman user in India who cannot read well.
Translate the following English scheme step text into spoken, natural, colloquial {lang_resolved}.
Keep it warm, simple, short, and very easy to understand when spoken aloud. Do not use bureaucratic or complex literary words.

English Text:
"{english_text}"

Spoken-friendly translation in {lang_resolved} (only the translated text):"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        if response and response.text:
            cleaned = response.text.strip()
            if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) > 2:
                cleaned = cleaned[1:-1].strip()
            return cleaned
        return english_text
    except Exception as err:
        logger.error("Gemini translate_step error: %s. Falling back to original English text.", err)
        return english_text


def answer_question(english_facts, question, target_language):
    """
    Answers free-form questions about the PMUY scheme using Gemini.
    Sends Gemini the English facts plus the user's question (which may be in any
    Indian language or simple broken English), asking for a very short, simple
    spoken-style answer (2-3 short sentences, no jargon) in the target_language,
    using ONLY those facts — never inventing information.

    If the question is unrelated to this scheme or inappropriate, replies politely
    in the target_language and redirects to the guided steps instead of guessing.

    If the API key is missing or any call fails, falls back to returning the original
    English text / safe English guidance so the application never crashes.

    Args:
        english_facts (dict or str): The official English PMUY facts (single source of truth).
        question (str): The user's question (in any language or broken English).
        target_language (str): The target language name or code to reply in.

    Returns:
        str: Spoken-style answer in target_language, or English text fallback on failure.
    """
    default_fallback_text = (
        "Pradhan Mantri Ujjwala Yojana 2.0 provides a free LPG connection, two-burner stove, "
        "and first refill cylinder to eligible women from poor households. "
        "You need an Aadhaar card, ration card, and bank passbook. Please follow the guided steps."
    )
    fallback_text = (
        english_facts.strip() if isinstance(english_facts, str) and english_facts.strip()
        else default_fallback_text
    )

    if not question or not str(question).strip():
        return fallback_text

    lang_resolved = _resolve_language_name(target_language)
    facts_str = _format_facts_to_string(english_facts)

    client = _get_genai_client()
    if not client:
        logger.info("No Gemini API client available. Returning English fallback for answer_question.")
        return fallback_text

    prompt = f"""You are "Digital Didi", a warm, patient, and respectful elder sister helping an illiterate rural woman in India.
Answer the user's question using ONLY the following verified English scheme facts.

VERIFIED ENGLISH SCHEME FACTS:
\"\"\"
{facts_str}
\"\"\"

USER'S QUESTION (may be in any Indian language or broken English):
"{question.strip()}"

INSTRUCTIONS:
1. Target Language: Answer strictly in {lang_resolved}.
2. Tone & Length: Spoken, warm, very simple style (exactly 2 to 3 short sentences, no bureaucratic jargon).
3. Strict Grounding: Use ONLY the verified facts above. NEVER invent or assume any information.
4. Out-of-Scope Guardrail: If the question is unrelated to Pradhan Mantri Ujjwala Yojana (PMUY / free gas connection) or inappropriate, do NOT guess. Politely say in {lang_resolved} that you can only help with the free gas connection scheme, and invite them to follow the guided steps.
5. Return ONLY the spoken answer text with no prefixes or meta-commentary.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        if response and response.text:
            cleaned = response.text.strip()
            if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) > 2:
                cleaned = cleaned[1:-1].strip()
            return cleaned
        return fallback_text
        except Exception as err:
        print("=" * 60)
        print("GEMINI ERROR DETAILS:")
        print(f"Error type: {type(err).__name__}")
        print(f"Error message: {err}")
        print("=" * 60)
        logger.error("Gemini answer_question error: %s. Falling back to English text.", err)
        return fallback_text

# ==============================================================================
# EXISTING BACKWARD-COMPATIBLE CLASS & METHODS
# ==============================================================================

_SENTINEL = object()


class GeminiClient:
    def __init__(self, api_key=_SENTINEL):
        if api_key is _SENTINEL:
            self.api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("Gemini_API_Key")
                or os.getenv("GOOGLE_API_KEY")
            )
        else:
            self.api_key = api_key

        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Google GenAI client successfully initialized with model: %s", MODEL_NAME)
            except Exception as e:
                logger.warning("Could not initialize Google GenAI client: %s. Using fallback mode.", e)
                self.client = None
        else:
            logger.info("No Gemini API key detected. Running in reliable offline fallback mode.")

    def ask(self, user_query, current_stage="welcome", lang="hi"):
        """
        Sends the user's speech query to Gemini or processes it via fallback.
        Accepts language code ('hi', 'ta', 'te', 'bn', etc.).
        """
        from scheme_data import TRANSLATIONS, PMUY_SCHEME_FACTS
        user_query_clean = (user_query or "").strip()
        target_lang = lang if lang in TRANSLATIONS else "hi"
        lang_name = LANGUAGE_MAP.get(target_lang, "Hindi")

        if self.client and user_query_clean:
            try:
                # Use answer_question logic with grounded facts
                reply = answer_question(PMUY_SCHEME_FACTS, user_query_clean, target_lang)
                intent = self._detect_intent(user_query_clean)
                return {
                    "reply_text": reply,
                    "audio_text": reply,
                    "detected_intent": intent,
                    "suggested_stage": self._map_intent_to_stage(intent),
                    "lang": target_lang,
                    "is_ai_generated": True
                }
            except Exception as e:
                logger.error("Gemini API error during ask(): %s. Reverting to fallback.", e)

        return self._fallback_reply(user_query_clean, current_stage, target_lang)

    def _detect_intent(self, text):
        text_lower = text.lower()
        if any(w in text_lower for w in ["कागज़", "दस्तावेज़", "आधार", "राशन", "document", "paper", "ஆவணம்", "పత్రాలు", "কাগজ", "कागदपत्रੇ"]):
            return "documents"
        elif any(w in text_lower for w in ["पैसा", "रुपया", "फीस", "मुफ्त", "free", "cost", "money", "விலை", "డబ్బు", "টাকা", "पैसे", "રૂપિયા"]):
            return "cost"
        elif any(w in text_lower for w in ["कहाँ", "कहा जाना", "एजेंसी", "where", "agency", "எங்கு", "ఎక్కడ", "কোথায়", "कुठे", "ક્યાં"]):
            return "where_to_go"
        elif any(w in text_lower for w in ["हाँ", "मिल जाएगा", "yes", "eligible", "ஆம்", "అవును", "হ্যাঁ", "होय"]):
            return "eligibility"
        return "general"

    def _map_intent_to_stage(self, intent):
        mapping = {
            "documents": "documents",
            "cost": "benefits",
            "where_to_go": "where_to_go",
            "eligibility": "documents"
        }
        return mapping.get(intent, "welcome")

    def _fallback_reply(self, user_query, current_stage, lang):
        from scheme_data import TRANSLATIONS
        t = TRANSLATIONS.get(lang, TRANSLATIONS["hi"])
        intent = self._detect_intent(user_query)

        if intent == "documents" or current_stage == "documents":
            reply = f"{t['doc_aadhaar_audio']} {t['doc_ration_audio']} {t['doc_passbook_audio']}"
            suggested = "documents"
        elif intent == "cost":
            reply = t["safety_alert"]
            suggested = "welcome"
        elif intent == "where_to_go" or current_stage == "where_to_go":
            reply = f"{t['where_agency_desc']} {t['where_csc_desc']}"
            suggested = "where_to_go"
        elif intent == "eligibility" or current_stage == "question_ration":
            reply = f"{t['congrats_title']}! {t['congrats_desc']}"
            suggested = "documents"
        else:
            reply = t["didi_greeting"]
            suggested = "welcome"

        return {
            "reply_text": reply,
            "audio_text": reply,
            "detected_intent": intent,
            "suggested_stage": suggested,
            "lang": lang,
            "is_ai_generated": False
        }


# Global singleton client instance
default_gemini_client = GeminiClient()
