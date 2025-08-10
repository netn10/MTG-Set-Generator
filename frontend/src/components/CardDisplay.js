import React from 'react';

const CardDisplay = ({ card }) => {
  const getColorClass = (manaCost) => {
    if (!manaCost) return 'colorless';
    if (manaCost.includes('W')) return 'white';
    if (manaCost.includes('U')) return 'blue';
    if (manaCost.includes('B')) return 'black';
    if (manaCost.includes('R')) return 'red';
    if (manaCost.includes('G')) return 'green';
    return 'colorless';
  };

  const formatManaCost = (manaCost) => {
    if (!manaCost) return '';
    return manaCost.replace(/([WUBRG])/g, '{$1}').replace(/(\d+)/g, '{$1}');
  };

  const isCreature = card.type && card.type.toLowerCase().includes('creature');

  return (
    <div className={`card ${getColorClass(card.mana_cost)}`}>
      <div className="card-header">
        <div className="card-name">{card.name}</div>
        <div className="mana-cost">{formatManaCost(card.mana_cost)}</div>
      </div>
      
      <div className="card-type">{card.type}</div>
      
      {card.rules_text && (
        <div className="rules-text">
          {card.rules_text}
        </div>
      )}
      
      {card.flavor_text && (
        <div className="flavor-text">
          <em>"{card.flavor_text}"</em>
        </div>
      )}
      
      {isCreature && card.power !== undefined && card.toughness !== undefined && (
        <div className="power-toughness">
          {card.power}/{card.toughness}
        </div>
      )}
      
      <div className="rarity">{card.rarity}</div>
      
      {card.error && (
        <div className="card-error">
          <small>Generated with fallback due to: {card.error}</small>
        </div>
      )}
    </div>
  );
};

export default CardDisplay;