import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCyberDeck, CyberToggleBtn } from './CyberDeckMode';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { isCyberMode, toggleCyberMode } = useCyberDeck();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { to: '/dashboard', icon: '⬡', label: 'Dashboard' },
    { to: '/projects/new', icon: '+', label: 'New Project' },
  ];

  return (
    <>
      {/* Navbar */}
      <nav className="navbar">
        <Link to="/dashboard" className="navbar-brand" title="AI Risk Manager - Security Intelligence">
          <div className="navbar-brand-icon">🛡️</div>
          <span>AI Risk Manager</span>
        </Link>

        <div className="navbar-actions">
          {/* Secret Cyber Deck Mode Toggle */}
          <CyberToggleBtn isCyberMode={isCyberMode} toggleCyberMode={toggleCyberMode} />

          <div className="navbar-user">
            <span>👤</span>
            <span>{user?.email || 'User'}</span>
          </div>

          <button
            id="btn-logout"
            className="btn btn-ghost btn-sm"
            onClick={handleLogout}
            title="Logout of account"
          >
            ⎋ Logout
          </button>
        </div>
      </nav>

      <div className="page-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <span className="sidebar-section">Navigation</span>
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`sidebar-link ${location.pathname === link.to ? 'active' : ''}`}
            >
              <span style={{ fontSize: '1.1rem' }}>{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          ))}

          {/* System status badge */}
          <div style={{ marginTop: 'auto', padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-cyan)', letterSpacing: '0.05em' }}>
              GEMINI AI ENGINE
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              v1.5 Flash • Active
            </div>
          </div>

          <span className="sidebar-section">Account</span>
          <button
            className="sidebar-link"
            onClick={handleLogout}
            style={{ background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'left' }}
          >
            <span>⎋</span>
            <span>Logout</span>
          </button>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </>
  );
}
