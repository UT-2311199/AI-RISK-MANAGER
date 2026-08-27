import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { projectsAPI, risksAPI } from '../api/client';
import Layout from '../components/Layout';
import VoiceAssistant from '../components/VoiceAssistant';
import RiskSimulatorModal from '../components/RiskSimulatorModal';
import ExecutiveReportModal from '../components/ExecutiveReportModal';
import {
  SeverityBadge, CategoryBadge, StatusBadge,
  RiskScoreGauge, Spinner, getScoreColor, formatDate
} from '../components/ui';

const VALID_STATUSES = ['Open', 'Under Review', 'Mitigation in Progress', 'Resolved', 'Accepted'];

function RiskCard({ risk, onStatusUpdate, onDelete }) {
  const [updating, setUpdating] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const handleStatus = async (e) => {
    setUpdating(true);
    try {
      await onStatusUpdate(risk.id, e.target.value);
    } finally {
      setUpdating(false);
    }
  };

  const barColor = getScoreColor(risk.risk_score);
  const barWidth = `${(risk.risk_score / 10) * 100}%`;

  return (
    <div className="risk-card" id={`risk-card-${risk.id}`}>
      {/* Risk progress fill bar */}
      <div className="risk-score-bar">
        <div
          className="risk-score-bar-fill"
          style={{ width: barWidth, background: `linear-gradient(90deg, ${barColor}80, ${barColor})` }}
        />
      </div>

      <div className="risk-card-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, color: barColor }}>
              {risk.risk_score?.toFixed(1)}
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>/10</span>
          </div>
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '8px', lineHeight: '1.3', fontSize: '1.05rem' }}>
            {risk.title}
          </h4>
          <div className="risk-card-badges">
            <SeverityBadge severity={risk.severity} />
            <CategoryBadge category={risk.category} />
            <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
              Prob: {risk.probability}
            </span>
            <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
              Impact: {risk.impact}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {updating && <div className="spinner" style={{ width: '16px', height: '16px' }} />}
            <select
              className="form-select"
              style={{ width: 'auto', padding: '4px 10px', fontSize: '0.78rem' }}
              value={risk.status}
              onChange={handleStatus}
              disabled={updating}
              id={`status-${risk.id}`}
            >
              {VALID_STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <button
            className="btn btn-danger btn-icon btn-sm"
            onClick={() => onDelete(risk.id)}
            title="Delete risk"
            id={`btn-delete-risk-${risk.id}`}
          >
            🗑
          </button>
        </div>
      </div>

      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '14px', lineHeight: '1.6' }}>
        {risk.explanation}
      </p>

      {risk.mitigation && risk.mitigation.length > 0 && (
        <div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setExpanded(!expanded)}
            style={{ fontSize: '0.8rem', marginBottom: '8px', paddingLeft: 0 }}
          >
            {expanded ? '▲ Hide' : '▼ View'} Recommended Actions ({risk.mitigation.length})
          </button>
          {expanded && (
            <ul className="risk-mitigation-list">
              {risk.mitigation.map((action, i) => (
                <li key={i} className="risk-mitigation-item">{action}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [additionalContext, setAdditionalContext] = useState('');
  const [error, setError] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  
  // Secret Modals State
  const [showSimulator, setShowSimulator] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projRes, risksRes] = await Promise.all([
        projectsAPI.get(id),
        risksAPI.list(id),
      ]);
      setProject(projRes.data);
      setRisks(risksRes.data);
    } catch (err) {
      if (err.response?.status === 404) navigate('/dashboard');
      else setError('Failed to load project.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, [id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError('');
    try {
      const res = await projectsAPI.analyze(id, { additional_context: additionalContext });
      setRisks(res.data.risks);
      setProject((p) => ({ ...p, overall_risk_score: res.data.overall_risk_score }));
      setAdditionalContext('');
    } catch (err) {
      setError(err.response?.data?.detail || 'AI analysis failed. Please check Gemini API key.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleStatusUpdate = async (riskId, newStatus) => {
    await risksAPI.updateStatus(riskId, newStatus);
    setRisks((r) => r.map((risk) => risk.id === riskId ? { ...risk, status: newStatus } : risk));
  };

  const handleDeleteRisk = async (riskId) => {
    if (!confirm('Delete this risk item?')) return;
    try {
      await risksAPI.delete(riskId);
      setRisks((r) => r.filter((risk) => risk.id !== riskId));
    } catch {
      setError('Failed to delete risk.');
    }
  };

  const categories = ['All', ...new Set(risks.map((r) => r.category))];
  const statuses = ['All', ...VALID_STATUSES];
  const filtered = risks.filter((r) => {
    const catOk = filterCategory === 'All' || r.category === filterCategory;
    const statusOk = filterStatus === 'All' || r.status === filterStatus;
    return catOk && statusOk;
  });

  if (loading) {
    return (
      <Layout>
        <div className="loading-state">
          <div className="spinner spinner-lg" />
          <p>Analyzing project data...</p>
        </div>
      </Layout>
    );
  }

  if (!project) return null;

  const critical = risks.filter((r) => r.severity === 'Critical').length;
  const high = risks.filter((r) => r.severity === 'High').length;
  const open = risks.filter((r) => r.status === 'Open').length;
  const resolved = risks.filter((r) => r.status === 'Resolved').length;

  return (
    <Layout>
      {/* Secret Modals */}
      {showSimulator && (
        <RiskSimulatorModal
          initialScore={project.overall_risk_score ?? 7.5}
          onClose={() => setShowSimulator(false)}
        />
      )}

      {showReport && (
        <ExecutiveReportModal
          project={project}
          risks={risks}
          onClose={() => setShowReport(false)}
        />
      )}

      {/* Breadcrumb */}
      <div className="breadcrumb">
        <Link to="/dashboard">Dashboard</Link>
        <span className="breadcrumb-sep">›</span>
        <span>{project.name}</span>
      </div>

      {/* Project Header & Secret Actions */}
      <div className="page-header">
        <div className="page-header-left">
          <h1>{project.name}</h1>
          {project.description && <p>{project.description}</p>}
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Secret Action Buttons */}
          <VoiceAssistant project={project} risks={risks} />

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setShowSimulator(true)}
            title="Interactive What-If Mitigation Simulator"
            id="btn-open-simulator"
          >
            ⚡ Risk Simulator
          </button>

          {risks.length > 0 && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setShowReport(true)}
              title="Generate Executive Audit Document"
              id="btn-export-report"
            >
              📄 Audit Report
            </button>
          )}
        </div>
      </div>

      {/* Gauge + Details Summary */}
      <div className="risk-gauge-container" style={{ flexWrap: 'wrap' }}>
        <RiskScoreGauge score={project.overall_risk_score} size={120} />

        <div style={{ flex: 1, minWidth: '200px' }}>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
            Security & Risk Posture Score
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginTop: '12px' }}>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{critical}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Critical Threats</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-high)' }}>{high}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>High Severity</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{open}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Open Items</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-low)' }}>{resolved}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Resolved</div>
            </div>
          </div>
        </div>

        {project.technologies && project.technologies.length > 0 && (
          <div style={{ flex: 1, minWidth: '200px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Technologies</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {project.technologies.map((tech, i) => (
                <span key={i} className="tag-chip">{tech}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && <div className="error-banner mb-lg">⚠ {error}</div>}

      {/* AI Analysis trigger */}
      <div className="analyze-section">
        <h3>🤖 AI Risk Intelligence Analysis</h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          {risks.length > 0
            ? 'Re-run analysis to update identified risks. Gemini will re-evaluate project details and context.'
            : 'Analyze this project with Google Gemini to identify security, privacy, compliance, and technical risks.'}
        </p>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div className="form-group" style={{ flex: 1, minWidth: '240px', marginBottom: 0 }}>
            <label className="form-label" htmlFor="additional-context">Additional Analysis Focus (optional)</label>
            <input
              id="additional-context"
              type="text"
              className="form-input"
              placeholder="e.g. Focus on GDPR compliance, or SOC2 data privacy requirements"
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              disabled={analyzing}
            />
          </div>
          <button
            id="btn-analyze"
            className="btn btn-primary btn-lg"
            onClick={handleAnalyze}
            disabled={analyzing}
          >
            {analyzing ? <><Spinner /> AI Analysis In Progress...</> : '⚡ Run AI Risk Analysis'}
          </button>
        </div>
      </div>

      {analyzing && (
        <div className="analyzing-overlay mb-lg">
          <div className="analyzing-title">🤖 Google Gemini is scanning your architecture...</div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Evaluating potential security vulnerabilities, technical debt, and compliance risks across 8 categories...
          </p>
        </div>
      )}

      {/* Risks Listing */}
      {risks.length > 0 && !analyzing && (
        <div>
          <div className="section-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
            <div className="section-title">
              <span>⚠</span>
              <span>Identified Risks ({filtered.length})</span>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <select
                className="form-select"
                style={{ width: 'auto', fontSize: '0.8rem', padding: '6px 10px' }}
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                id="filter-category"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>{c === 'All' ? 'All Categories' : c}</option>
                ))}
              </select>
              <select
                className="form-select"
                style={{ width: 'auto', fontSize: '0.8rem', padding: '6px 10px' }}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                id="filter-status"
              >
                {statuses.map((s) => (
                  <option key={s} value={s}>{s === 'All' ? 'All Statuses' : s}</option>
                ))}
              </select>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="empty-state" style={{ padding: '40px' }}>
              <div className="empty-state-icon">🔍</div>
              <h3>No risks match selected filters</h3>
              <button className="btn btn-ghost" onClick={() => { setFilterCategory('All'); setFilterStatus('All'); }}>
                Clear filters
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {filtered.map((risk) => (
                <RiskCard
                  key={risk.id}
                  risk={risk}
                  onStatusUpdate={handleStatusUpdate}
                  onDelete={handleDeleteRisk}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {risks.length === 0 && !analyzing && (
        <div className="empty-state">
          <div className="empty-state-icon">🛡️</div>
          <h3>No risk audit performed yet</h3>
          <p>Click "Run AI Risk Analysis" above to trigger Gemini AI risk detection.</p>
        </div>
      )}
    </Layout>
  );
}
