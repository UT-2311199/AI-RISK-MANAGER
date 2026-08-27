import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { projectsAPI } from '../api/client';
import Layout from '../components/Layout';
import { TagsInput, Spinner } from '../components/ui';

export default function NewProjectPage() {
  const [form, setForm] = useState({
    name: '',
    description: '',
    objective: '',
    context: '',
  });
  const [technologies, setTechnologies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.name.trim()) {
      setError('Project name is required.');
      return;
    }
    setLoading(true);
    try {
      const res = await projectsAPI.create({ ...form, technologies });
      navigate(`/projects/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="new-project-container">
        {/* Breadcrumbs */}
        <div className="breadcrumb">
          <Link to="/dashboard">Dashboard</Link>
          <span className="breadcrumb-sep">›</span>
          <span>New Project</span>
        </div>

        {/* Page Header */}
        <div className="page-header">
          <div className="page-header-left">
            <h1>Create New Project</h1>
            <p>Add your project details so AI can analyze its security and operational risks accurately.</p>
          </div>
        </div>

        {error && <div className="error-banner mb-lg">⚠ {error}</div>}

        <form onSubmit={handleSubmit} id="form-new-project">
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

            {/* Name */}
            <div className="form-group">
              <label className="form-label" htmlFor="proj-name">
                Project Name <span style={{ color: 'var(--severity-critical)' }}>*</span>
              </label>
              <input
                id="proj-name"
                type="text"
                name="name"
                className="form-input"
                placeholder="e.g. E-Commerce Payment Portal, Mobile Banking Application"
                value={form.name}
                onChange={handleChange}
                required
                autoFocus
              />
            </div>

            {/* Description */}
            <div className="form-group">
              <label className="form-label" htmlFor="proj-desc">Description</label>
              <textarea
                id="proj-desc"
                name="description"
                className="form-textarea"
                placeholder="What does this project do? What is the main functionality and scope?"
                value={form.description}
                onChange={handleChange}
                rows={3}
              />
            </div>

            {/* Objective */}
            <div className="form-group">
              <label className="form-label" htmlFor="proj-objective">Business Objective</label>
              <input
                id="proj-objective"
                type="text"
                name="objective"
                className="form-input"
                placeholder="e.g. Process 10,000 transactions daily with 99.99% uptime"
                value={form.objective}
                onChange={handleChange}
              />
            </div>

            {/* Technologies */}
            <div className="form-group">
              <label className="form-label">Technologies Used</label>
              <TagsInput
                tags={technologies}
                onChange={setTechnologies}
                placeholder="Type technology and press Enter (e.g. React, FastAPI, PostgreSQL, Stripe)"
              />
              <span className="form-hint">Press Enter or comma after each technology to add it</span>
            </div>

            {/* Context */}
            <div className="form-group">
              <label className="form-label" htmlFor="proj-context">Additional Context & Data Exposure</label>
              <textarea
                id="proj-context"
                name="context"
                className="form-textarea"
                placeholder="Team size, industry, user PII storage, payment data handling, compliance requirements (GDPR/HIPAA), known constraints..."
                value={form.context}
                onChange={handleChange}
                rows={4}
              />
              <span className="form-hint">
                More context = sharper, more targeted risk analysis from the AI model.
              </span>
            </div>

            {/* Submit Actions */}
            <div style={{ display: 'flex', gap: '16px', paddingTop: '12px' }}>
              <button
                id="btn-create-project"
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading}
              >
                {loading ? <><Spinner /> Creating Project...</> : '⚡ Create & Proceed to AI Audit'}
              </button>
              <Link to="/dashboard" className="btn btn-secondary btn-lg">Cancel</Link>
            </div>

          </div>
        </form>
      </div>
    </Layout>
  );
}
