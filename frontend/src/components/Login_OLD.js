import React, { useState } from 'react';
import './Login.css';

function Login({ onLogin }) {
  const [formData, setFormData] = useState({
    farmerId: '',
    password: '',
    language: 'en'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulate login validation
    // In production, this would call your backend API
    setTimeout(() => {
      if (formData.farmerId && formData.password) {
        // Mock validation - In production, verify against backend
        if (formData.password.length >= 4) {
          const farmerData = {
            farmerId: formData.farmerId.toUpperCase(),
            name: `Farmer ${formData.farmerId}`,
            language: formData.language,
            authenticated: true
          };
          localStorage.setItem('farmer', JSON.stringify(farmerData));
          onLogin(farmerData);
        } else {
          setError('Password must be at least 4 characters');
          setLoading(false);
        }
      } else {
        setError('Please fill in all fields');
        setLoading(false);
      }
    }, 1000);
  };

  const handleDemoLogin = () => {
    const demoFarmer = {
      farmerId: 'FARM001',
      name: 'Demo Farmer',
      language: 'en',
      authenticated: true
    };
    localStorage.setItem('farmer', JSON.stringify(demoFarmer));
    onLogin(demoFarmer);
  };

  const translations = {
    en: {
      title: 'Smart Farming AI',
      subtitle: 'Login to Your Farm Dashboard',
      farmerId: 'Farmer ID',
      password: 'Password',
      language: 'Preferred Language',
      loginButton: 'Login to Dashboard',
      demoButton: 'Try Demo',
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
      subtitle: 'अपने फार्म डैशबोर्ड में लॉगिन करें',
      farmerId: 'किसान ID',
      password: 'पासवर्ड',
      language: 'पसंदीदा भाषा',
      loginButton: 'डैशबोर्ड में लॉगिन करें',
      demoButton: 'डेमो आज़माएं',
      or: 'या',
      features: {
        title: 'AI-संचालित सुविधाएं',
        items: [
          '🌾 स्मार्ट खेती के लिए 17 AI एजेंट',
          '🌡️ वास्तविक समय मौसम और मिट्टी निगरानी',
          '💰 बाजार मूल्य भविष्यवाणी',
          '🌱 रोग का पता लगाना और रोकथाम',
          '⛓️ ब्लॉकचेन ग्रीन टोकन पुरस्कार',
          '🎤 वॉयस असिस्टेंट (मराठी/हिंदी/अंग्रेजी)'
        ]
      }
    },
    mr: {
      title: 'स्मार्ट फार्मिंग AI',
      subtitle: 'तुमच्या फार्म डॅशबोर्डमध्ये लॉगिन करा',
      farmerId: 'शेतकरी ID',
      password: 'पासवर्ड',
      language: 'पसंतीची भाषा',
      loginButton: 'डॅशबोर्डमध्ये लॉगिन करा',
      demoButton: 'डेमो वापरा',
      or: 'किंवा',
      features: {
        title: 'AI-संचालित वैशिष्ट्ये',
        items: [
          '🌾 स्मार्ट शेतीसाठी 17 AI एजंट',
          '🌡️ रिअल-टाइम हवामान आणि माती निरीक्षण',
          '💰 बाजार किंमत अंदाज',
          '🌱 रोग शोध आणि प्रतिबंध',
          '⛓️ ब्लॉकचेन ग्रीन टोकन बक्षिसे',
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
          <div className="form-group">
            <label>{t.farmerId}</label>
            <input
              type="text"
              value={formData.farmerId}
              onChange={(e) => setFormData({...formData, farmerId: e.target.value.toUpperCase()})}
              placeholder="FARM001"
              className="form-input"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>{t.password}</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              placeholder="••••••••"
              className="form-input"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>{t.language}</label>
            <select
              value={formData.language}
              onChange={(e) => setFormData({...formData, language: e.target.value})}
              className="form-input"
              disabled={loading}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? '⏳ Logging in...' : `🚀 ${t.loginButton}`}
          </button>

          <div className="divider">
            <span>{t.or}</span>
          </div>

          <button type="button" onClick={handleDemoLogin} className="demo-button" disabled={loading}>
            ✨ {t.demoButton}
          </button>
        </form>

        <div className="login-footer">
          <p>Demo: <strong>FARM001</strong> / <strong>demo</strong></p>
        </div>
      </div>

      <div className="login-right">
        <div className="features-section">
          <h2>{t.features.title}</h2>
          <ul className="features-list">
            {t.features.items.map((feature, index) => (
              <li key={index} className="feature-item">
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Login;
