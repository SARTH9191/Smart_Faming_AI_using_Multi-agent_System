import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VoiceAssistant({ apiUrl, farmer }) {
  const [isListening, setIsListening] = useState(false);
  const [response, setResponse] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showInputModal, setShowInputModal] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [language, setLanguage] = useState('en');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Sync language from farmer profile preference
  useEffect(() => {
    if (farmer?.language) {
      setLanguage(farmer.language);
    }
  }, [farmer]);

  const getFarmId = () => {
    if (!farmer) return 'FARM001';
    return farmer.farmerId || farmer.farmer_id || 'FARM001';
  };

  const handleVoiceCommand = async (text) => {
    try {
      setIsLoading(true);
      const res = await axios.post(`${apiUrl}/voice_command`, {
        text: text,
        language: language,
        farm_id: getFarmId(),
      });
      
      const responseText = res.data.reply || res.data.voice_summary || res.data.response_text;
      const llmUsed = res.data.llm_used || false;
      setResponse({ text: responseText, llmUsed });
      setShowModal(true);
      
      // Speak response with multilingual support
      await speakText(responseText, language);
    } catch (error) {
      console.error('Error processing voice command:', error);
      const errMsg = 'Sorry, I could not process your request. Please try again.';
      setResponse({ text: errMsg, llmUsed: false });
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced Multilingual Text-to-Speech Function
  const speakText = async (text, lang) => {
    try {
      // Stop any ongoing speech
      stopSpeech();
      setIsSpeaking(true);

      console.log('🔊 Starting TTS for text:', text.substring(0, 50) + '...');
      console.log('🌐 Language:', lang);

      // Method 1: Try backend gTTS (better for Hindi/Marathi)
      try {
        console.log('📡 Attempting backend gTTS...');
        const audioResponse = await axios.post(
          `${apiUrl}/text_to_speech`,
          null,
          {
            params: { text, language: lang },
            responseType: 'blob',
            timeout: 10000 // 10 second timeout
          }
        );
        
        console.log('✅ Backend TTS response received, size:', audioResponse.data.size, 'bytes');
        
        // Play audio from backend
        const audioBlob = new Blob([audioResponse.data], { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Set volume to maximum
        audio.volume = 1.0;
        
        setCurrentAudio(audio);
        
        audio.onloadedmetadata = () => {
          console.log('🎵 Audio loaded, duration:', audio.duration, 'seconds');
        };
        
        audio.onplay = () => {
          console.log('▶️ Audio started playing');
        };
        
        audio.onended = () => {
          console.log('⏹️ Audio finished playing');
          URL.revokeObjectURL(audioUrl);
          setIsSpeaking(false);
          setCurrentAudio(null);
        };
        
        audio.onerror = (e) => {
          console.error('❌ Audio playback error:', e);
          console.error('Audio error details:', audio.error);
          URL.revokeObjectURL(audioUrl);
          setIsSpeaking(false);
          setCurrentAudio(null);
          
          // Try browser fallback on audio error
          throw new Error('Audio playback failed');
        };
        
        try {
          console.log('🎬 Attempting to play audio...');
          const playPromise = audio.play();
          
          if (playPromise !== undefined) {
            await playPromise;
            console.log('✅ Audio playing successfully');
          }
        } catch (playError) {
          console.error('❌ Play failed:', playError);
          console.error('This might be due to browser autoplay policy');
          
          // Show alert to user
          alert('Please click the "Replay" button to hear the response. Browser blocked autoplay.');
          setIsSpeaking(false);
          
          // Keep audio available for manual replay
          return;
        }
        
        return; // Exit if backend TTS works
      } catch (backendError) {
        console.warn('⚠️ Backend TTS failed:', backendError.message);
        console.log('🔄 Falling back to browser Web Speech API...');
      }

      // Method 2: Fallback to browser Web Speech API
      if ('speechSynthesis' in window) {
        console.log('🗣️ Using browser Web Speech API');
        
        // Load voices if not loaded
        const voices = window.speechSynthesis.getVoices();
        if (voices.length === 0) {
          console.log('⏳ Waiting for voices to load...');
          await new Promise(resolve => {
            window.speechSynthesis.onvoiceschanged = () => resolve();
            setTimeout(resolve, 1000); // Timeout after 1 second
          });
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set language with proper locale codes
        const langMap = {
          'hi': 'hi-IN',
          'mr': 'mr-IN',
          'en': 'en-US'
        };
        utterance.lang = langMap[lang] || 'en-US';
        
        // Configure voice parameters
        utterance.rate = 0.9; // Slightly slower for clarity
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to find native voice for the language
        const loadedVoices = window.speechSynthesis.getVoices();
        console.log('📢 Available voices:', loadedVoices.length);
        
        const nativeVoice = loadedVoices.find(voice => 
          voice.lang.startsWith(lang) || voice.lang.startsWith(langMap[lang])
        );
        
        if (nativeVoice) {
          utterance.voice = nativeVoice;
          console.log('✅ Using voice:', nativeVoice.name, '(' + nativeVoice.lang + ')');
        } else {
          console.log('⚠️ No native voice found for', lang, 'using default');
        }
        
        // Speak with error handling
        return new Promise((resolve, reject) => {
          utterance.onstart = () => {
            console.log('▶️ Browser TTS started');
          };
          
          utterance.onend = () => {
            console.log('✅ Browser TTS finished');
            setIsSpeaking(false);
            resolve();
          };
          
          utterance.onerror = (event) => {
            console.error('❌ Browser TTS error:', event);
            setIsSpeaking(false);
            reject(event);
          };
          
          console.log('🎬 Speaking with browser TTS...');
          window.speechSynthesis.speak(utterance);
        });
      } else {
        console.error('❌ Speech Synthesis not supported in this browser');
        setIsSpeaking(false);
      }
    } catch (error) {
      console.error('❌ Text-to-speech error:', error);
      setIsSpeaking(false);
      // Silent fail - don't disrupt user experience
    }
  };

  // Stop speech function
  const stopSpeech = () => {
    // Stop audio playback
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
    }
    
    // Stop browser speech synthesis
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    
    setIsSpeaking(false);
  };

  // Replay speech function
  const replaySpeech = () => {
    if (response) {
      speakText(response, language);
    }
  };

  const handleClick = () => {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsListening(true);
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.lang = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 3;
      
      // Add timeout for recognition
      const timeoutId = setTimeout(() => {
        recognition.stop();
        console.log('Recognition timeout - showing text input');
        setIsListening(false);
        setShowInputModal(true);
      }, 10000); // 10 second timeout
      
      recognition.onresult = (event) => {
        clearTimeout(timeoutId);
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;
        console.log('Heard:', transcript, '(confidence:', confidence + ')');
        
        if (confidence < 0.5) {
          console.warn('Low confidence, prompting for confirmation');
        }
        
        handleVoiceCommand(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = (event) => {
        clearTimeout(timeoutId);
        console.error('Speech recognition error:', event.error);
        console.error('Error details:', event);
        
        const errorMessages = {
          'no-speech': 'No speech detected. Please try again or type your command.',
          'audio-capture': 'Microphone not available. Please check microphone permissions.',
          'not-allowed': 'Microphone access denied. Please allow microphone access in browser settings.',
          'network': 'Network error. Please check your internet connection.',
          'aborted': 'Recognition was cancelled. Click again to try.',
          'language-not-supported': 'This language is not supported for speech recognition.',
          'service-not-allowed': 'Speech recognition service not allowed.',
        };
        
        const userMessage = errorMessages[event.error] || 'Voice recognition failed. Please type your command below.';
        
        setIsListening(false);
        // Show text input modal as fallback instead of just showing error
        setTextInput('');
        setShowInputModal(true);
      };
      
      recognition.onend = () => {
        clearTimeout(timeoutId);
        setIsListening(false);
      };
      
      try {
        recognition.start();
      } catch (err) {
        console.error('Failed to start recognition:', err);
        setIsListening(false);
        setShowInputModal(true);
      }
    } else {
      // Browser doesn't support speech recognition - show text input
      console.warn('Speech recognition not supported in this browser');
      setShowInputModal(true);
    }
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      handleVoiceCommand(textInput);
      setTextInput('');
      setShowInputModal(false);
    }
  };

  return (
    <>
      {/* 🎤 Voice Button (fixed bottom-right) */}
      <button
        className={`voice-assistant ${isListening ? 'active' : ''}`}
        onClick={handleClick}
        title="AI Voice Assistant (Click to speak)"
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '90px',
          opacity: isLoading ? 0.6 : 1,
        }}
        disabled={isLoading}
      >
        {isLoading ? '⏳' : isListening ? '🔴' : '🎤'}
      </button>

      {/* ⌨️ Text Input Button */}
      <button
        className="voice-assistant"
        onClick={() => setShowInputModal(true)}
        title="Type Command"
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          fontSize: '1.5rem',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
          zIndex: 1000,
          transition: 'transform 0.2s',
        }}
        onMouseOver={(e) => (e.target.style.transform = 'scale(1.1)')}
        onMouseOut={(e) => (e.target.style.transform = 'scale(1)')}
      >
        ⌨️
      </button>

      {/* Text Input Modal */}
      {showInputModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 2000,
          backdropFilter: 'blur(4px)',
        }} onClick={() => setShowInputModal(false)}>
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '520px',
            width: '90%',
            boxShadow: '0 25px 70px rgba(0,0,0,0.35)',
          }} onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <span style={{ fontSize: '2rem' }}>🌾</span>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>AI Farming Assistant</h3>
                {farmer?.name && (
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>Helping {farmer.name}</p>
                )}
              </div>
            </div>

            {/* LLM Notice */}
            <div style={{
              background: 'linear-gradient(135deg, #ecfdf5, #d1fae5)',
              borderRadius: '8px', padding: '0.6rem 0.9rem',
              marginBottom: '1rem', fontSize: '0.78rem', color: '#065f46',
              display: 'flex', alignItems: 'center', gap: '0.4rem',
            }}>
              🤖 Powered by Groq AI — Ask anything about your farm!
            </div>

            {/* Language Selector */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ marginRight: '0.75rem', fontWeight: '600', fontSize: '0.9rem' }}>Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '0.9rem' }}
              >
                <option value="en">🇬🇧 English</option>
                <option value="hi">🇮🇳 हिंदी (Hindi)</option>
                <option value="mr">🇮🇳 मराठी (Marathi)</option>
              </select>
            </div>

            {/* Text Input */}
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder={language === 'hi' ? 'अपना सवाल यहाँ टाइप करें...' : language === 'mr' ? 'तुमचा प्रश्न येथे टाइप करा...' : 'Ask anything about your farm...'}
              style={{
                width: '100%', minHeight: '90px', padding: '0.85rem',
                borderRadius: '8px', border: '2px solid #d1d5db',
                fontSize: '1rem', marginBottom: '1rem',
                resize: 'vertical', fontFamily: 'inherit',
                boxSizing: 'border-box',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#10b981')}
              onBlur={(e) => (e.target.style.borderColor = '#d1d5db')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleTextSubmit();
                }
              }}
            />

            {/* Quick Commands */}
            <div style={{
              marginBottom: '1rem', padding: '0.75rem',
              background: '#f0fdf4', borderRadius: '8px', fontSize: '0.8rem',
            }}>
              <strong>Quick Questions:</strong>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.5rem' }}>
                {[
                  { label: '🌤 Weather', q: "What is the weather forecast?" },
                  { label: '💧 Irrigation', q: "Do my crops need irrigation today?" },
                  { label: '🌱 Soil Health', q: "How is my soil health?" },
                  { label: '🦠 Diseases', q: "Are there any diseases I should watch for?" },
                  { label: '💰 Market', q: "What are the current market prices for my crops?" },
                  { label: '🏛 Schemes', q: "What government schemes am I eligible for?" },
                ].map(({ label, q }) => (
                  <button
                    key={label}
                    onClick={() => setTextInput(q)}
                    style={{
                      padding: '0.3rem 0.6rem', borderRadius: '4px',
                      border: '1px solid #10b981', background: 'white',
                      cursor: 'pointer', fontSize: '0.75rem',
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => { setShowInputModal(false); setTextInput(''); }}
                style={{ flex: 1 }}
              >Cancel</button>
              <button
                className="btn btn-primary"
                onClick={handleTextSubmit}
                style={{ flex: 2, background: 'linear-gradient(135deg, #10b981, #059669)', border: 'none', color: 'white' }}
                disabled={!textInput.trim() || isLoading}
              >
                {isLoading ? '⏳ Thinking...' : '📤 Ask AI'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Response Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 2000,
          backdropFilter: 'blur(4px)',
        }} onClick={() => { stopSpeech(); setShowModal(false); }}>
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '520px',
            width: '90%',
            boxShadow: '0 25px 70px rgba(0,0,0,0.35)',
          }} onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.2rem' }}>
              <div style={{
                width: '48px', height: '48px', borderRadius: '50%',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.5rem', flexShrink: 0,
              }}>🌾</div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.05rem' }}>AI Farming Assistant</h3>
                <p style={{ margin: 0, fontSize: '0.78rem', color: '#6b7280' }}>
                  {response?.llmUsed ? '🤖 Groq AI (llama-3.1-8b-instant)' : '📋 Rule-based fallback'}
                  {farmer?.name ? ` · ${farmer.name}'s Farm` : ''}
                </p>
              </div>
            </div>

            {/* Language Selector */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ marginRight: '0.75rem', fontWeight: '600', fontSize: '0.85rem' }}>Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '0.85rem' }}
              >
                <option value="en">🇬🇧 English</option>
                <option value="hi">🇮🇳 हिंदी</option>
                <option value="mr">🇮🇳 मराठी</option>
              </select>
            </div>

            {/* AI Response bubble */}
            <div style={{
              background: 'linear-gradient(135deg, #f0fdf4, #ecfdf5)',
              border: '1px solid #a7f3d0',
              padding: '1.1rem 1.25rem',
              borderRadius: '12px',
              marginBottom: '1rem',
              lineHeight: '1.65',
              fontSize: '0.95rem',
              color: '#064e3b',
            }}>
              {response?.text || response}
            </div>

            {/* TTS Controls */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', justifyContent: 'center' }}>
              <button
                onClick={replaySpeech}
                disabled={isSpeaking}
                style={{
                  padding: '0.5rem 1rem', borderRadius: '6px',
                  border: '1px solid #10b981',
                  background: isSpeaking ? '#e5e7eb' : '#f0fdf4',
                  cursor: isSpeaking ? 'not-allowed' : 'pointer',
                  fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.3rem',
                }}
              >
                🔊 {isSpeaking ? 'Speaking...' : 'Replay'}
              </button>
              {isSpeaking && (
                <button
                  onClick={stopSpeech}
                  style={{
                    padding: '0.5rem 1rem', borderRadius: '6px',
                    border: '1px solid #ef4444', background: '#fef2f2',
                    cursor: 'pointer', fontSize: '0.875rem',
                    display: 'flex', alignItems: 'center', gap: '0.3rem',
                  }}
                >
                  ⏹️ Stop
                </button>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className="btn btn-primary"
                onClick={() => { stopSpeech(); setShowModal(false); }}
                style={{ flex: 1 }}
              >Close</button>
              <button
                className="btn btn-secondary"
                onClick={() => { stopSpeech(); setShowModal(false); setTimeout(handleClick, 200); }}
                style={{ flex: 1 }}
              >🎤 Ask Again</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default VoiceAssistant;
