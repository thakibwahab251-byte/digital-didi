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
    // Web Audio Synthesizer (Instant Zero-Asset Indic Acoustic Earcons)
    // =========================================================================
    let audioCtx = null;

    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function playAudioCue(type) {
        if (!state.isSoundEnabled) return;
        try {
            const ctx = getAudioContext();
            if (!ctx) return;
            const now = ctx.currentTime;

            if (type === 'tap') {
                // Soft click chime (480Hz gentle pluck, 0.08s)
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(480, now);
                osc.frequency.exponentialRampToValueAtTime(320, now + 0.08);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.08);
            } else if (type === 'mic_start') {
                // Ascending two-note chime (440Hz -> 660Hz) to signal mic listening
                [440, 660].forEach((freq, idx) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(freq, now + idx * 0.11);
                    gain.gain.setValueAtTime(0.15, now + idx * 0.11);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + (idx + 1) * 0.11);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + idx * 0.11);
                    osc.stop(now + (idx + 1) * 0.11);
                });
            } else if (type === 'mic_stop') {
                // Soft descending tone (550Hz -> 380Hz)
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(550, now);
                osc.frequency.exponentialRampToValueAtTime(380, now + 0.12);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.12);
            } else if (type === 'success') {
                // Cheerful 3-note celebration arpeggio (C5 -> E5 -> G5: 523Hz -> 659Hz -> 784Hz)
                [523.25, 659.25, 783.99].forEach((freq, idx) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(freq, now + idx * 0.13);
                    gain.gain.setValueAtTime(0.18, now + idx * 0.13);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.13 + 0.35);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + idx * 0.13);
                    osc.stop(now + idx * 0.13 + 0.35);
                });
            } else if (type === 'alert') {
                // Gentle cautionary two-tone (392Hz -> 330Hz)
                [392, 329.63].forEach((freq, idx) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(freq, now + idx * 0.15);
                    gain.gain.setValueAtTime(0.14, now + idx * 0.15);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.15 + 0.22);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + idx * 0.15);
                    osc.stop(now + idx * 0.15 + 0.22);
                });
            } else if (type === 'lang_change') {
                // Soft waterdrop-style harmonic chime (587Hz -> 880Hz)
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(587.33, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.16);
                gain.gain.setValueAtTime(0.14, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.18);
            }
        } catch (e) {
            // AudioContext gracefully bypassed if uninitialized
        }
    }

    // =========================================================================
    // Speech Synthesis (Audio Output in Selected Indian Language)
    // =========================================================================
    let cachedVoices = [];

    function populateVoices() {
        if ('speechSynthesis' in window) {
            cachedVoices = window.speechSynthesis.getVoices();
        }
    }

    if ('speechSynthesis' in window) {
        populateVoices();
        window.speechSynthesis.onvoiceschanged = populateVoices;
    }

    function findBestIndicVoice(langPrefix, speechCode) {
        if (!cachedVoices.length && 'speechSynthesis' in window) {
            cachedVoices = window.speechSynthesis.getVoices();
        }
        if (!cachedVoices || !cachedVoices.length) return null;

        const codeLower = speechCode.toLowerCase().replace('_', '-');
        const prefixLower = langPrefix.toLowerCase();

        // 1. Exact match with preference for female/Didi voice
        const femaleVoice = cachedVoices.find(v => {
            const vl = v.lang.toLowerCase().replace('_', '-');
            const vn = v.name.toLowerCase();
            const isMatch = vl === codeLower || vl.startsWith(prefixLower);
            const isFemale = vn.includes('female') || vn.includes('woman') || vn.includes('swara') ||
                             vn.includes('lekha') || vn.includes('kalpana') || vn.includes('geeta') ||
                             vn.includes('zira') || vn.includes('neerja') || vn.includes('heera');
            return isMatch && isFemale;
        });
        if (femaleVoice) return femaleVoice;

        // 2. Language code prefix match
        const exactLangVoice = cachedVoices.find(v => {
            const vl = v.lang.toLowerCase().replace('_', '-');
            return vl === codeLower || vl.startsWith(prefixLower);
        });
        if (exactLangVoice) return exactLangVoice;

        // 3. Match language name inside voice name
        const langNames = {
            hi: 'hindi', ta: 'tamil', te: 'telugu', bn: 'bengali',
            mr: 'marathi', gu: 'gujarati', kn: 'kannada', ml: 'malayalam',
            pa: 'punjabi', or: 'odia', en: 'india'
        };
        const targetName = langNames[prefixLower] || prefixLower;
        const nameMatch = cachedVoices.find(v => v.name.toLowerCase().includes(targetName));
        return nameMatch || null;
    }

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

        // Fine-tuned cadence and pitch per Indian language for respectful Didi persona
        const cadenceMap = {
            hi: { rate: 0.90, pitch: 1.05 },
            ta: { rate: 0.88, pitch: 1.02 },
            te: { rate: 0.89, pitch: 1.03 },
            bn: { rate: 0.90, pitch: 1.04 },
            mr: { rate: 0.90, pitch: 1.03 },
            gu: { rate: 0.91, pitch: 1.04 },
            kn: { rate: 0.89, pitch: 1.02 },
            ml: { rate: 0.87, pitch: 1.01 },
            pa: { rate: 0.90, pitch: 1.05 },
            or: { rate: 0.89, pitch: 1.03 },
            en: { rate: 0.94, pitch: 1.00 }
        };
        const cadence = cadenceMap[state.currentLang] || { rate: 0.90, pitch: 1.04 };
        utterance.rate = cadence.rate;
        utterance.pitch = cadence.pitch;

        const bestVoice = findBestIndicVoice(state.currentLang, state.currentSpeechCode);
        if (bestVoice) {
            utterance.voice = bestVoice;
        }

        let hasFinished = false;
        const finish = () => {
            if (hasFinished) return;
            hasFinished = true;
            state.isSpeaking = false;
            if (elements.speakingWave) elements.speakingWave.style.display = 'none';
            if (callback) callback();
        };

        // Safety watchdog: prevent utterance lock on browsers that hang speech synthesis
        const wordCount = text.split(/\s+/).length;
        const estimatedDurationMs = Math.max(2500, wordCount * 450);
        const watchdog = setTimeout(finish, estimatedDurationMs + 4000);

        utterance.onstart = () => {
            state.isSpeaking = true;
            if (elements.speakingWave) elements.speakingWave.style.display = 'flex';
        };

        utterance.onend = () => {
            clearTimeout(watchdog);
            finish();
        };

        utterance.onerror = (e) => {
            clearTimeout(watchdog);
            console.warn('SpeechSynthesis error:', e);
            finish();
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
            playAudioCue('mic_start');
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
        if (state.isListening) {
            playAudioCue('mic_stop');
        }
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
        playAudioCue('lang_change');
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
                    playAudioCue('success');
                    updateDialogue(t.congrats_title + '! ' + t.congrats_desc + ' ' + t.docs_heading);
                    break;
                case 'where_to_go':
                    updateDialogue(t.safety_alert);
                    break;
                case 'ineligible':
                    playAudioCue('alert');
                    updateDialogue(t.ineligible_text);
                    break;
            }
        }
    }

    // =========================================================================
    // 1-Click Automated Sample Walkthrough Demo (Multilingual & Zero-Fail)
    // =========================================================================
    function clearDemoFocus() {
        document.querySelectorAll('.demo-focus').forEach(el => {
            el.classList.remove('demo-focus');
        });
    }

    async function startWalkthroughDemo() {
        if (state.isDemoRunning) {
            stopDemo();
            return;
        }

        playAudioCue('tap');
        state.isDemoRunning = true;
        clearDemoFocus();
        elements.btnWalkthrough.innerHTML = '<span class="demo-icon">⏸️</span><span class="demo-text">Pause Demo</span>';
        elements.btnWalkthrough.style.background = '#FFCC80';

        let steps = [];
        try {
            const resp = await fetch(`/api/walkthrough?lang=${state.currentLang}`);
            const data = await resp.json();
            steps = data.steps || [];
        } catch (err) {
            console.warn('Network walkthrough fetch failed, using local offline fallback:', err);
        }

        // Resilient fallback if fetch failed or returned empty
        if (!steps || !steps.length) {
            const t = state.schemeData?.texts || {};
            steps = [
                { step: 1, didi_speech: t.didi_greeting || 'नमस्ते दीदी!', active_card: 'welcome' },
                { step: 2, didi_speech: (t.q1_text || '') + ' ' + (t.q1_hint || ''), active_card: 'question_existing', selected_choice: 'no' },
                { step: 3, didi_speech: (t.q2_text || '') + ' ' + (t.q2_hint || ''), active_card: 'question_ration', selected_choice: 'yes' },
                { step: 4, didi_speech: (t.congrats_title || '') + '! ' + (t.congrats_desc || ''), active_card: 'documents' },
                { step: 5, didi_speech: (t.doc_aadhaar_audio || '') + ' ' + (t.doc_ration_audio || '') + ' ' + (t.doc_passbook_audio || ''), active_card: 'documents' },
                { step: 6, didi_speech: t.safety_alert || 'गैस कनेक्शन बिल्कुल मुफ्त है।', active_card: 'where_to_go' }
            ];
        }

        let currentStepIdx = 0;

        function runNextStep() {
            if (!state.isDemoRunning || currentStepIdx >= steps.length) {
                stopDemo(true);
                return;
            }

            clearDemoFocus();
            const step = steps[currentStepIdx];
            currentStepIdx++;

            if (step.active_card === 'welcome') {
                navigateToStage('welcome', false);
                if (elements.btnStartCheck) elements.btnStartCheck.classList.add('demo-focus');
            } else if (step.active_card === 'question_existing') {
                navigateToStage('question_existing', false);
                if (elements.btnExistingNo) elements.btnExistingNo.classList.add('demo-focus');
            } else if (step.active_card === 'question_ration') {
                navigateToStage('question_ration', false);
                if (elements.btnRationYes) elements.btnRationYes.classList.add('demo-focus');
            } else if (step.active_card === 'documents') {
                navigateToStage('documents', false);
                playAudioCue('success');
                if (elements.docCards && elements.docCards.length) {
                    elements.docCards.forEach((c, i) => {
                        setTimeout(() => {
                            if (state.isDemoRunning) c.classList.add('demo-focus');
                        }, i * 350);
                    });
                }
            } else if (step.active_card === 'where_to_go') {
                navigateToStage('where_to_go', false);
                const whereCards = document.querySelectorAll('.agency-card');
                if (whereCards && whereCards.length) {
                    whereCards.forEach(c => c.classList.add('demo-focus'));
                }
            }

            updateDialogue(step.didi_speech, true, () => {
                if (state.isDemoRunning) {
                    state.walkthroughTimer = setTimeout(runNextStep, 1800);
                }
            });
        }

        runNextStep();
    }

    function stopDemo(completed = false) {
        state.isDemoRunning = false;
        clearDemoFocus();
        if (state.walkthroughTimer) clearTimeout(state.walkthroughTimer);
        window.speechSynthesis.cancel();
        const demoLabel = state.schemeData?.texts?.btn_demo || '1-क्लिक डेमो चलाएं';
        elements.btnWalkthrough.innerHTML = `<span class="demo-icon">⚡</span><span class="demo-text">${demoLabel}</span>`;
        elements.btnWalkthrough.style.background = '#FFE082';

        if (completed) {
            playAudioCue('success');
        }
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
                playAudioCue('tap');
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
            playAudioCue('tap');
            if (state.lastSpokenText) {
                speakText(state.lastSpokenText);
            }
        });

        // Central Mic button
        elements.btnMic.addEventListener('click', toggleListening);

        // Stage 1 -> Start
        elements.btnStartCheck.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('question_existing');
        });

        // Question 1: Existing Gas Connection?
        elements.btnExistingNo.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('question_ration');
        });

        elements.btnExistingYes.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('ineligible');
        });

        // Question 2: Ration Card?
        elements.btnRationYes.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('documents');
        });

        elements.btnRationNo.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('ineligible');
        });

        // Stage 4 -> Where to go
        elements.btnToWhere.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('where_to_go');
        });

        // Restart buttons
        elements.btnRestart.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('welcome');
        });

        elements.btnRetryIneligible.addEventListener('click', () => {
            playAudioCue('tap');
            navigateToStage('welcome');
        });

        // Document Cards: Tap to listen in current language
        elements.docCards.forEach(card => {
            card.addEventListener('click', () => {
                playAudioCue('tap');
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
