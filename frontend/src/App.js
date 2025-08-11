import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import CardDisplay from './components/CardDisplay';
import ThemeInput from './components/ThemeInput';
import SetBuilder from './components/SetBuilder';
import Settings from './components/Settings';

function App() {
  const [currentView, setCurrentView] = useState('builder'); // Start with integrated builder
  const [theme, setTheme] = useState('');
  const [setConcept, setSetConcept] = useState(null);
  const [commons, setCommons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [darkMode, setDarkMode] = useState(true);
  const [apiKey, setApiKey] = useState('');

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const generateSet = async () => {
    if (!theme.trim()) {
      setError('Please enter a theme');
      return;
    }

    if (!apiKey.trim()) {
      setError('Please enter your OpenAI API key');
      return;
    }

    console.log(`🎯 Legacy Generator: Starting set generation for theme "${theme.trim()}"`);
    setLoading(true);
    setError('');
    const startTime = Date.now();
    
    try {
      console.log(`🚀 Legacy Generator: Sending API request...`);
      const response = await axios.post('/api/generate-set', {
        theme: theme.trim(),
        apiKey: apiKey.trim()
      });
      
      const generationTime = Date.now() - startTime;
      console.log(`✅ Legacy Generator: Set generated successfully in ${generationTime}ms`);
      console.log(`📦 Generated ${response.data.commons?.length || 0} commons`);
      
      setCommons(response.data.commons);
    } catch (err) {
      const generationTime = Date.now() - startTime;
      console.error(`❌ Legacy Generator: Generation failed after ${generationTime}ms:`, err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      setError(err.response?.data?.error || 'Failed to generate set');
    } finally {
      setLoading(false);
      console.log(`🏁 Legacy Generator: Process completed`);
    }
  };

  const handleConceptGenerated = (themeString, concept) => {
    console.log('🎨 Concept generated, updating integrated builder');
    console.log('📝 Theme:', themeString);
    console.log('🎯 Concept:', concept.name);
    
    setTheme(themeString);
    setSetConcept(concept);
  };

  return (
    <div className={`App ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <header className="App-header">
        <h1 style={{textAlign: 'center', marginBottom: '20px'}}>Magic: The Gathering Set Generator</h1>
        <p style={{marginBottom: '5px'}}>Professional set design using Mark Rosewater's skeleton framework</p>
        
        <nav className="app-nav">
          <button 
            className={currentView === 'builder' ? 'active' : ''}
            onClick={() => setCurrentView('builder')}
          >
            Set Builder
          </button>
          <button 
            className={currentView === 'legacy' ? 'active' : ''}
            onClick={() => setCurrentView('legacy')}
          >
            Quick Generator
          </button>
          <button 
            className={currentView === 'settings' ? 'active' : ''}
            onClick={() => setCurrentView('settings')}
          >
            Settings
          </button>
        </nav>
      </header>
      
      <main className="App-main">
        {/* API Key Input - Always visible */}
        <div className="api-key-section">
          <div className="api-key-input-container">
            <label htmlFor="api-key-input">OpenAI API Key:</label>
            <input
              id="api-key-input"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your OpenAI API key (sk-...)"
              className="api-key-input"
            />
            <small className="api-key-help">
              Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI Platform</a>
            </small>
          </div>
        </div>

        {currentView === 'builder' ? (
          <SetBuilder 
            initialTheme={theme}
            setConcept={setConcept}
            onConceptGenerated={handleConceptGenerated}
            darkMode={darkMode}
            apiKey={apiKey}
          />
        ) : currentView === 'settings' ? (
          <Settings 
            darkMode={darkMode}
            theme={theme}
            setTheme={setTheme}
            onGenerate={generateSet}
            loading={loading}
          />
        ) : (
          <>
            <ThemeInput 
              theme={theme}
              setTheme={setTheme}
              onGenerate={generateSet}
              loading={loading}
            />
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            {loading && (
              <div className="loading-message">
                {(() => {
                  console.log(`🎬 Legacy UI: Displaying "Generating..." message for theme "${theme}"`);
                  return `Generating your ${theme} set... This may take a moment.`;
                })()}
              </div>
            )}
            
            {commons.length > 0 && (
              <div className="cards-container">
                <h2>Generated Commons for "{theme}" Theme</h2>
                <div className="cards-grid">
                  {commons.map((card, index) => (
                    <CardDisplay key={index} card={card} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;