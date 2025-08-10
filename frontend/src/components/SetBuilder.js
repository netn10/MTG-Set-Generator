import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './SetBuilder.css';
import './SetConceptBuilder.css';
import { useSocket } from '../hooks/useSocket';

const SetBuilder = ({ initialTheme = '', initialConcept = null, onConceptGenerated, darkMode: parentDarkMode }) => {
  const [skeleton, setSkeleton] = useState(null);
  const [currentSet, setCurrentSet] = useState({});
  const [theme, setTheme] = useState(initialTheme);
  const [selectedColor, setSelectedColor] = useState('white');
  // const [selectedRarity, setSelectedRarity] = useState('common');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [setType, setSetType] = useState('full'); // 'full' or 'commons'
  const [cardCounts, setCardCounts] = useState({ full: 271, commons: 102 }); // Default counts, will be updated when skeleton loads
  const [darkMode, setDarkMode] = useState(parentDarkMode !== undefined ? parentDarkMode : true);
  const [useParallel] = useState(true); // Always use parallel processing
  const [useStreaming] = useState(true); // Always use streaming for immediate card display
  const [useUltraFast] = useState(true); // Always use ultra-fast mega batch processing
  const [useBatched50] = useState(true); // Always use batched-50 processing for seamless updates
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0, batchTime: 0 });
  const [websocketStats, setWebsocketStats] = useState({ received: 0, processed: 0 });
  
  // Concept Builder state
  const [showConceptBuilder, setShowConceptBuilder] = useState(!initialConcept && !initialTheme);
  const [pitch, setPitch] = useState('');
  const [concept, setConcept] = useState(initialConcept);
  const [conceptLoading, setConceptLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // WebSocket hook for real-time card updates
  const { isConnected, connectionError, reconnectAttempts, maxReconnectAttempts, reconnect, onCardGenerated, offCardGenerated, onBatchCompleted, offBatchCompleted } = useSocket();

  // Handle real-time card updates via WebSocket
  const handleCardGenerated = useCallback((cardData) => {
    console.log('🎉 Real-time card received:', cardData.card.name);
    console.log('📍 Card location:', cardData.color, cardData.rarity, cardData.slot_id);
    console.log('📦 Full card data:', cardData);
    
    // Update WebSocket stats
    setWebsocketStats(prev => ({
      received: prev.received + 1,
      processed: prev.processed + 1
    }));
    
    setCurrentSet(prevSet => {
      console.log('🔄 Updating currentSet state with new card');
      console.log('📊 Previous state keys:', Object.keys(prevSet));
      
      const updatedSet = { ...prevSet };
      if (!updatedSet[cardData.color]) {
        console.log(`➕ Creating new color section: ${cardData.color}`);
        updatedSet[cardData.color] = {};
      }
      if (!updatedSet[cardData.color][cardData.rarity]) {
        console.log(`➕ Creating new rarity section: ${cardData.color}.${cardData.rarity}`);
        updatedSet[cardData.color][cardData.rarity] = {};
      }
      
      // Mark the card as newly generated for animation
      const newCard = { ...cardData.card, isNew: true };
      updatedSet[cardData.color][cardData.rarity][cardData.slot_id] = newCard;
      console.log(`✅ Card ${cardData.card.name} added to slot ${cardData.slot_id}`);
      
      // Remove the isNew flag after animation duration
      setTimeout(() => {
        setCurrentSet(currentSet => {
          const updated = { ...currentSet };
          if (updated[cardData.color]?.[cardData.rarity]?.[cardData.slot_id]) {
            updated[cardData.color][cardData.rarity][cardData.slot_id] = { 
              ...updated[cardData.color][cardData.rarity][cardData.slot_id], 
              isNew: false 
            };
          }
          return updated;
        });
      }, 2000); // 2 seconds animation
      
      // Update progress
      updateProgress(updatedSet);
      return updatedSet;
    });
  }, []);

  // Handle batch completion updates via WebSocket
  const handleBatchCompleted = useCallback((batchData) => {
    console.log(`🎯 Batch ${batchData.batch_number}/${batchData.total_batches} completed in ${batchData.batch_time.toFixed(2)}s`);
    console.log(`📊 Overall progress: ${batchData.cards_completed}/${batchData.total_cards} cards`);
    
    setBatchProgress({
      current: batchData.batch_number,
      total: batchData.total_batches,
      batchTime: batchData.batch_time,
      cardsCompleted: batchData.cards_completed,
      totalCards: batchData.total_cards
    });
  }, []);

  // Subscribe to WebSocket events
  useEffect(() => {
    console.log('🔌 WebSocket subscription effect triggered', { isConnected });
    
    if (isConnected) {
      console.log('🔌 WebSocket connected, subscribing to events');
      onCardGenerated(handleCardGenerated);
      onBatchCompleted(handleBatchCompleted);
    }

    return () => {
      console.log('🧹 Cleaning up WebSocket subscriptions');
      offCardGenerated(handleCardGenerated);
      offBatchCompleted(handleBatchCompleted);
    };
  }, [isConnected, handleBatchCompleted, handleCardGenerated, offBatchCompleted, offCardGenerated, onBatchCompleted, onCardGenerated]);

  // Initialize current set with empty slots
  const initializeCurrentSet = useCallback((skeletonData) => {
    const initialSet = {};
    
    // Initialize all slots as empty
    Object.keys(skeletonData).forEach(colorName => {
      initialSet[colorName] = {};
      
      if (colorName === 'multicolor' || colorName === 'colorless' || colorName === 'lands') {
        Object.keys(skeletonData[colorName]).forEach(rarity => {
          initialSet[colorName][rarity] = {};
          skeletonData[colorName][rarity].forEach(slot => {
            initialSet[colorName][rarity][slot.id] = null;
          });
        });
      } else {
        Object.keys(skeletonData[colorName]).forEach(rarity => {
          initialSet[colorName][rarity] = {};
          
          if (typeof skeletonData[colorName][rarity] === 'object' && !Array.isArray(skeletonData[colorName][rarity])) {
            Object.keys(skeletonData[colorName][rarity]).forEach(cardType => {
              if (Array.isArray(skeletonData[colorName][rarity][cardType])) {
                skeletonData[colorName][rarity][cardType].forEach(slot => {
                  initialSet[colorName][rarity][slot.id] = null;
                });
              }
            });
          } else if (Array.isArray(skeletonData[colorName][rarity])) {
            skeletonData[colorName][rarity].forEach(slot => {
              initialSet[colorName][rarity][slot.id] = null;
            });
          }
        });
      }
    });
    
    setCurrentSet(initialSet);
    updateProgress(initialSet);
  }, []);

  // Load skeleton data from API
  const loadSkeleton = useCallback(async () => {
    try {
      const endpoint = setType === 'commons' ? '/api/skeleton/commons' : '/api/skeleton';
      const response = await axios.get(endpoint);
      setSkeleton(response.data);
      
      // Calculate actual card count for this skeleton
      const actualCount = calculateCardCount(response.data);
      setCardCounts(prev => ({
        ...prev,
        [setType]: actualCount
      }));
      
      initializeCurrentSet(response.data);
    } catch (error) {
      console.error('Failed to load skeleton:', error);
    }
  }, [setType, initializeCurrentSet]);

  useEffect(() => {
    loadSkeleton();
    // Load dark mode preference from localStorage, defaulting to true (dark mode)
    const savedDarkMode = localStorage.getItem('darkMode');
    setDarkMode(savedDarkMode !== null ? savedDarkMode === 'true' : true);
  }, [loadSkeleton]);

  // Update theme when initialTheme changes
  useEffect(() => {
    if (initialTheme && initialTheme !== theme) {
      setTheme(initialTheme);
      setShowConceptBuilder(false);
      console.log('🎨 SetBuilder: Updated theme from concept:', initialTheme);
    }
  }, [initialTheme, theme]);

  // Update concept when initialConcept changes
  useEffect(() => {
    if (initialConcept && initialConcept !== concept) {
      setConcept(initialConcept);
      setShowConceptBuilder(false);
      console.log('🎯 SetBuilder: Updated concept:', initialConcept.name);
    }
  }, [initialConcept, concept]);

  // Update dark mode when parent changes
  useEffect(() => {
    if (parentDarkMode !== undefined) {
      setDarkMode(parentDarkMode);
    }
  }, [parentDarkMode]);

  useEffect(() => {
    // Apply dark mode class to body
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Log loading state changes
  useEffect(() => {
    if (loading) {
      console.log(`🔄 GENERATION STATE: Loading started`);
      console.log(`🎯 Current progress: ${progress.completed}/${progress.total} cards`);
      console.log(`📝 Theme: "${theme}"`);
      console.log(`🎨 Set type: ${setType}`);
    } else {
      console.log(`⏸️  GENERATION STATE: Loading stopped`);
      console.log(`🏁 Final progress: ${progress.completed}/${progress.total} cards`);
    }
  }, [loading, progress.completed, progress.total, setType, theme]);

  // Log progress changes
  useEffect(() => {
    console.log(`📈 PROGRESS CHANGE: ${progress.completed}/${progress.total} cards`);
    if (progress.total > 0) {
      const percentage = Math.round((progress.completed / progress.total) * 100);
      console.log(`📊 Completion: ${percentage}%`);
    }
  }, [progress.completed, progress.total]);

  const calculateCardCount = (skeletonData) => {
    let total = 0;
    
    Object.values(skeletonData).forEach(colorData => {
      if (Array.isArray(colorData)) {
        // Handle colorless format (direct array)
        total += colorData.length;
      } else if (typeof colorData === 'object') {
        // Handle regular color format (nested objects)
        Object.values(colorData).forEach(rarityData => {
          if (Array.isArray(rarityData)) {
            // Direct array of cards
            total += rarityData.length;
          } else if (typeof rarityData === 'object') {
            // Nested structure (creatures, spells, etc.)
            Object.values(rarityData).forEach(cardTypeData => {
              if (Array.isArray(cardTypeData)) {
                total += cardTypeData.length;
              }
            });
          }
        });
      }
    });
    
    return total;
  };



  // Load both skeleton counts on component mount
  useEffect(() => {
    const loadInitialCounts = async () => {
      try {
        // Load full set count
        const fullResponse = await axios.get('/api/skeleton');
        const fullCount = calculateCardCount(fullResponse.data);
        
        // Load commons count  
        const commonsResponse = await axios.get('/api/skeleton/commons');
        const commonsCount = calculateCardCount(commonsResponse.data);
        
        setCardCounts({ full: fullCount, commons: commonsCount });
      } catch (error) {
        console.error('Failed to load initial card counts:', error);
      }
    };
    
    loadInitialCounts();
  }, []);

  // Reload skeleton when set type changes
  useEffect(() => {
    if (setType) {
      loadSkeleton();
    }
  }, [setType, loadSkeleton]);



  const updateProgress = (setData) => {
    let completed = 0;
    let total = 0;
    
    Object.values(setData).forEach(colorData => {
      Object.values(colorData).forEach(rarityData => {
        Object.values(rarityData).forEach(card => {
          total++;
          if (card !== null) completed++;
        });
      });
    });
    
    // Ensure we don't divide by zero
    if (total === 0) {
      console.log(`📊 Progress update: 0/0 cards (empty set)`);
      setProgress({ completed: 0, total: 0 });
    } else {
      const percentage = Math.round((completed / total) * 100);
      console.log(`📊 Progress update: ${completed}/${total} cards (${percentage}%) - ${total - completed} remaining`);
      setProgress({ completed, total });
    }
  };

  // Concept Builder methods
  const generateConcept = async () => {
    if (!pitch.trim()) {
      alert('Please enter a pitch for your set');
      return;
    }

    setConceptLoading(true);
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
      setConceptLoading(false);
    }
  };

  const updateConcept = (field, value) => {
    setConcept(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // const updateArchetype = (index, field, value) => {
  //   setConcept(prev => ({
  //     ...prev,
  //     archetypes: prev.archetypes.map((arch, i) => 
  //       i === index ? { ...arch, [field]: value } : arch
  //     )
  //   }));
  // };

  const proceedToCardGeneration = () => {
    if (concept) {
      const requiredColorPairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'UR', 'BG', 'RW', 'GU'];
      const presentColors = concept.archetypes.map(arch => arch.colors);
      const missingColors = requiredColorPairs.filter(pair => !presentColors.includes(pair));
      
      if (missingColors.length > 0) {
        alert(`Missing archetypes for color pairs: ${missingColors.join(', ')}. Please ensure all 10 two-color pairs are covered.`);
        return;
      }
      
      // Create a comprehensive theme string from the concept
      const themeString = `${concept.name}: ${concept.description}. Key mechanics: ${concept.mechanics.join(', ')}. Archetypes: ${concept.archetypes.map(a => `${a.colors} ${a.name} (${a.description})`).join('; ')}`;
      setTheme(themeString);
      setShowConceptBuilder(false);
      
      // Notify parent if callback provided
      if (onConceptGenerated) {
        onConceptGenerated(themeString, concept);
      }
    }
  };

  const generateCard = async (slotId, colorName, rarity, slotData) => {
    if (!theme.trim()) {
      alert('Please enter a theme first');
      return;
    }

    console.log(`🎯 Starting card generation for slot ${slotId} (${colorName} ${rarity})`);
    console.log(`📝 Theme: "${theme.trim()}"`);
    console.log(`🔧 Slot data:`, slotData);
    
    setLoading(true);
    const startTime = Date.now();
    
    try {
      console.log(`🚀 Sending API request for card ${slotId}...`);
      const response = await axios.post('/api/generate-card', {
        theme: theme.trim(),
        color: colorName,
        rarity: rarity,
        slot_id: slotId,
        slot_data: slotData
      });
      
      const generationTime = Date.now() - startTime;
      console.log(`✅ Card generated successfully in ${generationTime}ms:`, response.data.card.name);
      
      const newSet = { ...currentSet };
      newSet[colorName][rarity][slotId] = response.data.card;
      setCurrentSet(newSet);
      updateProgress(newSet);
      
      console.log(`📊 Progress updated: ${progress.completed + 1}/${progress.total} cards`);
      
    } catch (error) {
      const generationTime = Date.now() - startTime;
      console.error(`❌ Failed to generate card ${slotId} after ${generationTime}ms:`, error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      alert('Failed to generate card: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      console.log(`🏁 Card generation process completed for ${slotId}`);
    }
  };

  const generateAllCardsStreaming = async () => {
    if (!theme.trim()) {
      alert('Please enter a theme first');
      return;
    }

    console.log(`🔥 Starting STREAMING SET generation!`);
    console.log(`📝 Theme: "${theme.trim()}"`);
    console.log(`🎯 Set type: ${setType}`);

    setLoading(true);
    const startTime = Date.now();
    
    // Reset current set and progress
    const newSet = { ...currentSet };
    Object.keys(newSet).forEach(color => {
      Object.keys(newSet[color]).forEach(rarity => {
        Object.keys(newSet[color][rarity]).forEach(slotId => {
          newSet[color][rarity][slotId] = null;
        });
      });
    });
    setCurrentSet(newSet);
    setProgress({ completed: 0, total: progress.total });
    
    try {
      // Use fetch with streaming for POST requests with body
      const response = await fetch('/api/generate-set-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: theme.trim(),
          set_type: setType,
          use_parallel: useParallel
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'card') {
                console.log(`✅ Received card: ${data.card.name} (${data.color} ${data.rarity})`);
                
                // Update the current set with the new card using functional update
                setCurrentSet(prevSet => {
                  const updatedSet = { ...prevSet };
                  if (!updatedSet[data.color]) updatedSet[data.color] = {};
                  if (!updatedSet[data.color][data.rarity]) updatedSet[data.color][data.rarity] = {};
                  updatedSet[data.color][data.rarity][data.slot_id] = data.card;
                  
                  // Update progress with the new set
                  updateProgress(updatedSet);
                  return updatedSet;
                });
                
              } else if (data.type === 'status') {
                console.log(`📢 Status: ${data.message}`);
              } else if (data.type === 'complete') {
                console.log(`🎉 Generation complete!`);
                break;
              } else if (data.type === 'error') {
                console.error(`❌ Error: ${data.message}`);
                if (data.slot_id) {
                  console.error(`   Slot: ${data.slot_id} (${data.color} ${data.rarity})`);
                }
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      const generationTime = Date.now() - startTime;
      console.log(`🎉 STREAMING GENERATION COMPLETE in ${(generationTime / 1000).toFixed(1)}s!`);
      
    } catch (error) {
      const generationTime = Date.now() - startTime;
      console.error(`💥 STREAMING GENERATION FAILED after ${(generationTime / 1000).toFixed(1)}s:`, error);
      alert('Failed to generate set: ' + error.message);
    } finally {
      setLoading(false);
      console.log(`🏁 Streaming generation process completed`);
    }
  };

  const generateAllCards = async () => {
    if (!theme.trim()) {
      alert('Please enter a theme first');
      return;
    }

    console.log(`🔥 Starting FULL SET generation!`);
    console.log(`📝 Theme: "${theme.trim()}"`);
    console.log(`🎯 Set type: ${setType}`);
    console.log(`📊 Target: ${progress.total} total cards`);
    console.log(`📊 Current set state before generation:`, Object.keys(currentSet).map(color => `${color}: ${Object.keys(currentSet[color] || {}).length} rarities`));

    setLoading(true);
    const startTime = Date.now();
    
    // Reset WebSocket stats for this generation
    setWebsocketStats({ received: 0, processed: 0 });
    
    // Reset progress and batch progress to show generation is starting
    setProgress({ completed: 0, total: progress.total });
    setBatchProgress({ current: 0, total: 0, batchTime: 0 });
    console.log(`🔄 Progress reset to 0/${progress.total}`);
    
    try {
      let endpoint;
      let processingMode;
      
      if (useBatched50) {
        // Use batched-50 endpoints for seamless real-time updates
        endpoint = setType === 'commons' ? '/api/generate-commons-only-batched-50' : '/api/generate-full-set-batched-50';
        processingMode = 'BATCHED-50';
      } else if (useUltraFast) {
        // Use ultra-fast endpoints for maximum speed
        endpoint = setType === 'commons' ? '/api/generate-commons-only-ultra-fast' : '/api/generate-full-set-ultra-fast';
        processingMode = 'ULTRA-FAST';
      } else if (useParallel) {
        endpoint = setType === 'commons' ? '/api/generate-commons-only-parallel' : '/api/generate-full-set-parallel';
        processingMode = 'PARALLEL';
      } else {
        endpoint = setType === 'commons' ? '/api/generate-commons-only' : '/api/generate-full-set';
        processingMode = 'SEQUENTIAL';
      }
      
      console.log(`🚀 Sending ${processingMode} bulk generation request to ${endpoint}...`);
      console.log(`⏱️  This will generate cards in ${useBatched50 ? 'batches of 50 with real-time updates' : (useUltraFast ? 'ultra-fast mode' : 'standard mode')} for ${progress.total} cards...`);
      console.log(`🔧 Using batched-50: ${useBatched50}, ultra-fast: ${useUltraFast}, parallel: ${useParallel}`);
      console.log(`🌐 WebSocket connected: ${isConnected}`);
      console.log(`📡 Real-time updates expected: ${useBatched50 && isConnected}`);
      
      const response = await axios.post(endpoint, {
        theme: theme.trim(),
        use_parallel: useParallel
      });
      
      const generationTime = Date.now() - startTime;
      const speedNote = useBatched50 ? ' (BATCHED-50 MODE)' : (useUltraFast ? ' (ULTRA-FAST MODE)' : '');
      console.log(`🎉 FULL SET GENERATION COMPLETE in ${(generationTime / 1000).toFixed(1)}s${speedNote}!`);
      console.log(`📦 Generated set structure:`, Object.keys(response.data.set));
      
      // Count total cards generated
      let totalGenerated = 0;
      Object.values(response.data.set).forEach(colorData => {
        Object.values(colorData).forEach(rarityData => {
          Object.values(rarityData).forEach(card => {
            if (card !== null) totalGenerated++;
          });
        });
      });
      
      console.log(`✅ Successfully generated ${totalGenerated} cards for "${theme.trim()}" theme`);
      
      // Only update the set if we're not using batched-50 (which updates in real-time)
      if (!useBatched50) {
        setCurrentSet(response.data.set);
        updateProgress(response.data.set);
      }
      
    } catch (error) {
      const generationTime = Date.now() - startTime;
      console.error(`💥 FULL SET GENERATION FAILED after ${(generationTime / 1000).toFixed(1)}s:`, error);
      console.error('Full error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url
      });
      alert('Failed to generate set: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      console.log(`🏁 Bulk generation process completed`);
    }
  };

  const clearCard = (slotId, colorName, rarity) => {
    const newSet = { ...currentSet };
    newSet[colorName][rarity][slotId] = null;
    setCurrentSet(newSet);
    updateProgress(newSet);
  };

  const exportSet = async (format = 'json') => {
    try {
      const response = await axios.post('/api/export-set', {
        set_data: currentSet,
        theme: theme,
        format: format
      });
      
      // Determine file extension and MIME type
      const extensions = { json: 'json', csv: 'csv', cockatrice: 'xml' };
      const mimeTypes = { 
        json: 'application/json', 
        csv: 'text/csv', 
        cockatrice: 'application/xml' 
      };
      
      const extension = extensions[format] || 'json';
      const mimeType = mimeTypes[format] || 'application/json';
      
      // Create download link
      const blob = new Blob([response.data], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${theme.replace(/\s+/g, '_')}_set.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Failed to export set:', error);
      alert('Failed to export set: ' + (error.response?.data?.error || error.message));
    }
  };

  const renderSlot = (slot, colorName, rarity) => {
    const card = currentSet[colorName]?.[rarity]?.[slot.id];
    
    // Debug logging for card rendering
    if (card) {
      console.log(`🎨 Rendering card ${card.name} in slot ${slot.id} (${colorName} ${rarity})`);
    }
    
    return (
      <div key={slot.id} className="slot-card">
        <div className="slot-header">
          <span className="slot-id">{slot.id}</span>
          <span className="slot-description">{slot.description}</span>
        </div>
        
        {card ? (
          <div className={`generated-card ${card.isNew ? 'card-appearing' : ''}`}>
            <div className="card-name">{card.name}</div>
            <div className="card-cost">{card.mana_cost}</div>
            <div className="card-type">{card.type}</div>
            {card.power !== undefined && (
              <div className="card-stats">{card.power}/{card.toughness}</div>
            )}
            <div className="card-text">{card.rules_text}</div>
            <div className="card-flavor">"{card.flavor_text}"</div>
            <button 
              className="clear-button"
              onClick={() => clearCard(slot.id, colorName, rarity)}
            >
              Clear
            </button>
            {card.isNew && (
              <div className="new-card-indicator">✨ Just Generated!</div>
            )}
          </div>
        ) : (
          <div className="empty-slot">
            <button 
              className="generate-button"
              onClick={() => generateCard(slot.id, colorName, rarity, slot)}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Card'}
            </button>
          </div>
        )}
      </div>
    );
  };

  const getColorClass = (colorName) => {
    const colorClasses = {
      white: 'color-white',
      blue: 'color-blue', 
      black: 'color-black',
      red: 'color-red',
      green: 'color-green',
      multicolor: 'color-multicolor',
      colorless: 'color-colorless',
      lands: 'color-lands'
    };
    return colorClasses[colorName] || '';
  };

  const renderColorSection = (colorName, colorData) => {
    return (
      <div key={colorName} className={`color-section ${getColorClass(colorName)}`}>
        <h3 className="color-title">{colorName.charAt(0).toUpperCase() + colorName.slice(1)}</h3>
        
        {Object.keys(colorData).map(rarity => {
          const rarityData = colorData[rarity];
          
          return (
            <div key={rarity} className="rarity-section">
              <h4 className="rarity-title">{rarity.charAt(0).toUpperCase() + rarity.slice(1)}</h4>
              
              <div className="slots-grid">
                {Array.isArray(rarityData) ? (
                  rarityData.map(slot => renderSlot(slot, colorName, rarity))
                ) : (
                  Object.keys(rarityData).map(cardType => {
                    if (Array.isArray(rarityData[cardType])) {
                      return (
                        <div key={cardType} className="card-type-section">
                          <h5 className="card-type-title">{cardType.replace('_', ' ').toUpperCase()}</h5>
                          {rarityData[cardType].map(slot => renderSlot(slot, colorName, rarity))}
                        </div>
                      );
                    }
                    return null;
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  if (!skeleton) {
    return <div className="loading">Loading skeleton...</div>;
  }

  return (
    <div className={`set-builder ${darkMode ? 'dark-mode' : ''}`}>
      {showConceptBuilder && (
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
                  disabled={conceptLoading}
                />
              </div>
              
              <button 
                className="generate-concept-button"
                onClick={generateConcept}
                disabled={conceptLoading || !pitch.trim()}
              >
                {conceptLoading ? 'Generating Concept...' : 'Generate Set Concept'}
              </button>
              
              <div className="concept-actions">
                <button 
                  className="skip-concept-button"
                  onClick={() => setShowConceptBuilder(false)}
                >
                  Skip Concept Builder
                </button>
              </div>
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
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="builder-header">
        <div className="header-top">
          <h2>MTG Set Builder</h2>
          <div className="header-controls">
            <div className={`websocket-status ${isConnected ? 'connected' : 'disconnected'}`} 
                 title={isConnected ? 'Real-time updates connected' : (connectionError || 'Real-time updates disconnected')}>
              {isConnected ? '🟢' : '🔴'} {isConnected ? 'Live' : 'Offline'}
              {websocketStats.received > 0 && (
                <span className="websocket-stats" style={{ marginLeft: '8px', fontSize: '12px' }}>
                  📡 {websocketStats.received} received
                </span>
              )}
              {connectionError && reconnectAttempts < maxReconnectAttempts && (
                <button 
                  className="reconnect-button"
                  onClick={reconnect}
                  title="Reconnect to real-time updates"
                >
                  🔄
                </button>
              )}
            </div>
            <button 
              className="dark-mode-toggle"
              onClick={() => setDarkMode(!darkMode)}
              title="Toggle dark mode"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
        
        <div className="set-type-selector">
          <label>
            <input
              type="radio"
              value="full"
              checked={setType === 'full'}
              onChange={(e) => setSetType(e.target.value)}
            />
            Full Set ({cardCounts.full} cards)
          </label>
          <label>
            <input
              type="radio"
              value="commons"
              checked={setType === 'commons'}
              onChange={(e) => setSetType(e.target.value)}
            />
            Commons Only ({cardCounts.commons} cards)
          </label>
        </div>
        
        {(concept || setConcept) && !showConceptBuilder && (
          <div className="concept-summary">
            <h3>Set Concept: {(concept || setConcept).name}</h3>
            <p className="concept-description">{(concept || setConcept).description}</p>
            <div className="concept-mechanics">
              <strong>Key Mechanics:</strong> {(concept || setConcept).mechanics?.join(', ')}
            </div>
            <div className="concept-archetypes">
              <strong>Archetypes:</strong> {(concept || setConcept).archetypes?.map(a => `${a.colors} ${a.name}`).join(', ')}
            </div>
          </div>
        )}

        {!showConceptBuilder && (
          <>
            <div className="connection-status">
              <span className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                {isConnected ? '🟢 WebSocket Connected - Real-time updates enabled' : '🔴 WebSocket Disconnected - No real-time updates'}
              </span>
              {connectionError && (
                <span className="connection-error">Error: {connectionError}</span>
              )}
            </div>
            
            <div className="theme-input">
              <input
                type="text"
                placeholder="Enter your set theme..."
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                className="theme-field"
              />
            </div>
          </>
        )}
        
        <div className="progress-bar">
          <div className="progress-text">
            {loading ? (
              (() => {
                console.log(`🎬 UI: Displaying "Generating..." state - ${progress.completed}/${progress.total} cards`);
                return 'Generating...';
              })()
            ) : (
              (() => {
                const percentage = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0;
                console.log(`📊 UI: Displaying progress - ${progress.completed}/${progress.total} cards (${percentage}%)`);
                return `Progress: ${progress.completed}/${progress.total} cards (${percentage}%)`;
              })()
            )}
          </div>
          <div 
            className={`progress-fill ${loading ? 'generating' : ''}`} 
            style={{ width: `${loading ? 100 : (progress.total > 0 ? (progress.completed / progress.total) * 100 : 0)}%` }}
          ></div>
        </div>

        {loading && useBatched50 && batchProgress.total > 0 && (
          <div className="batch-progress-bar">
            <div className="batch-progress-text">
              Batch {batchProgress.current}/{batchProgress.total} 
              {batchProgress.batchTime > 0 && ` (${batchProgress.batchTime.toFixed(1)}s per batch)`}
              {batchProgress.cardsCompleted && batchProgress.totalCards && 
                ` • ${batchProgress.cardsCompleted}/${batchProgress.totalCards} cards`
              }
            </div>
            <div 
              className="batch-progress-fill" 
              style={{ width: `${(batchProgress.current / batchProgress.total) * 100}%` }}
            ></div>
          </div>
        )}
        
        <div className="builder-actions">
          {!showConceptBuilder && (
            <button 
              className="show-concept-button"
              onClick={() => setShowConceptBuilder(true)}
            >
              Create New Concept
            </button>
          )}
          
          <button 
            className="generate-all-button"
            onClick={(useStreaming && !useUltraFast) ? generateAllCardsStreaming : generateAllCards}
            disabled={loading || !theme.trim()}
          >
            {loading 
              ? (() => {
                  const buttonText = setType === 'commons' ? 'Generating Commons...' : 'Generating Cards...';
                  console.log(`🔴 UI: Generate button showing "${buttonText}" (disabled)`);
                  return buttonText;
                })()
              : (() => {
                  const buttonText = setType === 'commons' ? 'Generate All Commons' : 'Generate All Cards';
                  console.log(`🟢 UI: Generate button showing "${buttonText}" (enabled)`);
                  return buttonText;
                })()
            }
          </button>
          

          
          <div className="export-dropdown">
            <button 
              className="export-button"
              onClick={() => exportSet('json')}
              disabled={progress.completed === 0}
            >
              Export JSON
            </button>
            <button 
              className="export-button"
              onClick={() => exportSet('csv')}
              disabled={progress.completed === 0}
            >
              Export CSV
            </button>
            <button 
              className="export-button"
              onClick={() => exportSet('cockatrice')}
              disabled={progress.completed === 0}
            >
              Export Cockatrice
            </button>
          </div>
        </div>
      </div>

      <div className="color-filter">
        <button 
          className={selectedColor === 'all' ? 'active' : ''}
          onClick={() => setSelectedColor('all')}
        >
          All Colors
        </button>
        {(setType === 'commons' 
          ? ['white', 'blue', 'black', 'red', 'green', 'colorless']
          : ['white', 'blue', 'black', 'red', 'green', 'multicolor', 'colorless', 'lands']
        ).map(color => (
          <button
            key={color}
            className={selectedColor === color ? 'active' : ''}
            onClick={() => setSelectedColor(color)}
          >
            {color.charAt(0).toUpperCase() + color.slice(1)}
          </button>
        ))}
      </div>

      <div className="skeleton-display">
        {selectedColor === 'all' ? (
          Object.keys(skeleton).map(colorName => renderColorSection(colorName, skeleton[colorName]))
        ) : (
          skeleton[selectedColor] && renderColorSection(selectedColor, skeleton[selectedColor])
        )}
      </div>
    </div>
  );
};

export default SetBuilder;