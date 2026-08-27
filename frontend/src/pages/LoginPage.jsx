import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '../components/ui';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">🛡</div>
          <span>AI Risk Manager</span>
        </div>

        <h2 style={{ marginBottom: '4px' }}>Welcome back</h2>
        <p style={{ marginBottom: '24px', fontSize: '0.9rem' }}>Sign in to your account to continue</p>

        {error && <div className="error-banner" style={{ marginBottom: '16px' }}>⚠ {error}</div>}

        <form className="auth-form" onSubmit={handleSubmit} id="form-login">
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">Email address</label>
            <input
              id="login-email"
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            id="btn-login-submit"
            type="submit"
            className="btn btn-primary btn-lg w-full"
            disabled={loading}
          >
            {loading ? <Spinner /> : '→ Sign In'}
          </button>
        </form>

        <div className="auth-switch">
          Don't have an account?{' '}
          <Link to="/register">Create one →</Link>
        </div>
      </div>
    </div>
  );
}
