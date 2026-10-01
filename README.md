# डिजिटल दीदी (Digital Didi)
> **Multilingual AI Voice & Visual Guide for Rural First-Time Women Users**  
> *Supports 11 Major Indian Languages • Powered by Google Gemini (gemini-3.8-flash) & Pure Web Tech*

**Digital Didi** is an accessible, illiterate-friendly AI web application that helps a first-time woman user in rural India independently discover, verify eligibility, and gather documents for **Pradhan Mantri Ujjwala Yojana 2.0 (मुफ़्त गैस चूल्हा और सिलेंडर)** in her own mother tongue.

---

## 🌟 Key Features

1. **11 Major Indian Languages Supported:**
   - 🇮🇳 **Hindi (हिन्दी)**
   - 🇮🇳 **Tamil (தமிழ்)**
   - 🇮🇳 **Telugu (తెలుగు)**
   - 🇮🇳 **Bengali (বাংলা)**
   - 🇮🇳 **Marathi (मराठी)**
   - 🇮🇳 **Gujarati (ગુજરાતી)**
   - 🇮🇳 **Kannada (ಕನ್ನಡ)**
   - 🇮🇳 **Malayalam (മലയാളം)**
   - 🇮🇳 **Punjabi (ਪੰਜਾਬੀ)**
   - 🇮🇳 **Odia (ଓଡ଼ିଆ)**
   - 🌐 **English**

2. **Flag & Native-Script Icon Language Picker:**
   - An intuitive, top-pinned visual ribbon displaying recognizable native scripts (e.g., `தமிழ்`, `తెలుగు`, `বাংলা`, `मराठी`, `ગુજરાતી`).
   - Tapping any language immediately updates all on-screen content and begins voice narration in that language.

3. **Voice-First ("डिजिटल दीदी" Persona):**
   - Natural spoken voice narration using the Browser Web Speech API (`SpeechSynthesis` & `SpeechRecognition` in regional language codes).
   - Powered by **Google Gemini (`gemini-3.8-flash`)** acting as a compassionate rural village elder sister.
   - Built-in zero-fail fallback: Every prompt and query works offline or under API quota limits.

4. **Zero-Text / Large Icon-Driven UI:**
   - Giant circular pulsing Microphone button (`#btn-mic`) for speech input.
   - Large pictorial yes/no choices (`✔️ हाँ` / `❌ ना`).
   - Realistic CSS-crafted document cards for **Aadhaar Card**, **Ration Card**, and **Bank Passbook** (tap any card to hear its audio description in the active language).

5. **1-Click Sample Walkthrough Demo:**
   - Tap **"⚡ 1-क्लिक डेमो चलाएं"** at the top right to watch a full simulated voice conversation end-to-end in the selected language.

6. **Ultra-Lightweight (< 10 MB Hard Limit):**
   - Total repository size is **~151 KB** (less than 1.5% of the 10 MB limit).
   - Uses pure CSS graphics and inline SVGs with zero heavy image or media files.

7. **No Database & No Login:**
   - Instant access with zero barriers for first-time internet users.

---

## 📁 Project Structure

```
digital-didi/
├── app.py              # Flask server, dynamic PORT binding, translation & Q&A endpoints
├── scheme_data.py      # Hardcoded PMUY facts (SSOT), 11-language UI strings & walkthrough
├── gemini_client.py    # Multilingual Gemini 3.8 Flash client with safe English fallbacks
├── templates/
│   └── index.html      # Accessible layout with 11-language native-script ribbon
├── static/
│   ├── style.css       # Clean responsive Indian civic styling (< 25 KB)
│   └── app.js          # Speech recognition, speech synthesis & Web Audio earcons
├── tests/
│   └── test_app.py     # 18 unit & integration tests including 10 MB limit verification
├── requirements.txt    # flask, python-dotenv, gunicorn, google-genai
├── .env.example        # Configuration template
├── .gitignore          # Ignores .env, __pycache__, .venv
└── README.md           # Project documentation & hackathon submission guide
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Main accessible visual & voice interface (`?lang=hi`) |
| `/api/languages` | `GET` | List of all 11 supported Indian languages |
| `/api/scheme` | `GET` | Localized PMUY scheme metadata, criteria, and benefits |
| `/api/step/<num>` | `GET/POST` | Official PMUY step guidance with on-demand Indic translation |
| `/api/translate` | `POST` | Translates English scheme instructions into any supported Indic language |
| `/api/ask` | `POST` | Grounded Q&A strictly using verified PMUY facts via Gemini |
| `/api/eligibility` | `POST` | Validates household eligibility (age, prior connection, BPL/ration card) |
| `/api/chat` | `POST` | Natural conversational voice query handling with Didi persona |
| `/api/walkthrough` | `GET` | Localized 1-click step-by-step automated demo script |
| `/health` | `GET` | Cloud health check endpoint |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# In .env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

### 3. Run the App
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in Chrome, Edge, or a mobile browser.

### 4. Run Test Suite
```bash
python -m unittest tests/test_app.py
```
*(Runs all 18 automated tests, verifying 11-language endpoints, Gemini resilience, safe English fallbacks, and the < 10 MB project limit)*.
