import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { projectsAPI } from '../api/client';
import Layout from '../components/Layout';
import ThreatRadarWidget from '../components/ThreatRadarWidget';
import { getScoreClass, formatDate, Spinner } from '../components/ui';

function ProjectCard({ project, onDelete }) {
  const score = project.overall_risk_score;
  const scoreClass = getScoreClass(score);

  return (
    <div className="project-card">
      <div className="project-card-header">
        <div>
          <h3 className="project-card-title">{project.name}</h3>
        </div>
        <button
          className="btn btn-danger btn-icon"
          title="Delete project"
          id={`btn-delete-project-${project.id}`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete(project.id, project.name);
          }}
          style={{ flexShrink: 0, zIndex: 10 }}
        >
          🗑
        </button>
      </div>

      {project.description && (
        <p className="project-card-desc">{project.description}</p>
      )}

      <div className="project-card-meta">
        <div className="project-risk-score">
          <span className={`risk-score-number ${scoreClass}`}>
            {score !== null && score !== undefined ? score.toFixed(1) : '—'}
          </span>
          <div>
            <div className="risk-score-label">Risk Score</div>
            <div className="risk-score-label">/10</div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-accent)', fontWeight: 600 }}>
            {project.risk_count ?? 0} Risks Identified
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            {formatDate(project.created_at)}
          </div>
        </div>
      </div>

      {/* Clickable Card Overlay */}
      <Link
        to={`/projects/${project.id}`}
        style={{ position: 'absolute', inset: 0, borderRadius: 'inherit', zIndex: 1 }}
        aria-label={`Open project ${project.name}`}
        id={`link-project-${project.id}`}
      />
    </div>
  );
}

export default function DashboardPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const res = await projectsAPI.list();
      setProjects(res.data);
    } catch {
      setError('Failed to load projects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProjects(); }, []);

  const handleDelete = async (id, name) => {
    if (deleteConfirm?.id === id) {
      try {
        await projectsAPI.delete(id);
        setProjects((p) => p.filter((proj) => proj.id !== id));
        setDeleteConfirm(null);
      } catch {
        setError('Failed to delete project.');
        setDeleteConfirm(null);
      }
    } else {
      setDeleteConfirm({ id, name });
      setTimeout(() => setDeleteConfirm(null), 4000);
    }
  };

  const totalProjects = projects.length;
  const analyzedProjects = projects.filter((p) => p.overall_risk_score !== null).length;
  const totalRisks = projects.reduce((sum, p) => sum + (p.risk_count ?? 0), 0);
  const avgScore = analyzedProjects > 0
    ? (projects.reduce((sum, p) => sum + (p.overall_risk_score ?? 0), 0) / analyzedProjects).toFixed(1)
    : '—';

  return (
    <Layout>
      {/* Delete confirmation banner */}
      {deleteConfirm && (
        <div
          className="error-banner mb-lg"
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
        >
          <span>⚠ Click delete again to confirm removing "<strong>{deleteConfirm.name}</strong>"</span>
          <button className="btn btn-sm btn-ghost" onClick={() => setDeleteConfirm(null)}>Cancel</button>
        </div>
      )}

      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h1>Dashboard</h1>
          <p>Overview of all your software projects and AI risk posture assessments</p>
        </div>
        <Link to="/projects/new" id="btn-new-project" className="btn btn-primary btn-lg">
          + Create New Project
        </Link>
      </div>

      {/* Threat Radar Visualizer Widget */}
      <ThreatRadarWidget
        totalProjects={totalProjects}
        totalRisks={totalRisks}
        avgScore={avgScore}
      />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{totalProjects}</div>
          <div className="stat-label">Total Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analyzedProjects}</div>
          <div className="stat-label">AI Audited</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totalRisks}</div>
          <div className="stat-label">Risks Detected</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{avgScore}</div>
          <div className="stat-label">Average Risk Score</div>
        </div>
      </div>

      {/* Project Grid */}
      <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Your Projects</h2>
      </div>

      {loading ? (
        <div className="loading-state">
          <Spinner size="lg" />
          <p>Loading projects from secure store...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="card empty-state">
          <div className="empty-state-icon">🛡️</div>
          <h3>No Projects Yet</h3>
          <p>Create your first project to perform automated AI risk analysis and mitigation planning.</p>
          <Link to="/projects/new" className="btn btn-primary btn-lg mt-md">
            + Create Your First Project
          </Link>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </Layout>
  );
}
