import { useState } from 'react';

export default function VoiceAssistant({ project, risks = [] }) {
  const [speaking, setSpeaking] = useState(false);

  const speakSummary = () => {
    if (!('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported in this browser.');
      return;
    }

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    const total = risks.length;
    const score = project?.overall_risk_score ? project.overall_risk_score.toFixed(1) : 'unknown';
    const topRisk = risks.find((r) => r.severity === 'Critical' || r.severity === 'High');

    const text = `Security audit summary for ${project?.name || 'this project'}. ` +
      `The overall risk score is ${score} out of 10. ` +
      `We identified ${total} potential risks. ` +
      (topRisk ? `The highest priority risk is ${topRisk.title}, categorized under ${topRisk.category}.` : 'No critical risks detected.');

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <button
      className="btn btn-secondary btn-sm"
      onClick={speakSummary}
      title="Listen to AI Voice Briefing"
      id="btn-voice-briefing"
      style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
    >
      <span>{speaking ? '🔊 Speaking...' : '🎙️ AI Voice Briefing'}</span>
    </button>
  );
}
