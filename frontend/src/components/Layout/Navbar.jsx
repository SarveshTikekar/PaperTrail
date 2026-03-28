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
    <nav className="navbar glass-panel">
      <div className="navbar-brand">
        <Layers className="brand-icon" />
        <span className="brand-name text-gradient">PaperTrail</span>
      </div>
      
      <div className="navbar-links">
        <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Home size={18} /> <span>{t('dashboard')}</span>
        </NavLink>
        <NavLink to="/upload" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Upload size={18} /> <span>{t('upload')}</span>
        </NavLink>
        <NavLink to="/verify" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <FileCheck size={18} /> <span>{t('verify')}</span>
        </NavLink>
      </div>
      
      <div className="navbar-user" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-tertiary)', borderRadius: '20px', padding: '4px 12px' }}>
          <Globe size={14} style={{ marginRight: '6px', color: 'var(--text-secondary)' }} />
          <select 
            value={lang} 
            onChange={(e) => setLang(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontSize: '0.85rem' }}
          >
            <option value="en">EN</option>
            <option value="hi">HI</option>
            <option value="mr">MR</option>
          </select>
        </div>

        <button 
          onClick={toggleTheme} 
          className="btn-secondary" 
          style={{ padding: '8px', borderRadius: '50%', border: 'none' }}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div className="user-avatar" style={{ marginLeft: '8px' }}>AD</div>
      </div>
    </nav>
  );
}
