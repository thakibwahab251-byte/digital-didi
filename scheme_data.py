"""
scheme_data.py
Defines the single source of truth for the Pradhan Mantri Ujjwala Yojana (PMUY) scheme,
hardcoded in English with real facts, along with multilingual translations for the Digital Didi UI.

NOTE: These facts should be verified against the official PMUY government source
(https://www.pmuy.gov.in) before real-world use.
"""

# ==============================================================================
# SINGLE SOURCE OF TRUTH (ENGLISH FACTS - PMUY 2.0)
# ==============================================================================
# NOTE: These facts should be verified against the official PMUY government source
# (https://www.pmuy.gov.in) before real-world use.

PMUY_SCHEME_FACTS = {
    "scheme_id": "pm_ujjwala_yojana",
    "official_name": "Pradhan Mantri Ujjwala Yojana 2.0 (PMUY)",
    "ministry": "Ministry of Petroleum and Natural Gas (MoPNG), Government of India",
    "official_website": "https://www.pmuy.gov.in",
    "official_helpline": "1800-266-6696",
    "emergency_leak_helpline": "1906",
    "target_beneficiary": "Adult women from Below Poverty Line (BPL) and underprivileged households",
    "benefits": [
        {
            "id": "free_lpg_connection",
            "title": "Free LPG Connection",
            "description": "Zero security deposit for the 14.2 kg LPG cylinder.",
            "cost_to_beneficiary": "₹0"
        },
        {
            "id": "free_first_refill",
            "title": "First Refill Cylinder Free",
            "description": "The first filled cylinder is provided completely free of cost.",
            "cost_to_beneficiary": "₹0"
        },
        {
            "id": "free_gas_stove",
            "title": "Free Two-Burner Gas Stove",
            "description": "ISI certified two-burner LPG stove (hotplate) provided free.",
            "cost_to_beneficiary": "₹0"
        },
        {
            "id": "free_safety_accessories",
            "title": "Safety Hose & Regulator",
            "description": "Safety regulator and high-grade safety hose pipe supplied at no cost.",
            "cost_to_beneficiary": "₹0"
        }
    ],
    "eligibility_criteria": [
        {
            "code": "adult_woman",
            "rule": "Applicant must be an adult woman aged 18 years or above.",
            "mandatory": True
        },
        {
            "code": "no_prior_connection",
            "rule": "There must be no existing LPG connection in the same household from any Oil Marketing Company (IOCL, BPCL, HPCL).",
            "mandatory": True
        },
        {
            "code": "bpl_or_poor_household",
            "rule": "Applicant must belong to an eligible BPL/poor household holding a ration card or belonging to SC/ST, PMAY (Gramin), Antyodaya Anna Yojana (AAY), Most Backward Classes, Forest Dwellers, or River Islands.",
            "mandatory": True
        }
    ],
    "required_documents": [
        {
            "id": "aadhaar",
            "name": "Aadhaar Card",
            "purpose": "Proof of Identity and Proof of Address of the adult woman applicant.",
            "mandatory": True
        },
        {
            "id": "ration_card",
            "name": "Ration Card",
            "purpose": "State Government issued ration card certifying family composition and household status.",
            "mandatory": True
        },
        {
            "id": "bank_passbook",
            "name": "Bank Account Passbook",
            "purpose": "Aadhaar-linked active bank account (Jan Dhan or regular savings) for direct benefit subsidy transfer.",
            "mandatory": True
        },
        {
            "id": "photograph",
            "name": "Passport-size Photograph",
            "purpose": "Recent photograph of the applicant for KYC application submission.",
            "mandatory": True
        }
    ],
    "application_steps": [
        {
            "step_number": 1,
            "title": "Gather Documents",
            "spoken_text": "Step 1: Gather your documents. You need the woman applicant's Aadhaar card, your family ration card, your bank passbook, and a passport-size photo."
        },
        {
            "step_number": 2,
            "title": "Visit Nearest Gas Agency or CSC",
            "spoken_text": "Step 2: Visit your nearest LPG distributor or Common Service Centre. You can visit any Indane, Bharat Gas, or HP Gas agency in your area."
        },
        {
            "step_number": 3,
            "title": "Submit Application Form",
            "spoken_text": "Step 3: Fill out the simple Ujjwala 2.0 application form and submit the 14-point declaration showing family composition."
        },
        {
            "step_number": 4,
            "title": "Verification and De-duplication",
            "spoken_text": "Step 4: The gas agency will verify your documents to confirm that no other member of your household already has a gas connection."
        },
        {
            "step_number": 5,
            "title": "Receive Free Gas Connection",
            "spoken_text": "Step 5: Once verified, receive your free gas connection, first filled cylinder, two-burner stove, regulator, and safety pipe with zero deposit."
        }
    ]
}


def get_step(step_number):
    """
    Returns the spoken-friendly English text for a specific step in the PMUY application process.

    Args:
        step_number (int): 1-indexed step number (1 to 5).

    Returns:
        str: Spoken-friendly English guidance for that step.
    """
    steps = PMUY_SCHEME_FACTS["application_steps"]
    for s in steps:
        if s["step_number"] == step_number:
            return s["spoken_text"]
    return f"Invalid step number: {step_number}. Available steps are 1 to {len(steps)}."


