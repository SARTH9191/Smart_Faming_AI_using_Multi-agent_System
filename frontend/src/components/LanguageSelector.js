import React from 'react';
import { useLanguage } from '../context/LanguageContext';

const LanguageSelector = () => {
  const { language, changeLanguage } = useLanguage();

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी', flag: '🇮🇳' }
  ];

  return (
    <div style={{
      display: 'flex',
      gap: '8px',
      alignItems: 'center'
    }}>
      {languages.map(lang => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 12px',
            border: language === lang.code ? '2px solid #16a34a' : '2px solid #e5e7eb',
            borderRadius: '8px',
            background: language === lang.code 
              ? 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)' 
              : 'white',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            fontSize: '14px',
            fontWeight: language === lang.code ? '600' : '500',
            boxShadow: language === lang.code 
              ? '0 4px 12px rgba(22, 163, 74, 0.3)' 
              : 'none'
          }}
          onMouseOver={(e) => {
            if (language !== lang.code) {
              e.currentTarget.style.borderColor = '#2563eb';
              e.currentTarget.style.background = '#eff6ff';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseOut={(e) => {
            if (language !== lang.code) {
              e.currentTarget.style.borderColor = '#e5e7eb';
              e.currentTarget.style.background = 'white';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <span style={{ fontSize: '20px' }}>{lang.flag}</span>
          <span style={{ fontSize: '13px' }} className="lang-name">{lang.name}</span>
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
