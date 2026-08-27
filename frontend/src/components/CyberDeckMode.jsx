import { useState, useEffect } from 'react';

export function useCyberDeck() {
  const [isCyberMode, setIsCyberMode] = useState(
    () => localStorage.getItem('cyber_deck_mode') === 'true'
  );

  useEffect(() => {
    if (isCyberMode) {
      document.body.classList.add('cyber-deck-mode');
      localStorage.setItem('cyber_deck_mode', 'true');
    } else {
      document.body.classList.remove('cyber-deck-mode');
      localStorage.setItem('cyber_deck_mode', 'false');
    }
  }, [isCyberMode]);

  const toggleCyberMode = () => setIsCyberMode(!isCyberMode);

  return { isCyberMode, toggleCyberMode };
}

export function CyberToggleBtn({ isCyberMode, toggleCyberMode }) {
  return (
    <button
      className="cyber-pill-btn"
      onClick={toggleCyberMode}
      title="Toggle Secret Cyber Deck Mode"
      id="btn-toggle-cyber-deck"
    >
      <span>{isCyberMode ? '⚡ CYBER DECK ACTIVE' : '⚡ CYBER DECK'}</span>
    </button>
  );
}
