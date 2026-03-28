import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Upload, FileCheck, Layers, Moon, Sun, Globe } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import './Navbar.css';

export default function Navbar() {
  const [theme, setTheme] = useState('dark');
  const { lang, setLang, t } = useLanguage();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Layers className="brand-icon" />
        <span className="brand-name text-gradient">
          <span className="brand-name-light">Paper</span>Trail
        </span>
      </div>
      
      <div className="navbar-links">
        <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"} end>
          <Home size={15} /> <span>{t('dashboard')}</span>
        </NavLink>
        <NavLink to="/upload" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Upload size={15} /> <span>{t('upload')}</span>
        </NavLink>
        <NavLink to="/verify" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <FileCheck size={15} /> <span>{t('verify')}</span>
        </NavLink>
      </div>
      
      <div className="navbar-user" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <div className="lang-switcher">
          <Globe size={13} style={{ color: 'var(--text-tertiary)' }} />
          <select 
            value={lang} 
            onChange={(e) => setLang(e.target.value)}
          >
            <option value="en">EN</option>
            <option value="hi">HI</option>
            <option value="mr">MR</option>
          </select>
        </div>

        <button 
          onClick={toggleTheme} 
          className="theme-toggle"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </button>
        <div className="user-avatar">AD</div>
      </div>
    </nav>
  );
}
