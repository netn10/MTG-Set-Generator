import React from 'react';
import './Settings.css';

const Settings = ({ darkMode, onDarkModeToggle }) => {
  return (
    <div className={`settings-page ${darkMode ? 'dark-mode' : ''}`}>
      <div className="settings-container">
        <h2>Settings</h2>
        
        <div className="settings-section">
          <h3>Appearance</h3>
          
          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="dark-mode-setting">Dark Mode</label>
              <p className="setting-description">
                Toggle between light and dark themes for better visibility
              </p>
            </div>
            <div className="setting-control">
              <button 
                id="dark-mode-setting"
                className={`toggle-switch ${darkMode ? 'active' : ''}`}
                onClick={onDarkModeToggle}
                aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                <span className="toggle-slider">
                  <span className="toggle-icon">
                    {darkMode ? '🌙' : '☀️'}
                  </span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;