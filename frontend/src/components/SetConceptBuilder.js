import React, { useState } from 'react';
import axios from 'axios';
import './SetConceptBuilder.css';

const SetConceptBuilder = ({ onConceptGenerated, darkMode }) => {
  const [pitch, setPitch] = useState('');
  const [concept, setConcept] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);

  const generateConcept = async () => {
    if (!pitch.trim()) {
      alert('Please enter a pitch for your set');
      return;
    }

    setLoading(true);
    try {
      console.log('🎯 Generating set concept from pitch:', pitch);
      const response = await axios.post('/api/generate-set-concept', {
        pitch: pitch.trim()
      });

      console.log('✅ Set concept generated:', response.data.concept.name);
      
      // Ensure we have exactly 10 archetypes for all color pairs
      const ensureAllArchetypes = (concept) => {
        const requiredColorPairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'];
        const existingColors = concept.archetypes.map(arch => arch.colors);
        const missingColors = requiredColorPairs.filter(pair => !existingColors.includes(pair));
        
        const colorPairNames = {
          'WU': 'Control', 'UB': 'Mill', 'BR': 'Aggro', 'RG': 'Ramp', 'GW': 'Tokens',
          'WB': 'Lifegain', 'UR': 'Spells', 'BG': 'Graveyard', 'RW': 'Equipment', 'GU': 'Flash'
        };
        
        // Add missing archetypes with placeholder names
        const additionalArchetypes = missingColors.map(colors => ({
          colors,
          name: `${colorPairNames[colors]} Archetype`,
          description: `A ${colors} archetype that fits the ${concept.name} theme.`,
          key_cards: []
        }));
        
        return {
          ...concept,
          archetypes: [...concept.archetypes, ...additionalArchetypes]
        };
      };
      
      const completeConceptData = ensureAllArchetypes(response.data.concept);
      setConcept(completeConceptData);
    } catch (error) {
      console.error('❌ Failed to generate set concept:', error);
      alert('Failed to generate set concept: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const updateConcept = (field, value) => {
    setConcept(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateArchetype = (index, field, value) => {
    setConcept(prev => ({
      ...prev,
      archetypes: prev.archetypes.map((arch, i) => 
        i === index ? { ...arch, [field]: value } : arch
      )
    }));
  };

  const addArchetype = () => {
    const colorPairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'];
    const usedColors = concept.archetypes.map(arch => arch.colors);
    const availableColors = colorPairs.filter(pair => !usedColors.includes(pair));
    
    setConcept(prev => ({
      ...prev,
      archetypes: [...prev.archetypes, {
        colors: availableColors[0] || '',
        name: '',
        description: '',
        key_cards: []
      }]
    }));
  };

  const removeArchetype = (index) => {
    setConcept(prev => ({
      ...prev,
      archetypes: prev.archetypes.filter((_, i) => i !== index)
    }));
  };

  const validateArchetypes = () => {
    const requiredColorPairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'];
    const presentColors = concept.archetypes.map(arch => arch.colors);
    const missingColors = requiredColorPairs.filter(pair => !presentColors.includes(pair));
    return { isValid: missingColors.length === 0, missingColors };
  };

  const proceedToCardGeneration = () => {
    if (concept) {
      const validation = validateArchetypes();
      if (!validation.isValid) {
        alert(`Missing archetypes for color pairs: ${validation.missingColors.join(', ')}. Please ensure all 10 two-color pairs are covered.`);
        return;
      }
      
      // Create a comprehensive theme string from the concept
      const themeString = `${concept.name}: ${concept.description}. Key mechanics: ${concept.mechanics.join(', ')}. Archetypes: ${concept.archetypes.map(a => `${a.colors} ${a.name} (${a.description})`).join('; ')}`;
      onConceptGenerated(themeString, concept);
    }
  };

  return (
    <div className={`set-concept-builder ${darkMode ? 'dark-mode' : ''}`}>
      <div className="concept-header">
        <h2>Set Concept Builder</h2>
        <p>Describe your set idea and let AI generate a full concept with archetypes</p>
      </div>

      {!concept ? (
        <div className="pitch-input-section">
          <div className="pitch-input">
            <label htmlFor="pitch">Set Pitch:</label>
            <textarea
              id="pitch"
              value={pitch}
              onChange={(e) => setPitch(e.target.value)}
              placeholder="Describe your set idea... (e.g., 'A steampunk world where inventors compete to build the greatest machines, featuring artifact synergies and innovation mechanics')"
              rows={4}
              disabled={loading}
            />
          </div>
          
          <button 
            className="generate-concept-button"
            onClick={generateConcept}
            disabled={loading || !pitch.trim()}
          >
            {loading ? 'Generating Concept...' : 'Generate Set Concept'}
          </button>
        </div>
      ) : (
        <div className="concept-display">
          <div className="concept-actions">
            <button 
              className="edit-toggle-button"
              onClick={() => setEditMode(!editMode)}
            >
              {editMode ? 'View Mode' : 'Edit Mode'}
            </button>
            <button 
              className="new-concept-button"
              onClick={() => {
                setConcept(null);
                setPitch('');
                setEditMode(false);
              }}
            >
              New Concept
            </button>
            <button 
              className="proceed-button"
              onClick={proceedToCardGeneration}
            >
              Use This Concept →
            </button>
          </div>

          <div className="concept-content">
            <div className="concept-field">
              <h3>Set Name</h3>
              {editMode ? (
                <input
                  type="text"
                  value={concept.name}
                  onChange={(e) => updateConcept('name', e.target.value)}
                  className="edit-input"
                />
              ) : (
                <p className="concept-name">{concept.name}</p>
              )}
            </div>

            <div className="concept-field">
              <h3>Description</h3>
              {editMode ? (
                <textarea
                  value={concept.description}
                  onChange={(e) => updateConcept('description', e.target.value)}
                  rows={4}
                  className="edit-textarea"
                />
              ) : (
                <p className="concept-description">{concept.description}</p>
              )}
            </div>

            <div className="concept-field">
              <h3>Key Mechanics</h3>
              {editMode ? (
                <div className="mechanics-edit">
                  {concept.mechanics.map((mechanic, index) => (
                    <div key={index} className="mechanic-edit">
                      <input
                        type="text"
                        value={mechanic}
                        onChange={(e) => {
                          const newMechanics = [...concept.mechanics];
                          newMechanics[index] = e.target.value;
                          updateConcept('mechanics', newMechanics);
                        }}
                        className="edit-input"
                      />
                      <button 
                        onClick={() => {
                          const newMechanics = concept.mechanics.filter((_, i) => i !== index);
                          updateConcept('mechanics', newMechanics);
                        }}
                        className="remove-button"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <button 
                    onClick={() => updateConcept('mechanics', [...concept.mechanics, ''])}
                    className="add-button"
                  >
                    + Add Mechanic
                  </button>
                </div>
              ) : (
                <ul className="mechanics-list">
                  {concept.mechanics.map((mechanic, index) => (
                    <li key={index}>{mechanic}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="concept-field">
              <h3>Draft Archetypes</h3>
              {concept.archetypes && (
                <div className="archetype-status">
                  <div className="color-pair-tracker">
                    {['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'].map(pair => {
                      const hasArchetype = concept.archetypes.some(arch => arch.colors === pair);
                      return (
                        <span 
                          key={pair} 
                          className={`color-pair-indicator ${hasArchetype ? 'present' : 'missing'}`}
                          title={hasArchetype ? `${pair} archetype present` : `${pair} archetype missing`}
                        >
                          {pair}
                        </span>
                      );
                    })}
                  </div>
                  <div className="archetype-count">
                    {concept.archetypes.length}/10 archetypes
                  </div>
                </div>
              )}
              {editMode ? (
                <div className="archetypes-edit">
                  {concept.archetypes.map((archetype, index) => (
                    <div key={index} className="archetype-edit">
                      <div className="archetype-header">
                        <select
                          value={archetype.colors}
                          onChange={(e) => updateArchetype(index, 'colors', e.target.value)}
                          className="colors-input"
                        >
                          <option value="">Select Colors</option>
                          {['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'].map(pair => (
                            <option key={pair} value={pair}>{pair}</option>
                          ))}
                        </select>
                        <input
                          type="text"
                          value={archetype.name}
                          onChange={(e) => updateArchetype(index, 'name', e.target.value)}
                          placeholder="Archetype Name"
                          className="name-input"
                        />
                        <button 
                          onClick={() => removeArchetype(index)}
                          className="remove-button"
                        >
                          ×
                        </button>
                      </div>
                      <textarea
                        value={archetype.description}
                        onChange={(e) => updateArchetype(index, 'description', e.target.value)}
                        placeholder="Archetype description..."
                        rows={2}
                        className="edit-textarea"
                      />
                    </div>
                  ))}
                  <div className="archetype-actions">
                    <button 
                      onClick={addArchetype}
                      className="add-button"
                      disabled={concept.archetypes.length >= 10}
                    >
                      + Add Archetype
                    </button>
                    <button 
                      onClick={() => {
                        const requiredColorPairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'];
                        const existingColors = concept.archetypes.map(arch => arch.colors);
                        const missingColors = requiredColorPairs.filter(pair => !existingColors.includes(pair));
                        
                        const colorPairNames = {
                          'WU': 'Control', 'UB': 'Mill', 'BR': 'Aggro', 'RG': 'Ramp', 'GW': 'Tokens',
                          'WB': 'Lifegain', 'UR': 'Spells', 'BG': 'Graveyard', 'RW': 'Equipment', 'GU': 'Flash'
                        };
                        
                        const newArchetypes = missingColors.map(colors => ({
                          colors,
                          name: `${colorPairNames[colors]} Archetype`,
                          description: `A ${colors} archetype that fits the ${concept.name} theme.`,
                          key_cards: []
                        }));
                        
                        setConcept(prev => ({
                          ...prev,
                          archetypes: [...prev.archetypes, ...newArchetypes]
                        }));
                      }}
                      className="fill-button"
                      disabled={concept.archetypes.length >= 10}
                    >
                      Fill Missing Archetypes
                    </button>
                  </div>
                </div>
              ) : (
                <div className="archetypes-display">
                  {concept.archetypes.map((archetype, index) => (
                    <div key={index} className="archetype-card">
                      <div className="archetype-header">
                        <span className="archetype-colors">{archetype.colors}</span>
                        <span className="archetype-name">{archetype.name}</span>
                      </div>
                      <p className="archetype-description">{archetype.description}</p>
                      {archetype.key_cards && archetype.key_cards.length > 0 && (
                        <div className="key-cards">
                          <strong>Key Cards:</strong> {archetype.key_cards.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {concept.flavor_themes && (
              <div className="concept-field">
                <h3>Flavor Themes</h3>
                <ul className="flavor-themes">
                  {concept.flavor_themes.map((theme, index) => (
                    <li key={index}>{theme}</li>
                  ))}
                </ul>
              </div>
            )}

            {concept.design_notes && (
              <div className="concept-field">
                <h3>Design Notes</h3>
                <p className="design-notes">{concept.design_notes}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SetConceptBuilder;