def check_eligibility(answers):
    """
    Evaluates applicant eligibility for PMUY based on basic yes/no questions.

    Args:
        answers (dict): Mapping containing answers to eligibility questions:
            - 'is_adult_woman' or 'is_woman_over_18': bool or str ('yes'/'no')
            - 'has_existing_connection': bool or str ('yes'/'no')
            - 'is_bpl_or_poor' or 'has_ration_card': bool or str ('yes'/'no')

    Returns:
        dict: Result with:
            - 'eligible' (bool): True if eligible, False otherwise.
            - 'reason' (str): Spoken-friendly English explanation of the decision.
    """
    def _is_yes(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in ("yes", "y", "true", "1", "haan", "ha")
        return bool(val)

    # 1. Must be adult woman
    woman_val = answers.get("is_adult_woman", answers.get("is_woman_over_18", False))
    if not _is_yes(woman_val):
        return {
            "eligible": False,
            "reason": "The applicant must be an adult woman aged 18 years or older."
        }

    # 2. Must not have existing connection
    conn_val = answers.get("has_existing_connection", False)
    if _is_yes(conn_val):
        return {
            "eligible": False,
            "reason": "PMUY is exclusively for households without an existing LPG connection. A connection already exists in this household."
        }

    # 3. Must be BPL / have ration card
    bpl_val = answers.get("is_bpl_or_poor", answers.get("has_ration_card", False))
    if not _is_yes(bpl_val):
        return {
            "eligible": False,
            "reason": "The applicant must belong to a BPL or underprivileged household holding a valid ration card."
        }

    return {
        "eligible": True,
        "reason": "Congratulations! The applicant is fully eligible for a free LPG connection, stove, and first refill under PMUY 2.0."
    }


# ==============================================================================
# MULTILINGUAL SUPPORT & UI TRANSLATIONS
# ==============================================================================

LANGUAGES = [
    {"code": "hi", "name": "Hindi", "native": "हिन्दी", "speech_code": "hi-IN", "flag": "🇮🇳"},
    {"code": "ta", "name": "Tamil", "native": "தமிழ்", "speech_code": "ta-IN", "flag": "🇮🇳"},
    {"code": "te", "name": "Telugu", "native": "తెలుగు", "speech_code": "te-IN", "flag": "🇮🇳"},
    {"code": "bn", "name": "Bengali", "native": "বাংলা", "speech_code": "bn-IN", "flag": "🇮🇳"},
    {"code": "mr", "name": "Marathi", "native": "मराठी", "speech_code": "mr-IN", "flag": "🇮🇳"},
    {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી", "speech_code": "gu-IN", "flag": "🇮🇳"},
    {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ", "speech_code": "kn-IN", "flag": "🇮🇳"},
    {"code": "ml", "name": "Malayalam", "native": "മലയാളം", "speech_code": "ml-IN", "flag": "🇮🇳"},
    {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ", "speech_code": "pa-IN", "flag": "🇮🇳"},
    {"code": "or", "name": "Odia", "native": "ଓଡ଼ିଆ", "speech_code": "or-IN", "flag": "🇮🇳"},
    {"code": "en", "name": "English", "native": "English", "speech_code": "en-IN", "flag": "🌐"}
]

TRANSLATIONS = {
    "hi": {
        "app_title": "डिजिटल दीदी",
        "app_subtitle": "उज्ज्वला दीदी • मुफ़्त गैस योजना साथी",
        "didi_greeting": "नमस्ते दीदी! मैं आपकी डिजिटल दीदी हूँ। क्या आपके घर में मुफ़्त गैस चूल्हा और सिलेंडर चाहिए?",
        "scheme_name": "प्रधानमंत्री उज्ज्वला योजना 2.0",
        "scheme_tagline": "गाँव की हर बहन के लिए सुरक्षित धुआं-मुक्त चूल्हा और पहला भरा सिलेंडर मुफ़्त!",
        "benefits": [
            {"title": "पहला सिलेंडर मुफ़्त", "desc": "पहला भरा हुआ 14.2 किलो गैस सिलेंडर मुफ़्त।", "badge": "मुफ़्त"},
            {"title": "2 बर्नर गैस चूल्हा", "desc": "सुरक्षित दो बर्नर वाला नया चूल्हा मुफ़्त।", "badge": "मुफ़्त"},
            {"title": "₹0 सुरक्षा राशि", "desc": "कोई सिक्योरिटी डिपॉजिट या दलाली नहीं।", "badge": "₹0 फीस"}
        ],
        "q1_text": "दीदी, क्या आपके घर में पहले से कोई गैस सिलेंडर है?",
        "q1_hint": "नीचे दिए गए दो बड़े बटनों में से एक को छूकर बताएं:",
        "q1_no": "ना, कोई गैस नहीं है",
        "q1_no_desc": "लकड़ी या चूल्हे पर खाना बनाते हैं",
        "q1_yes": "हाँ, गैस पहले से है",
        "q1_yes_desc": "घर में पहले से सिलेंडर मौजूद है",
        "q2_text": "क्या आपके पास राशन कार्ड या बीपीएल पर्ची है?",
        "q2_hint": "जिसमें परिवार के सदस्यों के नाम लिखे होते हैं:",
        "q2_yes": "हाँ, राशन कार्ड है",
        "q2_yes_desc": "परिवार की राशन पर्ची मौजूद है",
        "q2_no": "ना, राशन कार्ड नहीं है",
        "q2_no_desc": "राशन कार्ड अभी तक नहीं बना है",
        "congrats_title": "बधाई हो दीदी! आप पात्र हैं",
        "congrats_desc": "आपको मुफ़्त गैस चूल्हा और सिलेंडर मिलेगा।",
        "docs_heading": "📋 सिर्फ ये 3 कागज़ात तैयार करें:",
        "docs_hint": "(किसी भी कागज़ पर टैप करके उसकी आवाज़ सुनें)",
        "doc_aadhaar_title": "आधार कार्ड",
        "doc_aadhaar_desc": "महिला का खुद का आधार कार्ड।",
        "doc_aadhaar_audio": "पहला कागज़: आपका आधार कार्ड। पहचान और पते के लिए इसकी फोटोकॉपी लगेगी।",
        "doc_ration_title": "राशन कार्ड",
        "doc_ration_desc": "परिवार के सभी सदस्यों के नाम वाला राशन कार्ड।",
        "doc_ration_audio": "दूसरा कागज़: आपका राशन कार्ड। जिसमें परिवार के सभी सदस्यों के नाम लिखे हों।",
        "doc_passbook_title": "बैंक पासबुक",
        "doc_passbook_desc": "महिला का बैंक खाता या जनधन खाता।",
        "doc_passbook_audio": "तीसरा कागज़: बैंक पासबुक। खाता नंबर और सब्सिडी के लिए इसकी फोटोकॉपी लगेगी।",
        "where_title": "📍 ये तीनों कागज़ लेकर यहाँ जाएं:",
        "where_agency_title": "1. पास की गैस एजेंसी की दुकान",
        "where_agency_desc": "इंडेन, भारत गैस, या एचपी गैस की नजदीकी एजेंसी पर सीधे जाएं।",
        "where_csc_title": "2. गाँव का जन सेवा केंद्र (CSC)",
        "where_csc_desc": "गाँव के पंचायत भवन या कंप्यूटर केंद्र पर जाकर ऑनलाइन फॉर्म भरवाएं।",
        "safety_alert": "सावधानी दीदी: यह योजना सरकार की तरफ से 100% मुफ़्त है। किसी भी दलाल को एक रुपया भी न दें!",
        "ineligible_text": "दीदी, उज्ज्वला 2.0 नए गैस कनेक्शन के लिए है। यदि राशन कार्ड नहीं है, तो पहले पंचायत से राशन कार्ड बनवा लें।",
        "btn_start": "अपनी पात्रता जांचें (शुरू करें)",
        "btn_to_where": "ये कागज़ लेकर कहाँ जाना है? देखें 👉",
        "btn_restart": "🔄 फिर से शुरू करें",
        "btn_retry": "🔄 दोबारा जांचें",
        "btn_demo": "1-क्लिक डेमो चलाएं",
        "mic_tap": "माइक दबाकर बोलें",
        "mic_listening": "सुन रही हूँ... बोलिए दीदी"
    },
    "ta": {
        "app_title": "டிஜிட்டல் தீதி",
        "app_subtitle": "உஜ்வாலா தீதி • இலவச எரிவாயு திட்ட வழிகாட்டி",
        "didi_greeting": "வணக்கம் அம்மா! நான் உங்கள் டிஜிட்டல் தீதி. உங்கள் வீட்டிற்கு இலவச எரிவாயு அடுப்பும் சிலிண்டரும் வேண்டுமா?",
        "scheme_name": "பிரதம மந்திரி உஜ்வாலா திட்டம் 2.0",
        "scheme_tagline": "கிராமத்துப் பெண்களுக்கு இலவச கேஸ் அடுப்பு மற்றும் இலவச சிலிண்டர்!",
        "benefits": [
            {"title": "முதல் சிலிண்டர் இலவசம்", "desc": "14.2 கிலோ எடையுள்ள முதல் சிலிண்டர் முற்றிலும் இலவசம்.", "badge": "இலவசம்"},
            {"title": "2 பர்னர் கேஸ் அடுப்பு", "desc": "பாதுகாப்பான புதிய இரட்டை பர்னர் அடுப்பு இலவசம்.", "badge": "இலவசம்"},
            {"title": "₹0 வைப்புத்தொகை", "desc": "எந்தவித கட்டணமும் தரகரும் தேவையில்லை.", "badge": "₹0 கட்டணம்"}
        ],
        "q1_text": "அம்மா, உங்கள் வீட்டில் ஏற்கனவே எரிவாயு இணைப்பு உள்ளதா?",
        "q1_hint": "கீழே உள்ள இரண்டு பெரிய பொத்தான்களில் ஒன்றைத் தொடவும்:",
        "q1_no": "இல்லை, கேஸ் இணைப்பு இல்லை",
        "q1_no_desc": "விறகு அல்லது மண்ணெண்ணெய் அடுப்பில் சமைக்கிறோம்",
        "q1_yes": "ஆம், ஏற்கனவே கேஸ் உள்ளது",
        "q1_yes_desc": "வீட்டில் ஏற்கனவே சிலிண்டர் உள்ளது",
        "q2_text": "உங்களிடம் ரேஷன் கார்டு உள்ளதா?",
        "q2_hint": "குடும்ப உறுப்பினர்களின் பெயர்கள் உள்ள அட்டை:",
        "q2_yes": "ஆம், ரேஷன் கார்டு உள்ளது",
        "q2_yes_desc": "குடும்ப ரேஷன் அட்டை எங்களிடம் உள்ளது",
        "q2_no": "இல்லை, ரேஷன் கார்டு இல்லை",
        "q2_no_desc": "ரேஷன் கார்டு இதுவரை பெறவில்லை",
        "congrats_title": "வாழ்த்துகள் அம்மா! நீங்கள் தகுதியானவர்",
        "congrats_desc": "உங்களுக்கு இலவச கேஸ் அடுப்பும் சிலிண்டரும் கிடைக்கும்.",
        "docs_heading": "📋 இந்த 3 ஆவணங்களை மட்டும் தயார் செய்யுங்கள்:",
        "docs_hint": "(ஆடியோவைக் கேட்க ஏதேனும் அட்டையைத் தொடவும்)",
        "doc_aadhaar_title": "ஆதார் அட்டை",
        "doc_aadhaar_desc": "விண்ணப்பதாரர் பெண்ணின் ஆதார் அட்டை.",
        "doc_aadhaar_audio": "முதல் ஆவணம்: உங்கள் ஆதார் அட்டை நகல்.",
        "doc_ration_title": "ரேஷன் அட்டை",
        "doc_ration_desc": "குடும்ப உறுப்பினர்கள் பெயர் உள்ள ரேஷன் அட்டை.",
        "doc_ration_audio": "இரண்டாவது ஆவணம்: உங்கள் குடும்ப ரேஷன் அட்டை.",
        "doc_passbook_title": "வங்கி பாஸ்புக்",
        "doc_passbook_desc": "பெண்ணின் பெயரில் உள்ள வங்கி கணக்கு பாஸ்புக்.",
        "doc_passbook_audio": "மூன்றாவது ஆவணம்: உங்கள் வங்கி பாஸ்புக் முதல் பக்க நகல்.",
        "where_title": "📍 இந்த ஆவணங்களுடன் இங்கு செல்லுங்கள்:",
        "where_agency_title": "1. அருகிலுள்ள கேஸ் ஏஜென்சி",
        "where_agency_desc": "இண்டேன், பாரத் கேஸ் அல்லது ஹெச்பி கேஸ் ஏஜென்சிக்கு நேரில் செல்லவும்.",
        "where_csc_title": "2. கிராம இ-சேவை மையம் (CSC)",
        "where_csc_desc": "உங்கள் கிராம இ-சேவை மையத்தில் விண்ணப்பிக்கலாம்.",
        "safety_alert": "எச்சரிக்கை: இத்திட்டம் 100% இலவசம். இடைத்தரகர்களுக்கு பணம் கொடுக்க வேண்டாம்!",
        "ineligible_text": "உஜ்வாலா 2.0 புதிய இணைப்புகளுக்கு மட்டுமே. ரேஷன் அட்டை இல்லையென்றால் முதலில் பஞ்சாயத்தில் அட்டை பெறவும்.",
        "btn_start": "தகுதியை சரிபார்க்கவும் (தொடங்கு)",
        "btn_to_where": "எங்கு செல்ல வேண்டும்? பார்க்கவும் 👉",
        "btn_restart": "🔄 மீண்டும் தொடங்கவும்",
        "btn_retry": "🔄 மீண்டும் சரிபார்க்கவும்",
        "btn_demo": "1-கிளிக் டெமோ இயக்கவும்",
        "mic_tap": "மைக் அழுத்தி பேசவும்",
        "mic_listening": "கேட்கிறேன்... பேசுங்கள் அம்மா"
    },
    "te": {
        "app_title": "డిజిటల్ దీదీ",
        "app_subtitle": "ఉజ్వల దీదీ • ఉచిత గ్యాస్ పథకం మార్గదర్శి",
        "didi_greeting": "నమస్కారం అక్కా! నేను మీ డిజిటల్ దీదీని. మీ ఇంటికి ఉచిత గ్యాస్ పొయ్యి మరియు సిలిండర్ కావాలా?",
        "scheme_name": "ప్రధాన మంత్రి ఉజ్వల యోజన 2.0",
        "scheme_tagline": "గ్రామీణ మహిళలకు సురక్షితమైన పొగలేని పొయ్యి మరియు ఉచిత సిలిండర్!",
        "benefits": [
            {"title": "మొదటి సిలిండర్ ఉచితం", "desc": "14.2 కిలోల మొదటి నిండిన సిలిండర్ ఉచితం.", "badge": "ఉచితం"},
            {"title": "2 బర్నర్ల గ్యాస్ పొయ్యి", "desc": "నాణ్యమైన డబుల్ బర్నర్ గ్యాస్ స్టవ్ ఉచితం.", "badge": "ఉచితం"},
            {"title": "₹0 డిపాజిట్", "desc": "ఎటువంటి సెక్యూరిటీ డిపాజిట్ లేదా రుసుము లేదు.", "badge": "₹0 ఫీజు"}
        ],
        "q1_text": "అక్కా, మీ ఇంట్లో ఇదివరకే గ్యాస్ కనెక్షన్ ఉందా?",
        "q1_hint": "క్రింది రెండు పెద్ద బటన్లలో ఒకదాన్ని తాకండి:",
        "q1_no": "లేదు, గ్యాస్ కనెక్షన్ లేదు",
        "q1_no_desc": "కట్టెల పొయ్యిపై వంట చేసుకుంటాం",
        "q1_yes": "అవును, గ్యాస్ ఉంది",
        "q1_yes_desc": "ఇంట్లో ఇప్పటికే సిలిండర్ ఉంది",
        "q2_text": "మీ దగ్గర రేషన్ కార్డు ఉందా?",
        "q2_hint": "కుటుంబ సభ్యుల పేర్లు ఉన్న కార్డు:",
        "q2_yes": "అవును, రేషన్ కార్డు ఉంది",
        "q2_yes_desc": "కుటుంబ రేషన్ కార్డు మా వద్ద ఉంది",
        "q2_no": "లేదు, రేషన్ కార్డు లేదు",
        "q2_no_desc": "రేషన్ కార్డు ఇంకా తయారు కాలేదు",
        "congrats_title": "అభినందనలు అక్కా! మీరు అర్హులు",
        "congrats_desc": "మీకు ఉచిత గ్యాస్ పొయ్యి మరియు సిలిండర్ లభిస్తుంది.",
        "docs_heading": "📋 ఈ 3 పత్రాలు సిద్ధం చేసుకోండి:",
        "docs_hint": "(వాయిస్ వినడానికి ఏదైనా కార్డుపై తాకండి)",
        "doc_aadhaar_title": "ఆధార్ కార్డు",
        "doc_aadhaar_desc": "మహిళ స్వంత ఆధార్ కార్డు జిరాక్స్.",
        "doc_aadhaar_audio": "మొదటి పత్రం: మీ ఆధార్ కార్డు.",
        "doc_ration_title": "రేషన్ కార్డు",
        "doc_ration_desc": "కుటుంబ సభ్యుల పేర్లు ఉన్న రేషన్ కార్డు.",
        "doc_ration_audio": "రెండవ పత్రం: మీ రేషన్ కార్డు.",
        "doc_passbook_title": "బ్యాంకు పాసుబుక్",
        "doc_passbook_desc": "మహిళ పేరు మీద ఉన్న బ్యాంక్ ఖాతా పాసుబుక్.",
        "doc_passbook_audio": "మూడవ పత్రం: మీ బ్యాంక్ ఖాతా పాసుబుక్.",
        "where_title": "📍 ఈ పత్రాలతో ఇక్కడికి వెళ్ళండి:",
        "where_agency_title": "1. సమీపంలోని గ్యాస్ ఏజెన్సీ",
        "where_agency_desc": "ఇండేన్, భారత్ గ్యాస్ లేదా హెచ్‌పి గ్యాస్ ఏజెన్సీకి వెళ్ళండి.",
        "where_csc_title": "2. గ్రామ సచివాలయం / CSC కేంద్రం",
        "where_csc_desc": "మీ గ్రామ సాధారణ సేవా కేంద్రంలో దరఖాస్తు చేసుకోవచ్చు.",
        "safety_alert": "హెచ్చరిక: ఈ పథకం 100% ఉచితం. దళారులకు ఎటువంటి డబ్బు ఇవ్వకండి!",
        "ineligible_text": "ఉజ్వల 2.0 కొత్త కనెక్షన్ల కోసం మాత్రమే. రేషన్ కార్డు లేకపోతే ముందుగా దరఖాస్తు చేయండి.",
        "btn_start": "అర్హతను తనిఖీ చేయండి (ప్రారంభించండి)",
        "btn_to_where": "ఎక్కడికి వెళ్ళాలి? చూడండి 👉",
        "btn_restart": "🔄 మళ్ళీ ప్రారంభించండి",
        "btn_retry": "🔄 మళ్ళీ తనిఖీ చేయండి",
        "btn_demo": "1-క్లిక్ డెమో నడపండి",
        "mic_tap": "మైక్ నొక్కి మాట్లాడండి",
        "mic_listening": "వింటున్నాను... మాట్లాడండి అక్కా"
    },
    "bn": {
        "app_title": "ডিজিটাল দিদি",
        "app_subtitle": "উজ্জ্বলা দিদি • বিনামূল্যে গ্যাস যোজনা সহায়ক",
        "didi_greeting": "নমস্কার দিদি! আমি আপনার ডিজিটাল দিদি। আপনার কি বিনামূল্যে রান্নার গ্যাস ও সিলিন্ডার চাই?",
        "scheme_name": "প্রধানমন্ত্রী উজ্জ্বলা যোজনা ২.০",
        "scheme_tagline": "গ্রামের বোনেদের জন্য বিনামূল্যে গ্যাস ও নিরাপদ উনুন!",
        "benefits": [
            {"title": "প্রথম সিলিন্ডার বিনামূল্যে", "desc": "১৪.২ কেজি গ্যাস সিলিন্ডার সম্পূর্ণ বিনামূল্যে।", "badge": "বিনামূল্যে"},
            {"title": "২ বার্নারের গ্যাস উনুন", "desc": "নিরাপদ নতুন দুই বার্নারের উনুন সম্পূর্ণ বিনামূল্যে।", "badge": "বিনামূল্যে"},
            {"title": "₹০ ডিপোজিট", "desc": "কোনো জামানত বা দালালি দিতে হবে না।", "badge": "₹০ খরচ"}
        ],
        "q1_text": "দিদি, আপনার বাড়িতে কি আগে থেকেই কোনো গ্যাস কানেকশন আছে?",
        "q1_hint": "নিচের দুটি বড় বোতামের একটি স্পর্শ করে বলুন:",
        "q1_no": "না, কোনো গ্যাস নেই",
        "q1_no_desc": "কাঠ বা ঘুঁটের উনুনে রান্না করি",
        "q1_yes": "হ্যাঁ, আগে থেকেই গ্যাস আছে",
        "q1_yes_desc": "বাড়িতে ইতিমধ্যে সিলিন্ডার আছে",
        "q2_text": "আপনার কি রেশন কার্ড আছে?",
        "q2_hint": "যে কার্ডে পরিবারের সদস্যদের নাম লেখা আছে:",
        "q2_yes": "হ্যাঁ, রেশন কার্ড আছে",
        "q2_yes_desc": "পরিবারের রেশন কার্ড আমাদের কাছে আছে",
        "q2_no": "না, রেশন কার্ড নেই",
        "q2_no_desc": "রেশন কার্ড এখনও তৈরি হয়নি",
        "congrats_title": "অভিনন্দন দিদি! আপনি যোগ্য",
        "congrats_desc": "আপনি বিনামূল্যে গ্যাস উনুন ও সিলিন্ডার পাবেন।",
        "docs_heading": "📋 কেবল এই ৩টি কাগজপত্র তৈরি রাখুন:",
        "docs_hint": "(কথা শুনতে যেকোনো কার্ডে স্পর্শ করুন)",
        "doc_aadhaar_title": "আধার কার্ড",
        "doc_aadhaar_desc": "আবেদনকারী মহিলার নিজস্ব আধার কার্ড।",
        "doc_aadhaar_audio": "প্রথম কাগজ: আপনার আধার কার্ড।",
        "doc_ration_title": "রেশন কার্ড",
        "doc_ration_desc": "পরিবারের সদস্যদের নামসহ রেশন কার্ড।",
        "doc_ration_audio": "দ্বিতীয় কাগজ: আপনার পরিবারের রেশন কার্ড।",
        "doc_passbook_title": "ব্যাঙ্ক পাসবই",
        "doc_passbook_desc": "মহিলার নামের ব্যাঙ্ক অ্যাকাউন্ট বা জনধন খাতা।",
        "doc_passbook_audio": "তৃতীয় কাগজ: ব্যাঙ্ক পাসবইয়ের প্রথম পাতার কপি।",
        "where_title": "📍 এই কাগজগুলো নিয়ে এখানে যান:",
        "where_agency_title": "১. নিকটবর্তী গ্যাস এজেন্সি",
        "where_agency_desc": "ইন্ডেন, ভারত গ্যাস বা এইচপি গ্যাসের দোকানে যান।",
        "where_csc_title": "২. তথ্যমিত্র কেন্দ্র (CSC সেন্টার)",
        "where_csc_desc": "গ্রামের পঞ্চায়েত বা গ্রাহক সেবা কেন্দ্রে গিয়ে ফর্ম জমা দিন।",
        "safety_alert": "সাবধান দিদি: এই যোজনা সম্পূর্ণ বিনামূল্যে। কাউকে কোনো টাকা দেবেন না!",
        "ineligible_text": "উজ্জ্বলা ২.০ নতুন কানেকশনের জন্য। রেশন কার্ড না থাকলে আগে পঞ্চায়েত থেকে তৈরি করুন।",
        "btn_start": "যোগ্যতা পরীক্ষা করুন (শুরু করুন)",
        "btn_to_where": "কোথায় যেতে হবে? দেখুন 👉",
        "btn_restart": "🔄 পুনরায় শুরু করুন",
        "btn_retry": "🔄 আবার পরীক্ষা করুন",
        "btn_demo": "১-ক্লিক ডেমো চালান",
        "mic_tap": "মাইক টিপে বলুন",
        "mic_listening": "শুনছি দিদি... বলুন"
    },
    "mr": {
        "app_title": "डिजिटल दीदी",
        "app_subtitle": "उज्ज्वला दीदी • मोफत गॅस योजना मार्गदर्शक",
        "didi_greeting": "नमस्कार ताई! मी तुमची डिजिटल दीदी आहे. तुमच्या घरासाठी मोफत गॅस शेगडी आणि सिलेंडर हवे आहे का?",
        "scheme_name": "प्रधानमंत्री उज्ज्वला योजना २.०",
        "scheme_tagline": "ग्रामीण महिलांसाठी धूरमुक्त शेगडी आणि पहिला भरलेला सिलेंडर मोफत!",
        "benefits": [
            {"title": "पहिला सिलेंडर मोफत", "desc": "१४.२ किलोचा पहिला भरलेला सिलेंडर पूर्णपणे मोफत.", "badge": "मोफत"},
            {"title": "२ बर्नर गॅस शेगडी", "desc": "सुरक्षित दोन बर्नरची नवीन गॅस शेगडी मोफत.", "badge": "मोफत"},
            {"title": "₹० अनामत रक्कम", "desc": "कोणतीही डिपॉझिट किंवा दलाली द्यावी लागत नाही.", "badge": "₹० फी"}
        ],
        "q1_text": "ताई, तुमच्या घरात आधीपासून गॅस सिलेंडर कनेक्शन आहे का?",
        "q1_hint": "खालील दोन मोठ्या बटनांपैकी एकावर स्पर्श करा:",
        "q1_no": "नाही, गॅस कनेक्शन नाही",
        "q1_no_desc": "आम्ही चुलीवर लाकडावर स्वयंपाक करतो",
        "q1_yes": "हो, गॅस आधीपासून आहे",
        "q1_yes_desc": "घरात आधीच गॅस सिलेंडर आहे",
        "q2_text": "तुमच्याकडे रेशन कार्ड आहे का?",
        "q2_hint": "कुटुंबातील सदस्यांची नावे असलेले रेशन कार्ड:",
        "q2_yes": "हो, रेशन कार्ड आहे",
        "q2_yes_desc": "आमच्याकडे कुटुंबाचे रेशन कार्ड आहे",
        "q2_no": "नाही, रेशन कार्ड नाही",
        "q2_no_desc": "रेशन कार्ड अद्याप बनलेले नाही",
        "congrats_title": "अभिनंदन ताई! तुम्ही पात्र आहात",
        "congrats_desc": "तुम्हाला मोफत गॅस शेगडी आणि सिलेंडर मिळेल.",
        "docs_heading": "📋 फक्त ही ३ कागदपत्रे तयार ठेवा:",
        "docs_hint": "(आवाज ऐकण्यासाठी कोणत्याही कार्डावर स्पर्श करा)",
        "doc_aadhaar_title": "आधार कार्ड",
        "doc_aadhaar_desc": "महिला अर्जदाराचे स्वतःचे आधार कार्ड.",
        "doc_aadhaar_audio": "पहिले कागदपत्र: तुमचे आधार कार्ड.",
        "doc_ration_title": "रेशन कार्ड",
        "doc_ration_desc": "कुटुंबातील सर्वांची नावे असलेले रेशन कार्ड.",
        "doc_ration_audio": "दुसरे कागदपत्र: तुमचे रेशन कार्ड.",
        "doc_passbook_title": "बँक पासबुक",
        "doc_passbook_desc": "महिला अर्जदाराचे बँक खाते किंवा जनधन खाते.",
        "doc_passbook_audio": "तिसरे कागदपत्र: बँक पासबुकच्या पहिल्या पानाची झेरॉक्स.",
        "where_title": "📍 ही कागदपत्रे घेऊन येथे जा:",
        "where_agency_title": "१. जवळची गॅस एजन्सी",
        "where_agency_desc": "इंडेन, भारत गॅस किंवा एचपी गॅस एजन्सीवर जा.",
        "where_csc_title": "२. गावातील आपले सरकार / CSC केंद्र",
        "where_csc_desc": "ग्रामपंचायत किंवा ग्राहक सेवा केंद्रात ऑनलाइन अर्ज करा.",
        "safety_alert": "सावधान ताई: ही योजना १००% मोफत आहे. कोणत्याही दलालाला एक रुपयाही देऊ नका!",
        "ineligible_text": "उज्ज्वला २.० नवीन कनेक्शनसाठी आहे. रेशन कार्ड नसल्यास आधी ग्रामपंचायतीतून रेशन कार्ड बनवा.",
        "btn_start": "पात्रता तपासा (सुरू करा)",
        "btn_to_where": "कुठे जायचे? पहा 👉",
        "btn_restart": "🔄 पुन्हा सुरू करा",
        "btn_retry": "🔄 पुन्हा तपासा",
        "btn_demo": "१-क्लिक डेमो चालवा",
        "mic_tap": "माइक दाबून बोला",
        "mic_listening": "ऐकत आहे... बोला ताई"
    },
    "gu": {
        "app_title": "ડિજિટલ દીદી",
        "app_subtitle": "ઉજ્જ્વલા દીદી • મફત ગેસ યોજના સહાયક",
        "didi_greeting": "નમસ્તે બહેન! હું તમારી ડિજિટલ દીદી છું. શું તમારે મફત ગેસ ચૂલો અને સિલિન્ડર જોઈએ છે?",
        "scheme_name": "પ્રધાનમંત્રી ઉજ્જ્વલા યોજના ૨.૦",
        "scheme_tagline": "ગ્રામીણ બહેનો માટે ધુમાડા મુક્ત રસોડું અને મફત ગેસ સિલિન્ડર!",
        "benefits": [
            {"title": "પ્રથમ સિલિન્ડર મફત", "desc": "૧૪.૨ કિલોનો ભરેલો ગેસ સિલિન્ડર મફત.", "badge": "મફત"},
            {"title": "૨ બર્નર ગેસ ચૂલો", "desc": "સુરક્ષિત બે બર્નર વાળો નવો ચૂલો મફત.", "badge": "મફત"},
            {"title": "₹૦ ડિપોઝિટ", "desc": "કોઈ સિક્યોરિટી ડિપોઝિટ કે દલાલી આપવાની નથી.", "badge": "₹૦ ફી"}
        ],
        "q1_text": "બહેન, શું તમારા ઘરમાં પહેલેથી કોઈ ગેસ સિલિન્ડર છે?",
        "q1_hint": "નીચેના બે મોટા બટનોમાંથી એક પસંદ કરો:",
        "q1_no": "ના, ગેસ કનેક્શન નથી",
        "q1_no_desc": "અમે ચૂલા પર લાકડાથી રસોઈ બનાવીએ છીએ",
        "q1_yes": "હા, ગેસ પહેલેથી છે",
        "q1_yes_desc": "ઘરમાં પહેલેથી જ સિલિન્ડર છે",
        "q2_text": "શું તમારી પાસે રેશનકાર્ડ છે?",
        "q2_hint": "જેમાં પરિવારના સભ્યોના નામ લખેલા હોય:",
        "q2_yes": "હા, રેશનકાર્ડ છે",
        "q2_yes_desc": "અમારી પાસે રેશનકાર્ડ છે",
        "q2_no": "ના, રેશનકાર્ડ નથી",
        "q2_no_desc": "રેશનકાર્ડ હજુ સુધી બન્યું નથી",
        "congrats_title": "અભિનંદન બહેન! તમે પાત્ર છો",
        "congrats_desc": "તમને મફત ગેસ ચૂલો અને સિલિન્ડર મળશે.",
        "docs_heading": "📋 ફક્ત આ ૩ કાગળો તૈયાર રાખો:",
        "docs_hint": "(અવાજ સાંભળવા માટે કોઈપણ કાર્ડ પર અડો)",
        "doc_aadhaar_title": "આધાર કાર્ડ",
        "doc_aadhaar_desc": "મહિલાનું પોતાનું આધાર કાર્ડ.",
        "doc_aadhaar_audio": "પહેલો કાગળ: તમારું આધાર કાર્ડ.",
        "doc_ration_title": "રેશન કાર્ડ",
        "doc_ration_desc": "પરિવારના સભ્યોના નામ વાળું રેશન કાર્ડ.",
        "doc_ration_audio": "બીજો કાગળ: તમારું રેશન કાર્ડ.",
        "doc_passbook_title": "બેંક પાસબુક",
        "doc_passbook_desc": "મહિલાના નામનું બેંક ખાતું અથવા જનધન ખાતું.",
        "doc_passbook_audio": "ત્રીજો કાગળ: બેંક પાસબુકની પ્રથમ પાનાની નકલ.",
        "where_title": "📍 આ કાગળો લઈને અહીં જાઓ:",
        "where_agency_title": "૧. નજીકની ગેસ એજન્સી",
        "where_agency_desc": "ઇન્ડેન, ભારત ગેસ અથવા એચપી ગેસ એજન્સી પર જાઓ.",
        "where_csc_title": "૨. ગામનું ઈ-ગ્રામ / જન સેવા કેન્દ્ર",
        "where_csc_desc": "પંચાયત ભવન કે સીએસસી કેન્દ્ર પર ફોર્મ ભરાવો.",
        "safety_alert": "સાવધાન: આ યોજના ૧૦૦% મફત છે. કોઈ પણ વચેટિયાને એક પણ રૂપિયો આપશો નહીં!",
        "ineligible_text": "ઉજ્જ્વલા ૨.૦ નવા કનેક્શન માટે છે. જો રેશનકાર્ડ ન હોય તો પહેલા પંચાયતમાંથી કઢાવો.",
        "btn_start": "પાત્રતા તપાસો (શરૂ કરો)",
        "btn_to_where": "ક્યાં જવું? જુઓ 👉",
        "btn_restart": "🔄 ફરીથી શરૂ કરો",
        "btn_retry": "🔄 ફરી તપાસો",
        "btn_demo": "૧-ક્લિક ડેમો ચલાવો",
        "mic_tap": "માઈક દબાવીને બોલો",
        "mic_listening": "સાંભળી રહી છું... બોલો બહેન"
    },
    "kn": {
        "app_title": "ಡಿಜಿಟಲ್ ದೀದಿ",
        "app_subtitle": "ಉಜ್ವಲ ದೀದಿ • ಉಚಿತ ಗ್ಯಾಸ್ ಯೋಜನೆ ಮಾರ್ಗದರ್ಶಿ",
        "didi_greeting": "ನಮಸ್ಕಾರ ಅಕ್ಕ! ನಾನು ನಿಮ್ಮ ಡಿಜಿಟಲ್ ದೀದಿ. ನಿಮ್ಮ ಮನೆಗೆ ಉಚಿತ ಗ್ಯಾಸ್ ಒಲೆ ಮತ್ತು ಸಿಲಿಂಡರ್ ಬೇಕೇ?",
        "scheme_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಉಜ್ವಲ ಯೋಜನೆ ೨.೦",
        "scheme_tagline": "ಗ್ರಾಮೀಣ ಮಹಿಳೆಯರಿಗೆ ಹೊಗೆ ರಹಿತ ಒಲೆ ಮತ್ತು ಉಚಿತ ಗ್ಯಾಸ್ ಸಿಲಿಂಡರ್!",
        "benefits": [
            {"title": "ಮೊದಲ ಸಿಲಿಂಡರ್ ಉಚಿತ", "desc": "೧೪.೨ ಕೆಜಿ ತೂಕದ ಮೊದಲ ಸಿಲಿಂಡರ್ ಸಂಪೂರ್ಣ ಉಚಿತ.", "badge": "ಉಚಿತ"},
            {"title": "೨ ಬರ್ನರ್ ಗ್ಯಾಸ್ ಒಲೆ", "desc": "ಸುರಕ್ಷಿತ ಡಬಲ್ ಬರ್ನರ್ ಒಲೆ ಉಚಿತವಾಗಿ ಲಭ್ಯ.", "badge": "ಉಚಿತ"},
            {"title": "₹೦ ಠೇವಣಿ", "desc": "ಯಾವುದೇ ಸೆಕ್ಯೂರಿಟಿ ಠೇವಣಿ ಅಥವಾ ದಲ್ಲಾಳಿ ಇಲ್ಲ.", "badge": "₹೦ ಶುಲ್ಕ"}
        ],
        "q1_text": "ಅಕ್ಕ, ನಿಮ್ಮ ಮನೆಯಲ್ಲಿ ಈಗಾಗಲೇ ಗ್ಯಾಸ್ ಸಂಪರ್ಕವಿದೆಯೇ?",
        "q1_hint": "ಕೆಳಗಿನ ಎರಡು ದೊಡ್ಡ ಬಟನ್‌ಗಳಲ್ಲಿ ಒಂದನ್ನು ಮುಟ್ಟಿ:",
        "q1_no": "ಇಲ್ಲ, ಗ್ಯಾಸ್ ಸಂಪರ್ಕವಿಲ್ಲ",
        "q1_no_desc": "ನಾವು ಕಟ್ಟಿಗೆ ಒಲೆಯಲ್ಲಿ ಅಡುಗೆ ಮಾಡುತ್ತೇವೆ",
        "q1_yes": "ಹೌದು, ಗ್ಯಾಸ್ ಇದೆ",
        "q1_yes_desc": "ಮನೆಯಲ್ಲಿ ಈಗಾಗಲೇ ಸಿಲಿಂಡರ್ ಇದೆ",
        "q2_text": "ನಿಮ್ಮ ಬಳಿ ರೇಷನ್ ಕಾರ್ಡ್ ಇದೆಯೇ?",
        "q2_hint": "ಕುಟುಂಬದ ಸದಸ್ಯರ ಹೆಸರುಗಳಿರುವ ಕಾರ್ಡ್:",
        "q2_yes": "ಹೌದು, ರೇಷನ್ ಕಾರ್ಡ್ ಇದೆ",
        "q2_yes_desc": "ನಮ್ಮ ಬಳಿ ಕುಟುಂಬದ ರೇಷನ್ ಕಾರ್ಡ್ ಇದೆ",
        "q2_no": "ಇಲ್ಲ, ರೇಷನ್ ಕಾರ್ಡ್ ಇಲ್ಲ",
        "q2_no_desc": "ರೇಷನ್ ಕಾರ್ಡ್ ಇನ್ನೂ ಮಾಡಿಸಿಲ್ಲ",
        "congrats_title": "ಅಭಿನಂದನೆಗಳು ಅಕ್ಕ! ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ",
        "congrats_desc": "ನಿಮಗೆ ಉಚಿತ ಗ್ಯಾಸ್ ಒಲೆ ಮತ್ತು ಸಿಲಿಂಡರ್ ದೊರೆಯುತ್ತದೆ.",
        "docs_heading": "📋 ಈ ೩ ದಾಖಲೆಗಳನ್ನು ಮಾತ್ರ ಸಿದ್ಧವಾಗಿಡಿ:",
        "docs_hint": "(ಧ್ವನಿ ಕೇಳಲು ಯಾವುದೇ ಕಾರ್ಡ್ ಮೇಲೆ ಮುಟ್ಟಿ)",
        "doc_aadhaar_title": "ಆಧಾರ್ ಕಾರ್ಡ್",
        "doc_aadhaar_desc": "ಮಹಿಳೆಯ ಸ್ವಂತ ಆಧಾರ್ ಕಾರ್ಡ್ ಜೆರಾಕ್ಸ್.",
        "doc_aadhaar_audio": "ಮೊದಲ ದಾಖಲೆ: ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್.",
        "doc_ration_title": "ರೇಷನ್ ಕಾರ್ಡ್",
        "doc_ration_desc": "ಕುಟುಂಬದ ಸದಸ್ಯರ ಹೆಸರುಗಳಿರುವ ರೇಷನ್ ಕಾರ್ಡ್.",
        "doc_ration_audio": "ಎರಡನೇ ದಾಖಲೆ: ನಿಮ್ಮ ರೇಷನ್ ಕಾರ್ಡ್.",
        "doc_passbook_title": "ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್",
        "doc_passbook_desc": "ಮಹಿಳೆಯ ಹೆಸರಿನ ಬ್ಯಾಂಕ್ ಖಾತೆ ಪಾಸ್‌ಬುಕ್.",
        "doc_passbook_audio": "ಮೂರನೇ ದಾಖಲೆ: ಬ್ಯಾಂಕ್ ಖಾತೆ ಪಾಸ್‌ಬುಕ್ ಮುಖಪುಟ ಜೆರಾಕ್ಸ್.",
        "where_title": "📍 ಈ ದಾಖಲೆಗಳೊಂದಿಗೆ ಇಲ್ಲಿಗೆ ಹೋಗಿ:",
        "where_agency_title": "೧. ಹತ್ತಿರದ ಗ್ಯಾಸ್ ಏಜೆನ್ಸಿ",
        "where_agency_desc": "ಇಂಡೇನ್, ಭಾರತ್ ಗ್ಯಾಸ್ ಅಥವಾ ಎಚ್‌ಪಿ ಗ್ಯಾಸ್ ಏಜೆನ್ಸಿಗೆ ಭೇಟಿ ನೀಡಿ.",
        "where_csc_title": "೨. ಗ್ರಾಮ ಒನ್ / CSC ಕೇಂದ್ರ",
        "where_csc_desc": "ಗ್ರಾಮ ಪಂಚಾಯತ್ ಅಥವಾ ಸೇವಾ ಕೇಂದ್ರದಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.",
        "safety_alert": "ಎಚ್ಚರಿಕೆ: ಈ ಯೋಜನೆ ೧೦೦% ಉಚಿತ. ಯಾವುದೇ ಮಧ್ಯವರ್ತಿಗಳಿಗೆ ಹಣ ನೀಡಬೇಡಿ!",
        "ineligible_text": "ಉಜ್ವಲ ೨.೦ ಹೊಸ ಸಂಪರ್ಕಗಳಿಗಾಗಿ ಮಾತ್ರ. ರೇಷನ್ ಕಾರ್ಡ್ ಇಲ್ಲದಿದ್ದರೆ ಮೊದಲು ಮಾಡಿಸಿಕೊಳ್ಳಿ.",
        "btn_start": "ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ (ಪ್ರಾರಂಭಿಸಿ)",
        "btn_to_where": "ಎಲ್ಲಿಗೆ ಹೋಗಬೇಕು? ನೋಡಿ 👉",
        "btn_restart": "🔄 ಪುನಃ ಪ್ರಾರಂಭಿಸಿ",
        "btn_retry": "🔄 ಮತ್ತೆ ಪರಿಶೀಲಿಸಿ",
        "btn_demo": "೧-ಕ್ಲಿಕ್ ಡೆಮೊ ಚಾಲನೆ ಮಾಡಿ",
        "mic_tap": "ಮೈಕ್ ಒತ್ತಿ ಮಾತನಾಡಿ",
        "mic_listening": "ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ... ಮಾತನಾಡಿ ಅಕ್ಕ"
    },
    "ml": {
        "app_title": "ഡിജിറ്റൽ ദീദി",
        "app_subtitle": "ഉജ്ജ്വല ദീദി • സൗജന്യ ഗ്യാസ് പദ്ധതി സഹായി",
        "didi_greeting": "നമസ്കാരം ചേച്ചി! ഞാൻ നിങ്ങളുടെ ഡിജിറ്റൽ ദീദിയാണ്. നിങ്ങളുടെ വീട്ടിലേക്ക് സൗജന്യ ഗ്യാസ് അടുപ്പും സിലിണ്ടറും വേണമെന്നുണ്ടോ?",
        "scheme_name": "പ്രധാനമന്ത്രി ഉജ്ജ്വല യോജന 2.0",
        "scheme_tagline": "ഗ്രാമീണ സ്ത്രീകൾക്ക് പുകയില്ലാത്ത അടുപ്പും സൗജന്യ സിലിണ്ടറും!",
        "benefits": [
            {"title": "ആദ്യ സിലിണ്ടർ സൗജന്യം", "desc": "14.2 കിലോ സിലിണ്ടർ പൂർണ്ണമായും സൗജന്യമാണ്.", "badge": "സൗജന്യം"},
            {"title": "2 ബർണർ ഗ്യാസ് അടുപ്പ്", "desc": "സുരക്ഷിതമായ രണ്ട് ബർണർ അടുപ്പ് സൗജന്യമായി ലഭിക്കുന്നു.", "badge": "സൗജന്യം"},
            {"title": "₹0 ഡെപ്പോസിറ്റ്", "desc": "യാതൊരു ഫീസോ കൈക്കൂലിയോ നൽകേണ്ടതില്ല.", "badge": "₹0 ഫീസ്"}
        ],
        "q1_text": "ചേച്ചി, നിങ്ങളുടെ വീട്ടിൽ നിലവിൽ ഗ്യാസ് കണക്ഷൻ ഉണ്ടോ?",
        "q1_hint": "താഴെയുള്ള രണ്ട് വലിയ ബട്ടണുകളിൽ ഒന്നിൽ തൊടുക:",
        "q1_no": "ഇല്ല, ഗ്യാസ് കണക്ഷൻ ഇല്ല",
        "q1_no_desc": "വിറക് അടുപ്പിലാണ് ഭക്ഷണം പാകം ചെയ്യുന്നത്",
        "q1_yes": "ഉണ്ട്, ഗ്യാസ് ഉണ്ട്",
        "q1_yes_desc": "വീട്ടിൽ നിലവിൽ സിലിണ്ടർ ഉണ്ട്",
        "q2_text": "നിങ്ങളുടെ പക്കൽ റേഷൻ കാർഡ് ഉണ്ടോ?",
        "q2_hint": "കുടുംബാംഗങ്ങളുടെ പേരുള്ള റേഷൻ കാർഡ്:",
        "q2_yes": "ഉണ്ട്, റേഷൻ കാർഡ് ഉണ്ട്",
        "q2_yes_desc": "കുടുംബ റേഷൻ കാർഡ് ഞങ്ങളുടെ പക്കലുണ്ട്",
        "q2_no": "ഇല്ല, റേഷൻ കാർഡ് ഇല്ല",
        "q2_no_desc": "റേഷൻ കാർഡ് ഇതുവരെ ലഭിച്ചിട്ടില്ല",
        "congrats_title": "അഭിനന്ദനങ്ങൾ ചേച്ചി! നിങ്ങൾ അർഹയാണ്",
        "congrats_desc": "നിങ്ങൾക്ക് സൗജന്യ ഗ്യാസ് അടുപ്പും സിലിണ്ടറും ലഭിക്കും.",
        "docs_heading": "📋 ഈ 3 രേഖകൾ മാത്രം തയ്യാറാക്കുക:",
        "docs_hint": "(ശബ്ദം കേൾക്കാൻ ഏതെങ്കിലും കാർഡിൽ തൊടുക)",
        "doc_aadhaar_title": "ആധാർ കാർഡ്",
        "doc_aadhaar_desc": "സ്ത്രീയുടെ സ്വന്തം ആധാർ കാർഡ്.",
        "doc_aadhaar_audio": "ആദ്യ രേഖ: നിങ്ങളുടെ ആധാർ കാർഡ്.",
        "doc_ration_title": "റേഷൻ കാർഡ്",
        "doc_ration_desc": "കുടുംബാംഗങ്ങളുടെ പേരുള്ള റേഷൻ കാർഡ്.",
        "doc_ration_audio": "രണ്ടാമത്തെ രേഖ: നിങ്ങളുടെ റേഷൻ കാർഡ്.",
        "doc_passbook_title": "ബാങ്ക് പാസ്ബുക്ക്",
        "doc_passbook_desc": "സ്ത്രീയുടെ പേരിലുള്ള ബാങ്ക് അക്കൗണ്ട് പാസ്ബുക്ക്.",
        "doc_passbook_audio": "മൂന്നാമത്തെ രേഖ: ബാങ്ക് അക്കൗണ്ട് പാസ്ബുക്ക് ആദ്യ പേജ് കോപ്പി.",
        "where_title": "📍 ഈ രേഖകളുമായി ഇവിടെ പോകുക:",
        "where_agency_title": "1. അടുത്തുള്ള ഗ്യാസ് ഏജൻസി",
        "where_agency_desc": "ഇൻഡെയ്ൻ, ഭാരത് ഗ്യാസ് അല്ലെങ്കിൽ എച്ച്പി ഗ്യാസ് ഏജൻസിയിൽ നേരിട്ട് പോകുക.",
        "where_csc_title": "2. അക്ഷയ കേന്ദ്രം / CSC സെന്റർ",
        "where_csc_desc": "അക്ഷയ കേന്ദ്രത്തിലോ ജനസേവന കേന്ദ്രത്തിലോ അപേക്ഷിക്കാം.",
        "safety_alert": "ശ്രദ്ധിക്കുക: ഈ പദ്ധതി 100% സൗജന്യമാണ്. ആർക്കും പണം നൽകരുത്!",
        "ineligible_text": "ഉജ്ജ്വല 2.0 പുതിയ കണക്ഷനുകൾക്ക് മാത്രമാണ്. റേഷൻ കാർഡില്ലെങ്കിൽ ആദ്യം കാർഡ് എടുക്കുക.",
        "btn_start": "അർഹത പരിശോധിക്കുക (തുടങ്ങുക)",
        "btn_to_where": "എവിടെ പോകണം? കാണുക 👉",
        "btn_restart": "🔄 വീണ്ടും തുടങ്ങുക",
        "btn_retry": "🔄 വീണ്ടും പരിശോധിക്കുക",
        "btn_demo": "1-ക്ലിക്ക് ഡെമോ കാണുക",
        "mic_tap": "മൈക്ക് അമർത്തി സംസാരിക്കുക",
        "mic_listening": "കേൾക്കുന്നു... പറയൂ ചേച്ചി"
    },
    "pa": {
        "app_title": "ਡਿਜੀਟਲ ਦੀਦੀ",
        "app_subtitle": "ਉੱਜਵਲਾ ਦੀਦੀ • ਮੁਫ਼ਤ ਗੈਸ ਸਕੀਮ ਮਾਰਗਦਰਸ਼ਕ",
        "didi_greeting": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਭੈਣ ਜੀ! ਮੈਂ ਤੁਹਾਡੀ ਡਿਜੀਟਲ ਦੀਦੀ ਹਾਂ। ਕੀ ਤੁਹਾਨੂੰ ਘਰ ਲਈ ਮੁਫ਼ਤ ਗੈਸ ਚੁੱਲ੍ਹਾ ਅਤੇ ਸਿਲੰਡਰ ਚਾਹੀਦਾ ਹੈ?",
        "scheme_name": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਉੱਜਵਲਾ ਯੋਜਨਾ 2.0",
        "scheme_tagline": "ਪਿੰਡ ਦੀ ਹਰ ਭੈਣ ਲਈ ਧੂੰਏਂ-ਮੁਕਤ ਚੁੱਲ੍ਹਾ ਅਤੇ ਮੁਫ਼ਤ ਸਿਲੰਡਰ!",
        "benefits": [
            {"title": "ਪਹਿਲਾ ਸਿਲੰਡਰ ਮੁਫ਼ਤ", "desc": "14.2 ਕਿਲੋ ਦਾ ਭਰਿਆ ਹੋਇਆ ਪਹਿਲਾ ਸਿਲੰਡਰ ਮੁਫ਼ਤ।", "badge": "ਮੁਫ਼ਤ"},
            {"title": "2 ਬਰਨਰ ਗੈਸ ਚੁੱਲ੍ਹਾ", "desc": "ਸੁਰੱਖਿਅਤ ਦੋ ਬਰਨਰਾਂ ਵਾਲਾ ਨਵਾਂ ਚੁੱਲ੍ਹਾ ਮੁਫ਼ਤ।", "badge": "ਮੁਫ਼ਤ"},
            {"title": "₹0 ਸਕਿਓਰਿਟੀ ਫ਼ੀਸ", "desc": "ਕੋਈ ਸਕਿਓਰਿਟੀ ਜਾਂ ਦਲਾਲੀ ਨਹੀਂ ਦੇਣੀ।", "badge": "₹0 ਫ਼ੀਸ"}
        ],
        "q1_text": "ਭੈਣ ਜੀ, ਕੀ ਤੁਹਾਡੇ ਘਰ ਵਿੱਚ ਪਹਿਲਾਂ ਤੋਂ ਕੋਈ ਗੈਸ ਕੁਨੈਕਸ਼ਨ ਹੈ?",
        "q1_hint": "ਹੇਠਾਂ ਦਿੱਤੇ ਦੋ ਵੱਡੇ ਬਟਨਾਂ ਵਿੱਚੋਂ ਇੱਕ ਨੂੰ ਛੂਹੋ:",
        "q1_no": "ਨਹੀਂ, ਕੋਈ ਗੈਸ ਨਹੀਂ ਹੈ",
        "q1_no_desc": "ਲੱਕੜ ਜਾਂ ਚੁੱਲ੍ਹੇ 'ਤੇ ਰੋਟੀ ਬਣਾਉਂਦੇ ਹਾਂ",
        "q1_yes": "ਹਾਂ, ਗੈਸ ਪਹਿਲਾਂ ਤੋਂ ਹੈ",
        "q1_yes_desc": "ਘਰ ਵਿੱਚ ਪਹਿਲਾਂ ਹੀ ਸਿਲੰਡਰ ਹੈ",
        "q2_text": "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਰਾਸ਼ਨ ਕਾਰਡ ਹੈ?",
        "q2_hint": "ਜਿਸ ਵਿੱਚ ਪਰਿਵਾਰ ਦੇ ਮੈਂਬਰਾਂ ਦੇ ਨਾਮ ਲਿਖੇ ਹਨ:",
        "q2_yes": "ਹਾਂ, ਰਾਸ਼ਨ ਕਾਰਡ ਹੈ",
        "q2_yes_desc": "ਸਾਡੇ ਕੋਲ ਪਰਿਵਾਰ ਦਾ ਰਾਸ਼ਨ ਕਾਰਡ ਹੈ",
        "q2_no": "ਨਹੀਂ, ਰਾਸ਼ਨ ਕਾਰਡ ਨਹੀਂ ਹੈ",
        "q2_no_desc": "ਰਾਸ਼ਨ ਕਾਰਡ ਅਜੇ ਤੱਕ ਨਹੀਂ ਬਣਿਆ",
        "congrats_title": "ਵਧਾਈ ਹੋਵੇ ਭੈਣ ਜੀ! ਤੁਸੀਂ ਯੋਗ ਹੋ",
        "congrats_desc": "ਤੁਹਾਨੂੰ ਮੁਫ਼ਤ ਗੈਸ ਚੁੱਲ੍ਹਾ ਅਤੇ ਸਿਲੰਡਰ ਮਿਲੇਗਾ।",
        "docs_heading": "📋 ਸਿਰਫ਼ ਇਹ 3 ਕਾਗਜ਼ ਤਿਆਰ ਰੱਖੋ:",
        "docs_hint": "(ਆਵਾਜ਼ ਸੁਣਨ ਲਈ ਕਿਸੇ ਵੀ ਕਾਰਡ 'ਤੇ ਟੈਪ ਕਰੋ)",
        "doc_aadhaar_title": "ਆਧਾਰ ਕਾਰਡ",
        "doc_aadhaar_desc": "ਮਹਿਲਾ ਦਾ ਆਪਣਾ ਆਧਾਰ ਕਾਰਡ।",
        "doc_aadhaar_audio": "ਪਹਿਲਾ ਕਾਗਜ਼: ਤੁਹਾਡਾ ਆਧਾਰ ਕਾਰਡ।",
        "doc_ration_title": "ਰਾਸ਼ਨ ਕਾਰਡ",
        "doc_ration_desc": "ਪਰਿਵਾਰ ਦੇ ਮੈਂਬਰਾਂ ਦੇ ਨਾਵਾਂ ਵਾਲਾ ਰਾਸ਼ਨ ਕਾਰਡ।",
        "doc_ration_audio": "ਦੂਜਾ ਕਾਗਜ਼: ਤੁਹਾਡਾ ਰਾਸ਼ਨ ਕਾਰਡ।",
        "doc_passbook_title": "ਬੈਂਕ ਪਾਸਬੁੱਕ",
        "doc_passbook_desc": "ਮਹਿਲਾ ਦੇ ਨਾਮ ਦਾ ਬੈਂਕ ਖਾਤਾ।",
        "doc_passbook_audio": "ਤੀਜਾ ਕਾਗਜ਼: ਬੈਂਕ ਖਾਤੇ ਦੀ ਪਾਸਬੁੱਕ ਦੀ ਕਾਪੀ।",
        "where_title": "📍 ਇਹ ਕਾਗਜ਼ ਲੈ ਕੇ ਇੱਥੇ ਜਾਓ:",
        "where_agency_title": "1. ਨੇੜਲੀ ਗੈਸ ਏਜੰਸੀ",
        "where_agency_desc": "ਇੰਡੇਨ, ਭਾਰਤ ਗੈਸ ਜਾਂ ਐਚਪੀ ਗੈਸ ਏਜੰਸੀ 'ਤੇ ਜਾਓ।",
        "where_csc_title": "2. ਪਿੰਡ ਦਾ ਸੇਵਾ ਕੇਂਦਰ (CSC)",
        "where_csc_desc": "ਪਿੰਡ ਦੇ ਸੁਵਿਧਾ ਜਾਂ ਸੇਵਾ ਕੇਂਦਰ ਤੋਂ ਫ਼ਾਰਮ ਭਰਵਾਓ।",
        "safety_alert": "ਸਾਵਧਾਨੀ: ਇਹ ਸਕੀਮ 100% ਮੁਫ਼ਤ ਹੈ। ਕਿਸੇ ਵਿਚੋਲੇ ਨੂੰ ਪੈਸੇ ਨਾ ਦਿਓ!",
        "ineligible_text": "ਉੱਜਵਲਾ 2.0 ਨਵੇਂ ਕੁਨੈਕਸ਼ਨਾਂ ਲਈ ਹੈ। ਜੇ ਰਾਸ਼ਨ ਕਾਰਡ ਨਹੀਂ ਹੈ ਤਾਂ ਪਹਿਲਾਂ ਬਣਵਾਓ।",
        "btn_start": "ਯੋਗਤਾ ਚੈੱਕ ਕਰੋ (ਸ਼ੁਰੂ ਕਰੋ)",
        "btn_to_where": "ਕਿੱਥੇ ਜਾਣਾ ਹੈ? ਵੇਖੋ 👉",
        "btn_restart": "🔄 ਦੁਬਾਰਾ ਸ਼ੁਰੂ ਕਰੋ",
        "btn_retry": "🔄 ਮੁੜ ਚੈੱਕ ਕਰੋ",
        "btn_demo": "1-ਕਲਿੱਕ ਡੈਮੋ ਚਲਾਓ",
        "mic_tap": "ਮਾਈਕ ਦਬਾ ਕੇ ਬੋਲੋ",
        "mic_listening": "ਸੁਣ ਰਹੀ ਹਾਂ... ਬੋਲੋ ਭੈਣ ਜੀ"
    },
    "or": {
        "app_title": "ଡିଜିଟାଲ୍ ଦିଦି",
        "app_subtitle": "ଉଜ୍ଜ୍ୱଳା ଦିଦି • ମାଗଣା ଗ୍ୟାସ୍ ଯୋଜନା ସାଥୀ",
        "didi_greeting": "ନମସ୍କାର ଭଉଣୀ! ମୁଁ ଆପଣଙ୍କର ଡିଜିଟାଲ୍ ଦିଦି। ଆପଣଙ୍କୁ କ'ଣ ମାଗଣା ଗ୍ୟାସ୍ ଚୁଲା ଏବଂ ସିଲିଣ୍ଡର ଦରକାର?",
        "scheme_name": "ପ୍ରଧାନମନ୍ତ୍ରୀ ଉଜ୍ଜ୍ୱଳା ଯୋଜନା ୨.୦",
        "scheme_tagline": "ଗାଁର ପ୍ରତ୍ୟେକ ଭଉଣୀଙ୍କ ପାଇଁ ଧୂଆଁମୁକ୍ତ ଚୁଲା ଓ ମାଗଣା ସିଲିଣ୍ଡର!",
        "benefits": [
            {"title": "ପ୍ରଥମ ସିଲିଣ୍ଡର ମାଗଣା", "desc": "୧୪.୨ କେଜି ପ୍ରଥମ ପୂର୍ଣ୍ଣ ସିଲିଣ୍ଡର ସମ୍ପୂର୍ଣ୍ଣ ମାଗଣା।", "badge": "ମାଗଣା"},
            {"title": "୨ ବର୍ଣ୍ଣର ଗ୍ୟାସ୍ ଚୁଲା", "desc": "ନୂଆ ଦୁଇ ବର୍ଣ୍ଣର ଚୁଲା ମାଗଣାରେ ମିଳିବ।", "badge": "ମାଗଣା"},
            {"title": "₹୦ ଡିପୋଜିଟ୍", "desc": "କୌଣସି ଫିସ୍ ବା ଦଲାଲି ଦେବାକୁ ପଡ଼ିବ ନାହିଁ।", "badge": "₹୦ ଫିସ୍"}
        ],
        "q1_text": "ଭଉଣୀ, ଆପଣଙ୍କ ଘରେ ପୂର୍ବରୁ କୌଣସି ଗ୍ୟାସ୍ ସଂଯୋଗ ଅଛି କି?",
        "q1_hint": "ତଳେ ଦିଆଯାଇଥିବା ଦୁଇଟି ବଡ଼ ବଟନ୍ ମଧ୍ୟରୁ ଗୋଟିକୁ ଛୁଅନ୍ତୁ:",
        "q1_no": "ନାହିଁ, ଗ୍ୟାସ୍ ସଂଯୋଗ ନାହିଁ",
        "q1_no_desc": "ଆମେ କାଠ ବା ଚୁଲାରେ ରୋଷେଇ କରୁ",
        "q1_yes": "ହଁ, ପୂର୍ବରୁ ଗ୍ୟାସ୍ ଅଛି",
        "q1_yes_desc": "ଘରେ ପୂର୍ବରୁ ସିଲିଣ୍ଡର ଅଛି",
        "q2_text": "ଆପଣଙ୍କ ପାଖରେ ରାସନ୍ କାର୍ଡ ଅଛି କି?",
        "q2_hint": "ଯେଉଁଥିରେ ପରିବାରର ସଦସ୍ୟଙ୍କ ନାମ ଲେଖାଅଛି:",
        "q2_yes": "ହଁ, ରାସନ୍ କାର୍ଡ ଅଛି",
        "q2_yes_desc": "ଆମ ପାଖରେ ପରିବାରର ରାସନ୍ କାର୍ଡ ଅଛି",
        "q2_no": "ନାହିଁ, ରାସନ୍ କାର୍ଡ ନାହିଁ",
        "q2_no_desc": "ରାସନ୍ କାର୍ଡ ଏପର୍ଯ୍ୟନ୍ତ ହୋଇନାହିଁ",
        "congrats_title": "ଅଭିନନ୍ଦନ ଭଉଣୀ! ଆପଣ ଯୋଗ୍ୟ ଅଟନ୍ତି",
        "congrats_desc": "ଆପଣଙ୍କୁ ମାଗଣା ଗ୍ୟାସ୍ ଚୁଲା ଓ ସିଲିଣ୍ଡର ମିଳିବ।",
        "docs_heading": "📋 କେବଳ ଏହି ୩ଟି କାଗଜପତ୍ର ପ୍ରସ୍ତୁତ ରଖନ୍ତୁ:",
        "docs_hint": "(ଶବ୍ଦ ଶୁଣିବା ପାଇଁ ଯେକୌଣସି କାର୍ଡ ଉପରେ ଟ୍ୟାପ୍ କରନ୍ତୁ)",
        "doc_aadhaar_title": "ଆଧାର କାର୍ଡ",
        "doc_aadhaar_desc": "ମହିଳାଙ୍କ ନିଜର ଆଧାର କାର୍ଡ।",
        "doc_aadhaar_audio": "ପ୍ରଥମ କାଗଜ: ଆପଣଙ୍କ ଆଧାର କାର୍ଡ।",
        "doc_ration_title": "ରାସନ୍ କାର୍ଡ",
        "doc_ration_desc": "ପରିବାରର ସଦସ୍ୟଙ୍କ ନାମ ଥିବା ରାସନ୍ କାର୍ଡ।",
        "doc_ration_audio": "ଦ୍ୱିତୀୟ କାଗଜ: ଆପଣଙ୍କ ରାସନ୍ କାର୍ଡ।",
        "doc_passbook_title": "ବ୍ୟାଙ୍କ ପାସବୁକ୍",
        "doc_passbook_desc": "ମହିଳାଙ୍କ ନାମରେ ବ୍ୟାଙ୍କ ଖାତା।",
        "doc_passbook_audio": "ତୃତୀୟ କାଗଜ: ବ୍ୟାଙ୍କ ପାସବୁକ୍ ପ୍ରଥମ ପୃଷ୍ଠା ଜେରକ୍ସ।",
        "where_title": "📍 ଏହି କାଗଜପତ୍ର ନେଇ ଏଠାକୁ ଯାଆନ୍ତୁ:",
        "where_agency_title": "୧. ନିକଟସ୍ଥ ଗ୍ୟାସ୍ ଏଜେନ୍ସି",
        "where_agency_desc": "ଇଣ୍ଡେନ୍, ଭାରତ ଗ୍ୟାସ୍ କିମ୍ବା ଏଚପି ଗ୍ୟାସ୍ ଦୋକାନକୁ ଯାଆନ୍ତୁ।",
        "where_csc_title": "୨. ଜନସେବା କେନ୍ଦ୍ର (CSC କେନ୍ଦ୍ର)",
        "where_csc_desc": "ଗାଁର ପଞ୍ଚାୟତ ବା ସେବା କେନ୍ଦ୍ରରେ ଆବେଦନ କରନ୍ତୁ।",
        "safety_alert": "ସତର୍କତା: ଏହି ଯୋଜନା ସମ୍ପୂର୍ଣ୍ଣ ମାଗଣା। କାହାକୁ କୌଣସି ଟଙ୍କା ଦିଅନ୍ତୁ ନାହିଁ!",
        "ineligible_text": "ଉଜ୍ଜ୍ୱଳା ୨.୦ ନୂଆ ସଂଯୋଗ ପାଇଁ। ରାସନ୍ କାର୍ଡ ନଥିଲେ ପଞ୍ଚାୟତରୁ ପ୍ରଥମେ ବନାନ୍ତୁ।",
        "btn_start": "ଯୋଗ୍ୟତା ଯାଞ୍ଚ କରନ୍ତୁ (ଆରମ୍ଭ)",
        "btn_to_where": "କେଉଁଠାକୁ ଯିବେ? ଦେଖନ୍ତୁ 👉",
        "btn_restart": "🔄 ପୁନର୍ବାର ଆରମ୍ଭ କରନ୍ତୁ",
        "btn_retry": "🔄 ପୁଣି ଯାଞ୍ଚ କରନ୍ତୁ",
        "btn_demo": "୧-କ୍ଲିକ୍ ଡେମୋ ଚଲାନ୍ତୁ",
        "mic_tap": "ମାଇକ୍ ଦବାଇ କୁହନ୍ତୁ",
        "mic_listening": "ଶୁଣୁଛି... କୁହନ୍ତୁ ଭଉଣୀ"
    },
    "en": {
        "app_title": "Digital Didi",
        "app_subtitle": "Ujjwala Didi • Free Gas Scheme Guide",
        "didi_greeting": "Hello sister! I am your Digital Didi. Would you like a free gas stove and cylinder for your home?",
        "scheme_name": "PM Ujjwala Yojana 2.0",
        "scheme_tagline": "Safe smoke-free stove and free gas cylinder for rural women!",
        "benefits": [
            {"title": "1st Cylinder Free", "desc": "First filled 14.2 kg LPG cylinder completely free.", "badge": "Free"},
            {"title": "2-Burner Gas Stove", "desc": "Safe new double-burner gas stove for free.", "badge": "Free"},
            {"title": "₹0 Deposit", "desc": "Zero security deposit or middleman fee.", "badge": "₹0 Fee"}
        ],
        "q1_text": "Sister, do you already have a gas connection at home?",
        "q1_hint": "Tap one of the two large buttons below:",
        "q1_no": "No, no gas connection",
        "q1_no_desc": "We cook on firewood or traditional chulha",
        "q1_yes": "Yes, already have gas",
        "q1_yes_desc": "There is already a cylinder at home",
        "q2_text": "Do you have a Ration Card?",
        "q2_hint": "A card listing your family members' names:",
        "q2_yes": "Yes, have Ration Card",
        "q2_yes_desc": "Family ration card is available",
        "q2_no": "No Ration Card",
        "q2_no_desc": "Ration card is not yet made",
        "congrats_title": "Congratulations Sister! You are eligible",
        "congrats_desc": "You will receive a free gas stove and cylinder.",
        "docs_heading": "📋 Prepare only these 3 documents:",
        "docs_hint": "(Tap any card to hear its name spoken)",
        "doc_aadhaar_title": "Aadhaar Card",
        "doc_aadhaar_desc": "Woman applicant's own Aadhaar card.",
        "doc_aadhaar_audio": "First document: Your Aadhaar card photocopy.",
        "doc_ration_title": "Ration Card",
        "doc_ration_desc": "Ration card listing family members.",
        "doc_ration_audio": "Second document: Your family ration card.",
        "doc_passbook_title": "Bank Passbook",
        "doc_passbook_desc": "Woman's bank account or Jan Dhan passbook.",
        "doc_passbook_audio": "Third document: Bank passbook first page copy.",
        "where_title": "📍 Take these documents here:",
        "where_agency_title": "1. Nearest Gas Agency",
        "where_agency_desc": "Visit your nearest Indane, Bharat Gas, or HP Gas distributor.",
        "where_csc_title": "2. Village CSC Centre",
        "where_csc_desc": "Visit your village Panchayat or CSC kiosk for online form.",
        "safety_alert": "Caution Sister: This scheme is 100% free by the government. Never pay any fee or bribe to middlemen!",
        "ineligible_text": "Ujjwala 2.0 is for new connections. If you don't have a ration card, please apply through your Panchayat first.",
        "btn_start": "Check Eligibility (Start)",
        "btn_to_where": "Where to go? View 👉",
        "btn_restart": "🔄 Start Over",
        "btn_retry": "🔄 Check Again",
        "btn_demo": "Run 1-Click Demo",
        "mic_tap": "Tap Mic & Speak",
        "mic_listening": "Listening... Speak sister"
    }
}


def get_languages():
    """
    Returns the list of 11 supported Indian languages with their codes and flags.

    Returns:
        list: List of language dictionaries.
    """
    return LANGUAGES


def get_scheme_data(lang="hi"):
    """
    Returns localized scheme metadata, UI texts, and official helpline information.

    Args:
        lang (str): 2-letter language code ('hi', 'ta', 'te', etc.).

    Returns:
        dict: Localized scheme dictionary.
    """
    data = TRANSLATIONS.get(lang, TRANSLATIONS["hi"])
    return {
        "id": PMUY_SCHEME_FACTS["scheme_id"],
        "official_facts": PMUY_SCHEME_FACTS,
        "lang": lang,
        "texts": data,
        "helpline": {
            "toll_free": PMUY_SCHEME_FACTS["official_helpline"],
            "emergency": PMUY_SCHEME_FACTS["emergency_leak_helpline"],
            "website": PMUY_SCHEME_FACTS["official_website"]
        }
    }


def get_walkthrough(lang="hi"):
    """
    Generates the step-by-step 1-click sample walkthrough in the requested language.

    Args:
        lang (str): 2-letter language code ('hi', 'ta', 'te', etc.).

    Returns:
        list: List of step dictionaries for sequential walkthrough execution.
    """
    t = TRANSLATIONS.get(lang, TRANSLATIONS["hi"])
    return [
        {
            "step": 1,
            "title": t["app_title"],
            "didi_speech": t["didi_greeting"],
            "active_card": "welcome"
        },
        {
            "step": 2,
            "title": t["q1_text"],
            "didi_speech": t["q1_text"] + " " + t["q1_hint"],
            "active_card": "question_existing",
            "selected_choice": "no"
        },
        {
            "step": 3,
            "title": t["q2_text"],
            "didi_speech": t["q2_text"] + " " + t["q2_hint"],
            "active_card": "question_ration",
            "selected_choice": "yes"
        },
        {
            "step": 4,
            "title": t["congrats_title"],
            "didi_speech": t["congrats_title"] + "! " + t["congrats_desc"],
            "active_card": "documents"
        },
        {
            "step": 5,
            "title": t["docs_heading"],
            "didi_speech": t["doc_aadhaar_audio"] + " " + t["doc_ration_audio"] + " " + t["doc_passbook_audio"],
            "active_card": "documents"
        },
        {
            "step": 6,
            "title": t["where_title"],
            "didi_speech": t["safety_alert"],
            "active_card": "where_to_go"
        }
    ]
