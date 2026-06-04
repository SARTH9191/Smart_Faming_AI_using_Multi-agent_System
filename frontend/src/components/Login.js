import React, { useState } from 'react';
import './Login.css';

function Login({ onLogin, onAdminClick }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [formData, setFormData] = useState({
    farmerId: '',
    password: '',
    confirmPassword: '',
    name: '',
    email: '',
    phone: '',
    language: 'en'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (mode === 'register') {
        // Registration
        if (!formData.farmerId || !formData.password || !formData.name) {
          setError('Farmer ID, password, and name are required');
          setLoading(false);
          return;
        }

        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }

        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        const response = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            farmer_id: formData.farmerId.toUpperCase(),
            password: formData.password,
            name: formData.name,
            email: formData.email || null,
            phone: formData.phone || null,
            language: formData.language
          })
        });

        const data = await response.json();

        if (!response.ok) {
          const errorMessage = typeof data.detail === 'string' 
            ? data.detail 
            : (Array.isArray(data.detail) ? data.detail[0]?.msg : JSON.stringify(data.detail));
          setError(errorMessage || 'Registration failed');
          setLoading(false);
          return;
        }

        setSuccess('Registration successful! Please login.');
        setTimeout(() => {
          setMode('login');
          setSuccess('');
        }, 2000);
        setLoading(false);

      } else {
        // Login
        if (!formData.farmerId || !formData.password) {
          setError('Farmer ID and password are required');
          setLoading(false);
          return;
        }

        const response = await fetch('http://localhost:8000/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            farmer_id: formData.farmerId.toUpperCase(),
            password: formData.password
          })
        });

        const data = await response.json();

        if (!response.ok) {
          const errorMessage = typeof data.detail === 'string' 
            ? data.detail 
            : (Array.isArray(data.detail) ? data.detail[0]?.msg : JSON.stringify(data.detail));
          setError(errorMessage || 'Invalid credentials');
          setLoading(false);
          return;
        }

        // Store session
        const userData = {
          ...data.user,
          session_id: data.session_id,
          authenticated: true
        };
        localStorage.setItem('farmer', JSON.stringify(userData));
        localStorage.setItem('session_id', data.session_id);

        onLogin(userData);
        setLoading(false);
      }
    } catch (err) {
      console.error('Error:', err);
      if (err.message === 'Failed to fetch') {
        setError('Cannot connect to server. Please ensure backend is running on http://localhost:8000');
      } else {
        setError('Connection error. Please ensure backend is running.');
      }
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    const demoFarmer = {
      farmerId: 'DEMO',
      name: 'Demo Farmer',
      language: 'en',
      authenticated: true,
      isDemo: true
    };
    localStorage.setItem('farmer', JSON.stringify(demoFarmer));
    onLogin(demoFarmer);
  };

  const translations = {
    en: {
      title: 'Smart Farming AI',
      subtitle: mode === 'login' ? 'Login to Your Farm Dashboard' : 'Register New Account',
      farmerId: 'Farmer ID',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      name: 'Full Name',
      email: 'Email (Optional)',
      phone: 'Phone Number (Optional)',
      language: 'Preferred Language',
      loginButton: 'Login to Dashboard',
      registerButton: 'Create Account',
      demoButton: 'Try Demo',
      switchToRegister: "Don't have an account? Register",
      switchToLogin: 'Already have an account? Login',
      or: 'OR',
      features: {
        title: 'AI-Powered Features',
        items: [
          '🌾 17 AI Agents for Smart Farming',
          '🌡️ Real-time Weather & Soil Monitoring',
          '💰 Market Price Predictions',
          '🌱 Disease Detection & Prevention',
          '⛓️ Blockchain Green Token Rewards',
          '🎤 Voice Assistant (Marathi/Hindi/English)'
        ]
      }
    },
    hi: {
      title: 'स्मार्ट फार्मिंग AI',
      subtitle: mode === 'login' ? 'अपने फार्म डैशबोर्ड में लॉगिन करें' : 'नया खाता बनाएं',
      farmerId: 'किसान ID',
      password: 'पासवर्ड',
      confirmPassword: 'पासवर्ड की पुष्टि करें',
      name: 'पूरा नाम',
      email: 'ईमेल (वैकल्पिक)',
      phone: 'फ़ोन नंबर (वैकल्पिक)',
      language: 'पसंदीदा भाषा',
      loginButton: 'डैशबोर्ड में लॉगिन करें',
      registerButton: 'खाता बनाएं',
      demoButton: 'डेमो आज़माएं',
      switchToRegister: 'खाता नहीं है? रजिस्टर करें',
      switchToLogin: 'पहले से खाता है? लॉगिन करें',
      or: 'या',
      features: {
        title: 'AI-Powered Smart Farming',
        items: [
          '🤖 10 Autonomous AI Agents',
          '🌡️ Real-time Weather & Soil Monitoring',
          '💰 Market Price Predictions',
          '🌱 Disease Detection & Prevention',
          '💧 Smart Irrigation Control',
          '🎤 Voice Assistant (Marathi/Hindi/English)'
        ]
      }
    },
    mr: {
      title: 'स्मार्ट फार्मिंग AI',
      subtitle: mode === 'login' ? 'तुमच्या फार्म डॅशबोर्डमध्ये लॉगिन करा' : 'नवीन खाते तयार करा',
      farmerId: 'शेतकरी ID',
      password: 'पासवर्ड',
      confirmPassword: 'पासवर्डची पुष्टी करा',
      name: 'पूर्ण नाव',
      email: 'ईमेल (पर्यायी)',
      phone: 'फोन नंबर (पर्यायी)',
      language: 'पसंतीची भाषा',
      loginButton: 'डॅशबोर्डमध्ये लॉगिन करा',
      registerButton: 'खाते तयार करा',
      demoButton: 'डेमो वापरा',
      switchToRegister: 'खाते नाही? नोंदणी करा',
      switchToLogin: 'आधीपासून खाते आहे? लॉगिन करा',
      or: 'किंवा',
      features: {
        title: 'AI-Powered Smart Farming',
        items: [
          '🤖 10 Autonomous AI Agents',
          '🌡️ Real-time Weather & Soil Monitoring',
          '💰 Market Price Predictions',
          '🌱 Disease Detection & Prevention',
          '💧 Smart Irrigation Control',
          '🎤 Voice Assistant (Marathi/Hindi/English)'
        ]
      }
    },
    hi: {
      title: 'स्मार्ट फार्मिंग AI',
      subtitle: mode === 'login' ? 'अपने फार्म डैशबोर्ड में लॉगिन करें' : 'नया खाता बनाएं',
      farmerId: 'किसान ID',
      password: 'पासवर्ड',
      confirmPassword: 'पासवर्ड की पुष्टि करें',
      name: 'पूरा नाम',
      email: 'ईमेल (वैकल्पिक)',
      phone: 'फ़ोन नंबर (वैकल्पिक)',
      language: 'पसंदीदा भाषा',
      loginButton: 'डैशबोर्ड में लॉगिन करें',
      registerButton: 'खाता बनाएं',
      demoButton: 'डेमो आज़माएं',
      switchToRegister: 'खाता नहीं है? रजिस्टर करें',
      switchToLogin: 'पहले से खाता है? लॉगिन करें',
      or: 'या',
      features: {
        title: 'AI-संचालित स्मार्ट खेती',
        items: [
          '🤖 10 स्वायत्र AI एजेंट',
          '🌡️ वास्तविक समय मौसम और मिट्टी निगरानी',
          '💰 बाजार मूल्य भविष्यवाणी',
          '🌱 रोग का पता लगाना और रोकथाम',
          '💧 स्मार्ट सिंचाई नियंत्रण',
          '🎤 वॉयस असिस्टेंट (मराठी/हिंदी/अंग्रेजी)'
        ]
      }
    },
    mr: {
      title: 'स्मार्ट फार्मिंग AI',
      subtitle: mode === 'login' ? 'तुमच्या फार्म डॅशबोर्डमध्ये लॉगिन करा' : 'नवीन खाते तयार करा',
      farmerId: 'शेतकरी ID',
      password: 'पासवर्ड',
      confirmPassword: 'पासवर्डची पुष्टी करा',
      name: 'पूर्ण नाव',
      email: 'ईमेल (पर्यायी)',
      phone: 'फोन नंबर (पर्यायी)',
      language: 'पसंतीची भाषा',
      loginButton: 'डॅशबोर्डमध्ये लॉगिन करा',
      registerButton: 'खाते तयार करा',
      demoButton: 'डेमो वापरा',
      switchToRegister: 'खाते नाही? नोंदणी करा',
      switchToLogin: 'आधीपासून खाते आहे? लॉगिन करा',
      or: 'किंवा',
      features: {
        title: 'AI-संचालित स्मार्ट शेती',
        items: [
          '🤖 10 स्वायत्त AI एजंट',
          '🌡️ रिअल-टाइम हवामान आणि माती निरीक्षण',
          '💰 बाजार किंमत अंदाज',
          '🌱 रोग शोध आणि प्रतिबंध',
          '💧 स्मार्ट सिंचाई नियंत्रण',
          '🎤 व्हॉइस असिस्टंट (मराठी/हिंदी/इंग्रजी)'
        ]
      }
    }
  };

  const t = translations[formData.language];

  return (
    <div className="login-container">
      <div className="login-left">
        <div className="login-branding">
          <div className="logo">
            <span className="logo-icon">🌾</span>
            <span className="logo-text">{t.title}</span>
          </div>
          <p className="tagline">{t.subtitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'register' && (
            <div className="form-group">
              <label>{t.name}</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ravi Kumar"
                className="form-input"
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label>{t.farmerId}</label>
            <input
              type="text"
              value={formData.farmerId}
              onChange={(e) => setFormData({ ...formData, farmerId: e.target.value.toUpperCase() })}
              placeholder="FARM001"
              className="form-input"
              disabled={loading}
            />
          </div>

          {mode === 'register' && (
            <>
              <div className="form-group">
                <label>{t.email}</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="farmer@example.com"
                  className="form-input"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>{t.phone}</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+919876543210"
                  className="form-input"
                  disabled={loading}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>{t.password}</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              className="form-input"
              disabled={loading}
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label>{t.confirmPassword}</label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="••••••••"
                className="form-input"
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label>{t.language}</label>
            <select
              value={formData.language}
              onChange={(e) => setFormData({ ...formData, language: e.target.value })}
              className="form-input"
              disabled={loading}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
            </select>
          </div>

          {error && <div className="error-message">❌ {error}</div>}
          {success && <div className="success-message">✅ {success}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? '⏳ Processing...' :
              mode === 'login' ? `🚀 ${t.loginButton}` : `✨ ${t.registerButton}`}
          </button>

          <div className="switch-mode">
            <button
              type="button"
              onClick={() => {
                setMode(mode === 'login' ? 'register' : 'login');
                setError('');
                setSuccess('');
              }}
              className="switch-button"
              disabled={loading}
            >
              {mode === 'login' ? t.switchToRegister : t.switchToLogin}
            </button>
          </div>

          {mode === 'login' && (
            <>
              <div className="divider">
                <span>{t.or}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button type="button" onClick={handleDemoLogin} className="demo-button" disabled={loading}>
                  ✨ {t.demoButton}
                </button>
                <button type="button" onClick={onAdminClick} className="demo-button" disabled={loading} style={{ background: '#374151', color: 'white', border: 'none' }}>
                  🛡️ Admin Portal
                </button>
              </div>
            </>
          )}
        </form>

        {mode === 'login' && (
          <div className="login-footer">
            <p>Need an account? Click "Register" above</p>
          </div>
        )}
      </div>

      <div className="login-right" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ 
          width: '100%', 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: 'url(https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920&h=1080&fit=crop) center/cover no-repeat'
        }}>
          <div style={{
            background: 'rgba(0,0,0,0.3)',
            padding: '40px',
            borderRadius: '20px',
            backdropFilter: 'blur(5px)'
          }}>
            <h1 style={{ 
              fontSize: '48px', 
              fontWeight: '800',
              color: 'white',
              textShadow: '0 4px 20px rgba(0,0,0,0.5)',
              margin: 0
            }}>
              AgroBrain OS
            </h1>
            <p style={{ 
              fontSize: '20px', 
              color: 'rgba(255,255,255,0.9)',
              marginTop: '10px'
            }}>
              AI-Powered Smart Farming
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
