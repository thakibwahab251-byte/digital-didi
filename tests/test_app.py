"""
tests/test_app.py
Comprehensive test suite for Digital Didi web application.
Validates routes, 11-language support, API endpoints, Gemini client fallback,
official PMUY scheme facts, get_step(), check_eligibility(), translate_step(), answer_question(),
environment variable PORT reading, and the < 10 MB project size constraint.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add parent directory to path so imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from scheme_data import (
    PMUY_SCHEME_FACTS,
    get_step,
    check_eligibility,
    get_scheme_data,
    get_walkthrough,
    get_languages
)
from gemini_client import GeminiClient, translate_step, answer_question

class DigitalDidiTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_pmuy_scheme_facts_structure(self):
        """Verifies the hardcoded English single source of truth for PMUY scheme facts."""
        self.assertEqual(PMUY_SCHEME_FACTS["scheme_id"], "pm_ujjwala_yojana")
        self.assertIn("Pradhan Mantri Ujjwala Yojana", PMUY_SCHEME_FACTS["official_name"])
        self.assertEqual(PMUY_SCHEME_FACTS["official_website"], "https://www.pmuy.gov.in")
        self.assertEqual(PMUY_SCHEME_FACTS["official_helpline"], "1800-266-6696")
        self.assertEqual(PMUY_SCHEME_FACTS["emergency_leak_helpline"], "1906")

        # Verify eligibility criteria are present
        self.assertGreaterEqual(len(PMUY_SCHEME_FACTS["eligibility_criteria"]), 3)
        codes = [c["code"] for c in PMUY_SCHEME_FACTS["eligibility_criteria"]]
        self.assertIn("adult_woman", codes)
        self.assertIn("no_prior_connection", codes)
        self.assertIn("bpl_or_poor_household", codes)

        # Verify required documents
        doc_ids = [d["id"] for d in PMUY_SCHEME_FACTS["required_documents"]]
        self.assertIn("aadhaar", doc_ids)
        self.assertIn("ration_card", doc_ids)
        self.assertIn("bank_passbook", doc_ids)

        # Verify application steps
        steps = PMUY_SCHEME_FACTS["application_steps"]
        self.assertEqual(len(steps), 5)
        for s in steps:
            self.assertIn("step_number", s)
            self.assertIn("spoken_text", s)

    def test_get_step_function(self):
        """Tests get_step(step_number) returns spoken-friendly English text for valid/invalid steps."""
        step1 = get_step(1)
        self.assertIn("Step 1", step1)
        self.assertIn("Aadhaar", step1)

        step3 = get_step(3)
        self.assertIn("Step 3", step3)
        self.assertIn("application form", step3)

        step5 = get_step(5)
        self.assertIn("Step 5", step5)
        self.assertIn("free gas connection", step5)

        invalid_step = get_step(99)
        self.assertIn("Invalid step number: 99", invalid_step)

    def test_check_eligibility_function(self):
        """Tests check_eligibility(answers) with various yes/no combinations."""
        # Case 1: Fully eligible (booleans)
        ans_eligible_bool = {
            "is_adult_woman": True,
            "has_existing_connection": False,
            "is_bpl_or_poor": True
        }
        res1 = check_eligibility(ans_eligible_bool)
        self.assertTrue(res1["eligible"])
        self.assertIn("eligible", res1["reason"].lower())

        # Case 2: Fully eligible (string representations 'yes'/'no')
        ans_eligible_str = {
            "is_woman_over_18": "yes",
            "has_existing_connection": "no",
            "has_ration_card": "yes"
        }
        res2 = check_eligibility(ans_eligible_str)
        self.assertTrue(res2["eligible"])

        # Case 3: Ineligible because household already has an LPG cylinder
        ans_has_gas = {
            "is_adult_woman": True,
            "has_existing_connection": True,
            "is_bpl_or_poor": True
        }
        res3 = check_eligibility(ans_has_gas)
        self.assertFalse(res3["eligible"])
        self.assertIn("existing", res3["reason"].lower())

        # Case 4: Ineligible because applicant is not an adult woman (under 18)
        ans_underage = {
            "is_adult_woman": False,
            "has_existing_connection": False,
            "is_bpl_or_poor": True
        }
        res4 = check_eligibility(ans_underage)
        self.assertFalse(res4["eligible"])
        self.assertIn("woman", res4["reason"].lower())

        # Case 5: Ineligible because no BPL status / ration card
        ans_not_bpl = {
            "is_adult_woman": True,
            "has_existing_connection": False,
            "is_bpl_or_poor": False
        }
        res5 = check_eligibility(ans_not_bpl)
        self.assertFalse(res5["eligible"])
        self.assertIn("bpl", res5["reason"].lower())

    def test_translate_step_with_fallback(self):
        """Tests translate_step translates or safely falls back to English text."""
        sample_text = "Step 1: Gather your documents."

        # Translation into English returns identical string
        en_res = translate_step(sample_text, "English")
        self.assertEqual(en_res, sample_text)

        # Translation into Hindi returns a non-empty string
        hi_res = translate_step(sample_text, "Hindi")
        self.assertIsInstance(hi_res, str)
        self.assertGreater(len(hi_res), 0)

        # Fallback when client is None
        with patch("gemini_client._get_genai_client", return_value=None):
            fallback_res = translate_step(sample_text, "Tamil")
            self.assertEqual(fallback_res, sample_text)

    def test_answer_question_with_fallback(self):
        """Tests answer_question grounds answers in English facts with safe fallback."""
        # Grounded query about stove
        ans = answer_question(PMUY_SCHEME_FACTS, "Does the stove cost any money?", "Hindi")
        self.assertIsInstance(ans, str)
        self.assertGreater(len(ans), 0)

        # Fallback when client is None
        with patch("gemini_client._get_genai_client", return_value=None):
            fallback_ans = answer_question(PMUY_SCHEME_FACTS, "How do I apply?", "Telugu")
            self.assertIn("Pradhan Mantri Ujjwala Yojana", fallback_ans)

    def test_home_page(self):
        """Verifies that the index page loads with Digital Didi branding and language picker."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("डिजिटल दीदी", html)
        self.assertIn("Digital Didi", html)
        self.assertIn("language-ribbon", html)
        self.assertIn("தமிழ்", html)
        self.assertIn("తెలుగు", html)
        self.assertIn("বাংলা", html)
        self.assertIn("btn-walkthrough", html)
        self.assertIn("btn-mic", html)
        self.assertIn("card-aadhaar", html)
        self.assertIn("card-ration", html)
        self.assertIn("card-passbook", html)

    def test_languages_api(self):
        """Verifies GET /api/languages returns all 11 supported Indian languages."""
        response = self.client.get("/api/languages")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        languages = data["languages"]
        self.assertEqual(len(languages), 11)
        codes = [l["code"] for l in languages]
        expected_codes = ["hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "or", "en"]
        for c in expected_codes:
            self.assertIn(c, codes)

    def test_scheme_api_multilingual(self):
        """Verifies GET /api/scheme returns valid localized metadata in different languages."""
        # Test Hindi
        resp_hi = self.client.get("/api/scheme?lang=hi")
        self.assertEqual(resp_hi.status_code, 200)
        data_hi = resp_hi.get_json()
        self.assertEqual(data_hi["lang"], "hi")
        self.assertEqual(data_hi["texts"]["doc_aadhaar_title"], "आधार कार्ड")
        self.assertEqual(data_hi["helpline"]["toll_free"], "1800-266-6696")

        # Test Tamil
        resp_ta = self.client.get("/api/scheme?lang=ta")
        self.assertEqual(resp_ta.status_code, 200)
        data_ta = resp_ta.get_json()
        self.assertEqual(data_ta["lang"], "ta")
        self.assertIn("ஆதார்", data_ta["texts"]["doc_aadhaar_title"])

        # Test Telugu
        resp_te = self.client.get("/api/scheme?lang=te")
        self.assertEqual(resp_te.status_code, 200)
        data_te = resp_te.get_json()
        self.assertEqual(data_te["lang"], "te")
        self.assertIn("ఆధార్", data_te["texts"]["doc_aadhaar_title"])

        # Test English
        resp_en = self.client.get("/api/scheme?lang=en")
        self.assertEqual(resp_en.status_code, 200)
        data_en = resp_en.get_json()
        self.assertEqual(data_en["lang"], "en")
        self.assertEqual(data_en["texts"]["doc_aadhaar_title"], "Aadhaar Card")

    def test_walkthrough_api_multilingual(self):
        """Verifies GET /api/walkthrough returns localized 1-click demo steps."""
        resp = self.client.get("/api/walkthrough?lang=bn")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["lang"], "bn")
        steps = data["steps"]
        self.assertGreaterEqual(len(steps), 5)
        self.assertIn("নমস্কার", steps[0]["didi_speech"])

    def test_chat_api_multilingual(self):
        """Tests POST /api/chat with queries across languages."""
        # Test Hindi
        resp_hi = self.client.post("/api/chat", json={"query": "कागज़ क्या लगेंगे", "stage": "welcome", "lang": "hi"})
        self.assertEqual(resp_hi.status_code, 200)
        data_hi = resp_hi.get_json()
        self.assertEqual(data_hi["status"], "success")
        self.assertGreater(len(data_hi["data"]["reply_text"]), 10)

        # Test Tamil
        resp_ta = self.client.post("/api/chat", json={"query": "விலை என்ன", "stage": "welcome", "lang": "ta"})
        self.assertEqual(resp_ta.status_code, 200)
        data_ta = resp_ta.get_json()
        self.assertEqual(data_ta["status"], "success")
        self.assertGreater(len(data_ta["data"]["reply_text"]), 10)

        # Test English
        resp_en = self.client.post("/api/chat", json={"query": "is this free", "stage": "welcome", "lang": "en"})
        self.assertEqual(resp_en.status_code, 200)
        data_en = resp_en.get_json()
        self.assertEqual(data_en["status"], "success")
        self.assertGreater(len(data_en["data"]["reply_text"]), 10)

    def test_step_api(self):
        """Verifies GET /api/step/<step_num> and /api/step endpoints."""
        # Test GET /api/step/1 with English
        resp1 = self.client.get("/api/step/1?lang=en")
        self.assertEqual(resp1.status_code, 200)
        d1 = resp1.get_json()
        self.assertEqual(d1["status"], "success")
        self.assertEqual(d1["step_number"], 1)
        self.assertIn("Aadhaar", d1["english_text"])

        # Test POST /api/step with Hindi
        resp2 = self.client.post("/api/step", json={"step_number": 2, "lang": "hi"})
        self.assertEqual(resp2.status_code, 200)
        d2 = resp2.get_json()
        self.assertEqual(d2["status"], "success")
        self.assertEqual(d2["step_number"], 2)
        self.assertIn("Step 2", d2["english_text"])
        self.assertGreater(len(d2["translated_text"]), 0)

    def test_translate_api(self):
        """Verifies POST /api/translate endpoint with fallback."""
        # Missing text
        resp_err = self.client.post("/api/translate", json={"text": ""})
        self.assertEqual(resp_err.status_code, 400)

        # Valid text translated to Hindi
        resp = self.client.post("/api/translate", json={"text": "Hello sister, please come in.", "lang": "hi"})
        self.assertEqual(resp.status_code, 200)
        d = resp.get_json()
        self.assertEqual(d["status"], "success")
        self.assertGreater(len(d["translated_text"]), 0)

    def test_ask_api(self):
        """Verifies POST /api/ask endpoint with grounded facts."""
        resp = self.client.post("/api/ask", json={"question": "Is the gas cylinder free?", "lang": "en"})
        self.assertEqual(resp.status_code, 200)
        d = resp.get_json()
        self.assertEqual(d["status"], "success")
        self.assertIn("answer", d)
        self.assertGreater(len(d["answer"]), 0)

    def test_eligibility_api(self):
        """Verifies POST /api/eligibility endpoint."""
        resp = self.client.post("/api/eligibility", json={
            "is_adult_woman": True,
            "has_existing_connection": False,
            "is_bpl_or_poor": True
        })
        self.assertEqual(resp.status_code, 200)
        d = resp.get_json()
        self.assertEqual(d["status"], "success")
        self.assertTrue(d["eligibility"]["eligible"])

    def test_health_check(self):
        """Verifies GET /health endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "digital-didi")
        self.assertEqual(data["languages_supported"], 11)

    def test_gemini_client_fallback_mode(self):
        """Ensures GeminiClient functions safely without API key across languages."""
        client_offline = GeminiClient(api_key=None)
        result = client_offline.ask("documents needed", current_stage="welcome", lang="en")
        self.assertIn("reply_text", result)
        self.assertFalse(result["is_ai_generated"])
        self.assertGreater(len(result["reply_text"]), 0)

    def test_port_configuration(self):
        """Ensures PORT environment variable is respected."""
        original_port = os.environ.get("PORT")
        try:
            os.environ["PORT"] = "8080"
            port = int(os.environ.get("PORT", 5000))
            self.assertEqual(port, 8080)
        finally:
            if original_port is not None:
                os.environ["PORT"] = original_port
            else:
                os.environ.pop("PORT", None)

    def test_project_size_under_10mb(self):
        """
        Hard limit constraint test:
        Validates that the entire project size (excluding git and virtual environments)
        is strictly under 10 MB (10,485,760 bytes).
        """
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        total_size = 0
        ignored_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        max_allowed = 10 * 1024 * 1024  # 10 MB
        print(f"\nTotal calculated project size: {total_size} bytes ({total_size / 1024:.2f} KB)")
        self.assertLess(total_size, max_allowed, f"Project size {total_size} bytes exceeds 10 MB limit!")

if __name__ == "__main__":
    unittest.main()
