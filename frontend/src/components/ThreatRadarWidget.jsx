import { useState, useEffect } from 'react';

export default function ThreatRadarWidget({ totalProjects = 0, totalRisks = 0, avgScore = 0 }) {
  const [scanIndex, setScanIndex] = useState(0);

  const scanSignals = [
    'ENCRYPTED CHANNEL SECURE',
    'GEMINI-1.5 AI ENGINE ONLINE',
    'CONTINUOUS THREAT MONITORING',
    'ZERO-DAY AUDIT STANDBY',
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setScanIndex((prev) => (prev + 1) % scanSignals.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="radar-widget">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
        
        {/* Left Side: Animated Radar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div className="radar-sweep-circle">
            <div className="radar-sweep-line" />
            <span style={{ fontSize: '1.4rem' }}>🛡️</span>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-cyan)', letterSpacing: '0.08em' }}>
                LIVE AI SECURITY MATRIX
              </span>
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              Cyber Threat Defense Center
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
              STATUS: {scanSignals[scanIndex]}
            </p>
          </div>
        </div>

        {/* Right Side: Quick Stats */}
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          <div style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>System Guard</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>ACTIVE</div>
          </div>

          <div style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Scanned Risks</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{totalRisks}</div>
          </div>

          <div style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Average Score</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-primary)' }}>{avgScore}/10</div>
          </div>
        </div>

      </div>
    </div>
  );
}
