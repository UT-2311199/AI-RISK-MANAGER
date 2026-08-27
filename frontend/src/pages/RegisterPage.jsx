import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '../components/ui';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { register, login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    const regResult = await register(email, password, fullName);
    if (!regResult.success) {
      setError(regResult.error);
      return;
    }

    // Auto-login after registration
    const loginResult = await login(email, password);
    if (loginResult.success) {
      navigate('/dashboard');
    } else {
      setSuccess('Account created! Please sign in.');
      navigate('/login');
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">🛡</div>
          <span>AI Risk Manager</span>
        </div>

        <h2 style={{ marginBottom: '4px' }}>Create your account</h2>
        <p style={{ marginBottom: '24px', fontSize: '0.9rem' }}>Start managing project risks with AI</p>

        {error && <div className="error-banner" style={{ marginBottom: '16px' }}>⚠ {error}</div>}
        {success && <div className="success-banner" style={{ marginBottom: '16px' }}>✓ {success}</div>}

        <form className="auth-form" onSubmit={handleSubmit} id="form-register">
          <div className="form-group">
            <label className="form-label" htmlFor="reg-name">Full name</label>
            <input
              id="reg-name"
              type="text"
              className="form-input"
              placeholder="John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email address</label>
            <input
              id="reg-email"
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              className="form-input"
              placeholder="Min 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <span className="form-hint">At least 8 characters</span>
          </div>

          <button
            id="btn-register-submit"
            type="submit"
            className="btn btn-primary btn-lg w-full"
            disabled={loading}
          >
            {loading ? <Spinner /> : '→ Create Account'}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account?{' '}
          <Link to="/login">Sign in →</Link>
        </div>
      </div>
    </div>
  );
}
