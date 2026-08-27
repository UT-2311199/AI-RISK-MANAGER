import { useState } from 'react';

export default function RiskSimulatorModal({ initialScore = 8.0, onClose }) {
  const [controls, setControls] = useState({
    mfa: false,
    encryption: false,
    waf: false,
    backups: false,
    soc2: false,
    zeroTrust: false,
  });

  const controlImpacts = [
    { key: 'mfa', label: 'Multi-Factor Authentication (MFA)', reduction: 1.5, icon: '🔑' },
    { key: 'encryption', label: 'End-to-End Field Level Encryption', reduction: 2.0, icon: '🔒' },
    { key: 'waf', label: 'Cloud Web Application Firewall (WAF)', reduction: 1.2, icon: '🛡️' },
    { key: 'backups', label: 'Automated Immutable Data Backups', reduction: 1.0, icon: '💾' },
    { key: 'soc2', label: 'SOC-2 Compliance Audit Framework', reduction: 0.8, icon: '📜' },
    { key: 'zeroTrust', label: 'Zero-Trust Architecture Controls', reduction: 1.5, icon: '⚡' },
  ];

  const totalReduction = Object.keys(controls).reduce((sum, key) => {
    if (controls[key]) {
      const match = controlImpacts.find((c) => c.key === key);
      return sum + (match ? match.reduction : 0);
    }
    return sum;
  }, 0);

  const simulatedScore = Math.max(1.0, (initialScore - totalReduction)).toFixed(1);

  const getSimulatedGrade = (score) => {
    if (score < 3.0) return { grade: 'A+ (SECURE)', color: '#10b981' };
    if (score < 5.0) return { grade: 'B (MODERATE)', color: '#3b82f6' };
    if (score < 7.0) return { grade: 'C (ELEVATED)', color: '#f59e0b' };
    return { grade: 'F (CRITICAL)', color: '#ef4444' };
  };

  const gradeInfo = getSimulatedGrade(Number(simulatedScore));

  const toggleControl = (key) => {
    setControls((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-cyan)', letterSpacing: '0.08em' }}>
              SECRET AI FEATURE
            </span>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-primary)', margin: 0 }}>
              ⚡ Interactive Risk Simulator Sandbox
            </h2>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Simulate how implementing target security controls reduces overall risk posture in real-time.
        </p>

        {/* Score Comparison Display */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Current Risk Score</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{initialScore.toFixed(1)}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 10</div>
          </div>

          <div style={{ padding: '16px', background: 'rgba(6, 182, 212, 0.08)', borderRadius: '12px', border: '1px solid var(--accent-cyan)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Simulated Risk Score</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: gradeInfo.color }}>{simulatedScore}</div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: gradeInfo.color }}>{gradeInfo.grade}</div>
          </div>
        </div>

        {/* Controls Toggles */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
          {controlImpacts.map((c) => {
            const active = controls[c.key];
            return (
              <div
                key={c.key}
                onClick={() => toggleControl(c.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: active ? 'rgba(99,102,241,0.15)' : 'var(--bg-input)',
                  border: `1px solid ${active ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '1.2rem' }}>{c.icon}</span>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: active ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                    {c.label}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#10b981' }}>
                    -{c.reduction} Score
                  </span>
                  <input type="checkbox" checked={active} onChange={() => {}} style={{ cursor: 'pointer' }} />
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={onClose}>Done Simulation</button>
        </div>

      </div>
    </div>
  );
}
