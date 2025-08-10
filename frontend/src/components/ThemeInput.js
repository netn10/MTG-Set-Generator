import React from 'react';

const ThemeInput = ({ theme, setTheme, onGenerate, loading }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate();
  };

  const exampleThemes = [
    'Steampunk Inventors',
    'Underwater Civilization', 
    'Desert Nomads',
    'Haunted Library',
    'Sky Pirates',
    'Crystal Caves',
    'Time Travelers',
    'Mushroom Forest'
  ];

  return (
    <div className="theme-input-container">
      <form onSubmit={handleSubmit} className="theme-form">
        <div className="input-group">
          <label htmlFor="theme">Set Theme:</label>
          <input
            id="theme"
            type="text"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="Enter a theme (e.g., 'Steampunk Inventors')"
            disabled={loading}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !theme.trim()}
          className="generate-button"
        >
          {loading ? (() => {
            console.log(`🔴 Legacy UI: ThemeInput button showing "Generating..." (disabled)`);
            return 'Generating...';
          })() : (() => {
            console.log(`🟢 Legacy UI: ThemeInput button showing "Generate Commons" (enabled)`);
            return 'Generate Commons';
          })()}
        </button>
      </form>
      
      <div className="example-themes">
        <p>Example themes:</p>
        <div className="theme-tags">
          {exampleThemes.map((exampleTheme, index) => (
            <button
              key={index}
              className="theme-tag"
              onClick={() => setTheme(exampleTheme)}
              disabled={loading}
            >
              {exampleTheme}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ThemeInput;