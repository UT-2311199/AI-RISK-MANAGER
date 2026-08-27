export function getSeverityClass(severity) {
  switch (severity?.toLowerCase()) {
    case 'critical': return 'critical';
    case 'high':     return 'high';
    case 'medium':   return 'medium';
    case 'low':      return 'low';
    default:         return 'low';
  }
}

export function getScoreColor(score) {
  if (score === null || score === undefined) return 'var(--text-muted)';
  if (score >= 8.5) return 'var(--severity-critical)';
  if (score >= 6.7) return 'var(--severity-high)';
  if (score >= 3.4) return 'var(--severity-medium)';
  return 'var(--severity-low)';
}

export function getScoreClass(score) {
  if (score === null || score === undefined) return 'score-none';
  if (score >= 8.5) return 'score-critical';
  if (score >= 6.7) return 'score-high';
  if (score >= 3.4) return 'score-medium';
  return 'score-low';
}

export function formatDate(dateString) {
  if (!dateString) return '—';
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });
}

export function getStatusClass(status) {
  return 'status-' + (status || 'Open').replace(/\s+/g, '-');
}

// ── SeverityBadge Component ─────────────────────────────────────────────────
export function SeverityBadge({ severity }) {
  const cls = getSeverityClass(severity);
  return (
    <span className={`badge badge-${cls}`}>
      {severity === 'Critical' && '🔴'}
      {severity === 'High'     && '🟠'}
      {severity === 'Medium'   && '🟡'}
      {severity === 'Low'      && '🟢'}
      {' '}{severity}
    </span>
  );
}

// ── CategoryBadge Component ─────────────────────────────────────────────────
export function CategoryBadge({ category }) {
  return <span className="badge badge-category">🏷 {category}</span>;
}

// ── StatusBadge Component ───────────────────────────────────────────────────
export function StatusBadge({ status }) {
  return (
    <span className={`status-badge ${getStatusClass(status)}`}>
      {status || 'Open'}
    </span>
  );
}

// ── RiskScoreGauge Component ────────────────────────────────────────────────
export function RiskScoreGauge({ score, size = 120 }) {
  const safeScore = score ?? 0;
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (safeScore / 10) * circumference;
  const color = getScoreColor(safeScore);

  return (
    <div className="risk-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={8}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeDasharray={`${progress} ${circumference - progress}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease', filter: `drop-shadow(0 0 6px ${color}50)` }}
        />
      </svg>
      <div className="risk-gauge-text">
        <span className="risk-gauge-score" style={{ color }}>
          {score !== null && score !== undefined ? score.toFixed(1) : '—'}
        </span>
        <span className="risk-gauge-max">/10</span>
      </div>
    </div>
  );
}

// ── Spinner Component ────────────────────────────────────────────────────────
export function Spinner({ size = 'default' }) {
  return <div className={`spinner ${size === 'lg' ? 'spinner-lg' : ''}`} />;
}

// ── TagsInput Component ─────────────────────────────────────────────────────
export function TagsInput({ tags, onChange, placeholder = 'Add technology...' }) {
  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && e.target.value.trim()) {
      e.preventDefault();
      const newTag = e.target.value.trim().replace(/,$/, '');
      if (newTag && !tags.includes(newTag)) {
        onChange([...tags, newTag]);
      }
      e.target.value = '';
    } else if (e.key === 'Backspace' && !e.target.value && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const removeTag = (index) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div className="tags-input-container" onClick={(e) => e.currentTarget.querySelector('input').focus()}>
      {tags.map((tag, i) => (
        <span key={i} className="tag-chip">
          {tag}
          <button type="button" className="tag-remove" onClick={() => removeTag(i)}>×</button>
        </span>
      ))}
      <input
        type="text"
        className="tags-input"
        placeholder={tags.length === 0 ? placeholder : ''}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
}
