/**
 * app.js
 * Digital Didi Frontend Logic
 * Supports 11 major Indian languages:
 * Hindi (hi), Tamil (ta), Telugu (te), Bengali (bn), Marathi (mr),
 * Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa), Odia (or), English (en).
 *
 * Implements:
 * 1. Web Speech Synthesis (TTS in selected Indian language)
 * 2. Web Speech Recognition (STT in selected Indian language)
 * 3. Icon/Flag Language Picker
 * 4. 1-Click Automated Sample Walkthrough in chosen language
 * 5. High-contrast large touch button navigation
 */

(function () {
    'use strict';

    // Application State
    const state = {
        currentLang: 'hi',
        currentSpeechCode: 'hi-IN',
        currentStage: 'welcome',
        isSoundEnabled: true,
        isSpeaking: false,
        isListening: false,
        isDemoRunning: false,
        lastSpokenText: '',
        recognition: null,
        walkthroughTimer: null,
        schemeData: null
    };

    // DOM Elements Cache
    const elements = {
        didiMessage: document.getElementById('didi-message'),
        speakingWave: document.getElementById('speaking-wave'),
        btnReplay: document.getElementById('btn-replay-audio'),
        btnSoundToggle: document.getElementById('btn-sound-toggle'),
        soundIcon: document.getElementById('sound-icon'),
        lblSoundStatus: document.getElementById('lbl-sound-status'),
        btnWalkthrough: document.getElementById('btn-walkthrough'),
        lblBtnDemo: document.getElementById('lbl-btn-demo'),
        btnMic: document.getElementById('btn-mic'),
        micStatusLabel: document.getElementById('mic-status-label'),
        btnStartCheck: document.getElementById('btn-start-check'),
        btnExistingNo: document.getElementById('btn-existing-no'),
        btnExistingYes: document.getElementById('btn-existing-yes'),
        btnRationYes: document.getElementById('btn-ration-yes'),
        btnRationNo: document.getElementById('btn-ration-no'),
        btnToWhere: document.getElementById('btn-to-where'),
        btnRestart: document.getElementById('btn-restart'),
        btnRetryIneligible: document.getElementById('btn-retry-ineligible'),
        quickChips: document.getElementById('quick-chips'),
        docCards: document.querySelectorAll('.doc-card'),
        langButtons: document.querySelectorAll('.lang-btn')
    };

    // =========================================================================
    // Speech Synthesis (Audio Output in Selected Indian Language)
    // =========================================================================
    function speakText(text, callback) {
        if (!text) return;
        state.lastSpokenText = text;

        if (!state.isSoundEnabled || !('speechSynthesis' in window)) {
            if (callback) callback();
            return;
        }

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = state.currentSpeechCode;
        utterance.rate = 0.92; // Slightly slower, clear conversational pace
        utterance.pitch = 1.05; // Warm, respectful elder sister tone

        // Look for matching Indic voice in the browser
        const voices = window.speechSynthesis.getVoices();
        const langPrefix = state.currentLang;
        const matchingVoice = voices.find(v =>
            v.lang.toLowerCase().startsWith(langPrefix) ||
            v.lang.toLowerCase().replace('_', '-').includes(state.currentSpeechCode.toLowerCase())
        );

        if (matchingVoice) {
            utterance.voice = matchingVoice;
        }

        utterance.onstart = () => {
            state.isSpeaking = true;
            if (elements.speakingWave) elements.speakingWave.style.display = 'flex';
        };

        utterance.onend = () => {
            state.isSpeaking = false;
            if (elements.speakingWave) elements.speakingWave.style.display = 'none';
            if (callback) callback();
        };

        utterance.onerror = (e) => {
            console.warn('SpeechSynthesis error:', e);
            state.isSpeaking = false;
            if (elements.speakingWave) elements.speakingWave.style.display = 'none';
            if (callback) callback();
        };

        window.speechSynthesis.speak(utterance);
    }

    function updateDialogue(text, autoSpeak = true, callback = null) {
        if (elements.didiMessage) {
            elements.didiMessage.textContent = text;
        }
        if (autoSpeak) {
            speakText(text, callback);
        } else if (callback) {
            callback();
        }
    }

    // =========================================================================
    // Speech Recognition (Voice Input in Selected Indian Language)
    // =========================================================================
    function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log('Web Speech Recognition not supported in this browser.');
            return;
        }

        state.recognition = new SpeechRecognition();
        state.recognition.lang = state.currentSpeechCode;
        state.recognition.continuous = false;
        state.recognition.interimResults = false;

        state.recognition.onstart = () => {
            state.isListening = true;
            elements.btnMic.classList.add('listening');
            const listeningPrompt = state.schemeData?.texts?.mic_listening || 'सुन रही हूँ... बोलिए दीदी';
            elements.micStatusLabel.textContent = listeningPrompt;
        };

        state.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            elements.micStatusLabel.textContent = `"${transcript}"`;
            sendVoiceQuery(transcript);
        };

        state.recognition.onerror = (event) => {
            console.warn('SpeechRecognition error:', event.error);
            resetMicButton();
        };

        state.recognition.onend = () => {
            resetMicButton();
        };
    }

    function toggleListening() {
        if (state.isDemoRunning) {
            stopDemo();
        }

        if (state.isListening) {
            if (state.recognition) state.recognition.stop();
            resetMicButton();
            return;
        }

        if (state.recognition) {
            try {
                state.recognition.lang = state.currentSpeechCode;
                state.recognition.start();
            } catch (err) {
                console.warn('Recognition start failed:', err);
                promptFallbackQuery();
            }
        } else {
            promptFallbackQuery();
        }
    }

    function resetMicButton() {
        state.isListening = false;
        elements.btnMic.classList.remove('listening');
        const defaultLabel = state.schemeData?.texts?.mic_tap || 'माइक दबाकर बोलें';
        elements.micStatusLabel.textContent = defaultLabel;
    }

    function promptFallbackQuery() {
        const query = state.schemeData?.texts?.q1_no || 'गैस कनेक्शन चाहिए';
        elements.micStatusLabel.textContent = `"${query}"`;
        sendVoiceQuery(query);
    }

    // =========================================================================
    // Multilingual Language Switcher
    // =========================================================================
    async function switchLanguage(langCode, speechCode) {
        state.currentLang = langCode;
        state.currentSpeechCode = speechCode;

        // Update active class on buttons
        elements.langButtons.forEach(btn => {
            if (btn.getAttribute('data-lang') === langCode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update recognition language
        if (state.recognition) {
            state.recognition.lang = speechCode;
        }

        // Fetch localized scheme data
        try {
            const resp = await fetch(`/api/scheme?lang=${langCode}`);
            const data = await resp.json();
            state.schemeData = data;
            applyLocalizedTexts(data.texts);

            // Greet in the newly selected language
            updateDialogue(data.texts.didi_greeting, true);
        } catch (err) {
            console.error('Failed to load language data:', err);
        }
    }

    function applyLocalizedTexts(t) {
        if (!t) return;

        // Update UI IDs
        const map = {
            'lbl-app-title': t.app_title,
            'lbl-app-subtitle': t.app_subtitle,
            'lbl-btn-demo': t.btn_demo,
            'lbl-scheme-name': t.scheme_name,
            'lbl-scheme-tagline': t.scheme_tagline,
            'lbl-benefit-1-title': t.benefits[0].title,
            'lbl-benefit-1-badge': t.benefits[0].badge,
            'lbl-benefit-2-title': t.benefits[1].title,
            'lbl-benefit-2-badge': t.benefits[1].badge,
            'lbl-benefit-3-title': t.benefits[2].title,
            'lbl-benefit-3-badge': t.benefits[2].badge,
            'lbl-btn-start': t.btn_start,
            'lbl-q1-text': t.q1_text,
            'lbl-q1-hint': t.q1_hint,
            'lbl-q1-no': t.q1_no,
            'lbl-q1-no-desc': t.q1_no_desc,
            'lbl-q1-yes': t.q1_yes,
            'lbl-q1-yes-desc': t.q1_yes_desc,
            'lbl-q2-text': t.q2_text,
            'lbl-q2-hint': t.q2_hint,
            'lbl-q2-yes': t.q2_yes,
            'lbl-q2-yes-desc': t.q2_yes_desc,
            'lbl-q2-no': t.q2_no,
            'lbl-q2-no-desc': t.q2_no_desc,
            'lbl-congrats-title': t.congrats_title,
            'lbl-congrats-desc': t.congrats_desc,
            'lbl-docs-heading': t.docs_heading,
            'lbl-docs-hint': t.docs_hint,
            'lbl-doc-aadhaar-title': t.doc_aadhaar_title,
            'lbl-doc-aadhaar-desc': t.doc_aadhaar_desc,
            'lbl-doc-ration-title': t.doc_ration_title,
            'lbl-doc-ration-desc': t.doc_ration_desc,
            'lbl-doc-passbook-title': t.doc_passbook_title,
            'lbl-doc-passbook-desc': t.doc_passbook_desc,
            'lbl-btn-to-where': t.btn_to_where,
            'lbl-where-title': t.where_title,
            'lbl-where-agency-title': t.where_agency_title,
            'lbl-where-agency-desc': t.where_agency_desc,
            'lbl-where-csc-title': t.where_csc_title,
            'lbl-where-csc-desc': t.where_csc_desc,
            'lbl-safety-alert': t.safety_alert,
            'lbl-btn-restart': t.btn_restart,
            'lbl-btn-retry': t.btn_retry,
            'lbl-ineligible-text': t.ineligible_text,
            'mic-status-label': t.mic_tap
        };

        for (const [elemId, textValue] of Object.entries(map)) {
            const el = document.getElementById(elemId);
            if (el && textValue) {
                el.textContent = textValue;
            }
        }
    }

    // =========================================================================
    // API Communication with Backend (Gemini Integration)
    // =========================================================================
    async function sendVoiceQuery(queryText) {
        try {
            elements.micStatusLabel.textContent = '...';
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: queryText,
                    stage: state.currentStage,
                    lang: state.currentLang
                })
            });

            const result = await response.json();
            if (result.status === 'success' && result.data) {
                const data = result.data;
                updateDialogue(data.reply_text, true);

                if (data.suggested_stage && data.suggested_stage !== state.currentStage) {
                    setTimeout(() => {
                        navigateToStage(data.suggested_stage, false);
                    }, 1400);
                }
            }
        } catch (err) {
            console.error('API query error:', err);
            const fallbackMsg = state.schemeData?.texts?.didi_greeting || 'दीदी, नीचे दिए गए बटन से चुनकर बताएं।';
            updateDialogue(fallbackMsg, true);
        } finally {
            resetMicButton();
        }
    }

    // =========================================================================
    // Stage Management & Navigation
    // =========================================================================
    function navigateToStage(stageName, triggerVoice = true) {
        state.currentStage = stageName;

        document.querySelectorAll('.stage-view').forEach(view => {
            view.classList.remove('active');
        });

        const targetView = document.getElementById(`stage-${stageName}`);
        if (targetView) {
            targetView.classList.add('active');
        }

        const t = state.schemeData?.texts;
        if (triggerVoice && t) {
            switch (stageName) {
                case 'welcome':
                    updateDialogue(t.didi_greeting);
                    break;
                case 'question_existing':
                    updateDialogue(t.q1_text + ' ' + t.q1_hint);
                    break;
                case 'question_ration':
                    updateDialogue(t.q2_text + ' ' + t.q2_hint);
                    break;
                case 'documents':
                    updateDialogue(t.congrats_title + '! ' + t.congrats_desc + ' ' + t.docs_heading);
                    break;
                case 'where_to_go':
                    updateDialogue(t.safety_alert);
                    break;
                case 'ineligible':
                    updateDialogue(t.ineligible_text);
                    break;
            }
        }
    }

    // =========================================================================
    // 1-Click Automated Sample Walkthrough Demo (Multilingual)
    // =========================================================================
    async function startWalkthroughDemo() {
        if (state.isDemoRunning) {
            stopDemo();
            return;
        }

        state.isDemoRunning = true;
        elements.btnWalkthrough.innerHTML = '<span class="demo-icon">⏸️</span><span class="demo-text">Pause Demo</span>';
        elements.btnWalkthrough.style.background = '#FFCC80';

        try {
            const resp = await fetch(`/api/walkthrough?lang=${state.currentLang}`);
            const data = await resp.json();
            const steps = data.steps || [];

            let currentStepIdx = 0;

            function runNextStep() {
                if (!state.isDemoRunning || currentStepIdx >= steps.length) {
                    stopDemo();
                    return;
                }

                const step = steps[currentStepIdx];
                currentStepIdx++;

                if (step.active_card === 'welcome') {
                    navigateToStage('welcome', false);
                } else if (step.active_card === 'question_existing') {
                    navigateToStage('question_existing', false);
                } else if (step.active_card === 'question_ration') {
                    navigateToStage('question_ration', false);
                } else if (step.active_card === 'documents') {
                    navigateToStage('documents', false);
                } else if (step.active_card === 'where_to_go') {
                    navigateToStage('where_to_go', false);
                }

                updateDialogue(step.didi_speech, true, () => {
                    if (state.isDemoRunning) {
                        state.walkthroughTimer = setTimeout(runNextStep, 1700);
                    }
                });
            }

            runNextStep();

        } catch (err) {
            console.error('Walkthrough demo failed:', err);
            stopDemo();
        }
    }

    function stopDemo() {
        state.isDemoRunning = false;
        if (state.walkthroughTimer) clearTimeout(state.walkthroughTimer);
        window.speechSynthesis.cancel();
        const demoLabel = state.schemeData?.texts?.btn_demo || '1-क्लिक डेमो चलाएं';
        elements.btnWalkthrough.innerHTML = `<span class="demo-icon">⚡</span><span class="demo-text">${demoLabel}</span>`;
        elements.btnWalkthrough.style.background = '#FFE082';
    }

    // =========================================================================
    // Event Listeners & Binding
    // =========================================================================
    function initEvents() {
        // Language Buttons
        elements.langButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.getAttribute('data-lang');
                const speech = btn.getAttribute('data-speech');
                switchLanguage(lang, speech);
            });
        });

        // 1-Click Demo
        elements.btnWalkthrough.addEventListener('click', startWalkthroughDemo);

        // Sound Toggle
        elements.btnSoundToggle.addEventListener('click', () => {
            state.isSoundEnabled = !state.isSoundEnabled;
            if (state.isSoundEnabled) {
                elements.btnSoundToggle.classList.remove('muted');
                elements.soundIcon.textContent = '🔊';
                elements.lblSoundStatus.textContent = 'आवाज़ चालू';
                speakText(state.lastSpokenText || 'आवाज़ चालू है।');
            } else {
                elements.btnSoundToggle.classList.add('muted');
                elements.soundIcon.textContent = '🔇';
                elements.lblSoundStatus.textContent = 'आवाज़ बंद';
                window.speechSynthesis.cancel();
            }
        });

        // Replay Spoken Audio
        elements.btnReplay.addEventListener('click', () => {
            if (state.lastSpokenText) {
                speakText(state.lastSpokenText);
            }
        });

        // Central Mic button
        elements.btnMic.addEventListener('click', toggleListening);

        // Stage 1 -> Start
        elements.btnStartCheck.addEventListener('click', () => {
            navigateToStage('question_existing');
        });

        // Question 1: Existing Gas Connection?
        elements.btnExistingNo.addEventListener('click', () => {
            navigateToStage('question_ration');
        });

        elements.btnExistingYes.addEventListener('click', () => {
            navigateToStage('ineligible');
        });

        // Question 2: Ration Card?
        elements.btnRationYes.addEventListener('click', () => {
            navigateToStage('documents');
        });

        elements.btnRationNo.addEventListener('click', () => {
            navigateToStage('ineligible');
        });

        // Stage 4 -> Where to go
        elements.btnToWhere.addEventListener('click', () => {
            navigateToStage('where_to_go');
        });

        // Restart buttons
        elements.btnRestart.addEventListener('click', () => {
            navigateToStage('welcome');
        });

        elements.btnRetryIneligible.addEventListener('click', () => {
            navigateToStage('welcome');
        });

        // Document Cards: Tap to listen in current language
        elements.docCards.forEach(card => {
            card.addEventListener('click', () => {
                const docType = card.getAttribute('data-doc');
                const t = state.schemeData?.texts;
                if (!t) return;

                let docText = '';
                if (docType === 'aadhaar') {
                    docText = t.doc_aadhaar_audio;
                } else if (docType === 'ration_card') {
                    docText = t.doc_ration_audio;
                } else if (docType === 'bank_passbook') {
                    docText = t.doc_passbook_audio;
                }
                updateDialogue(docText, true);
            });
        });

        // Quick voice helper chips
        elements.quickChips.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (chip) {
                const query = chip.getAttribute('data-query');
                elements.micStatusLabel.textContent = `"${query}"`;
                sendVoiceQuery(query);
            }
        });

        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = () => {
                // Voices ready
            };
        }
    }

    // =========================================================================
    // Initialization on Page Load
    // =========================================================================
    document.addEventListener('DOMContentLoaded', async () => {
        setupSpeechRecognition();
        initEvents();

        // Initial fetch of current language data
        try {
            const resp = await fetch(`/api/scheme?lang=${state.currentLang}`);
            const data = await resp.json();
            state.schemeData = data;
        } catch (e) {
            console.warn('Initial scheme load failed:', e);
        }

        // Voice greeting after short delay
        setTimeout(() => {
            const greeting = state.schemeData?.texts?.didi_greeting || 'नमस्ते दीदी! मैं आपकी डिजिटल दीदी हूँ।';
            updateDialogue(greeting, true);
        }, 600);
    });

})();
