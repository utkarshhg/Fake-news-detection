

import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const initials = user?.username
    ? user.username.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
    : '??';

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sb-brand">
          <div className="sb-brand-mark">FN</div>
          <div>
            <div className="sb-brand-title">Fake News Detector</div>
            <div className="sb-brand-sub">Credibility intelligence</div>
          </div>
        </div>

        <div className="sb-user">
          <div className="sb-avatar">{initials}</div>
          <div>
            <div className="sb-user-name">{user?.username}</div>
            <div className="sb-user-role">{user?.role}</div>
          </div>
        </div>

        <div className="sb-label">Navigation</div>
        <nav className="sb-nav">
          <NavLink to="/analyzer" className={({ isActive }) => `sb-nav-item ${isActive ? 'active' : ''}`}>
            Article Analyzer
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => `sb-nav-item ${isActive ? 'active' : ''}`}>
            Dashboard
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => `sb-nav-item ${isActive ? 'active' : ''}`}>
            History
          </NavLink>
          {user?.role === 'admin' && (
            <NavLink to="/admin" className={({ isActive }) => `sb-nav-item ${isActive ? 'active' : ''}`}>
              Admin Panel
            </NavLink>
          )}
        </nav>

        <div className="sb-divider" />

        <button className="btn btn-block btn-sm" onClick={handleLogout}>
          Logout
        </button>

        <div className="sb-footer">
          <span className="sb-footer-dot" />
          Fake News Detector v1.0.0
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
