import React, { createContext, useState, useContext, useEffect } from 'react';
import { dashboardTranslations } from '../translations/dashboard';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('farmLanguage') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('farmLanguage', language);
  }, [language]);

  const t = (key) => {
    return dashboardTranslations[language]?.[key] || dashboardTranslations.en[key] || key;
  };

  const changeLanguage = (lang) => {
    if (['en', 'hi', 'mr'].includes(lang)) {
      setLanguage(lang);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
