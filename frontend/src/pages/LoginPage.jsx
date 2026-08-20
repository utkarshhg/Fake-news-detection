

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { register as apiRegister } from '../api/client';

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState('login');

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <div className="login-badge">Verified Journalism Toolkit</div>
          <h1 className="login-title">Fake News Detector</h1>
          <p className="login-subtitle">
            An AI-assisted workspace for scoring article credibility, tracing sources
            and flagging misinformation before it spreads.
          </p>
        </div>

        <div className="tabs" style={{ marginBottom: 0 }}>
          <button className={`tab ${activeTab === 'login' ? 'active' : ''}`} onClick={() => setActiveTab('login')}>
            Sign in
          </button>
          <button className={`tab ${activeTab === 'register' ? 'active' : ''}`} onClick={() => setActiveTab('register')}>
            Create account
          </button>
        </div>

        {activeTab === 'login' ? <LoginForm /> : <RegisterForm onSuccess={() => setActiveTab('login')} />}

        <p className="login-footer">
          Your analyses stay private to your account unless shared by an administrator.
        </p>
      </div>
    </div>
  );
}

function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!username || !password) { setError('Please fill in all fields.'); return; }
    setLoading(true);
    try {
      await login(username, password);
      navigate('/analyzer');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <div className="login-form-title">Welcome back</div>
      <div className="login-form-sub">Sign in to continue your verification work.</div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="form-group">
        <label className="form-label">Username</label>
        <input className="form-input" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter your username" />
      </div>
      <div className="form-group">
        <label className="form-label">Password</label>
        <input className="form-input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" />
      </div>

      <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
}

function RegisterForm({ onSuccess }) {
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '', role: 'reporter' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (key, val) => setForm(prev => ({ ...prev, [key]: val }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    if (form.password !== form.password2) { setError('Passwords do not match.'); return; }
    setLoading(true);
    try {
      await apiRegister(form.username, form.email, form.password, form.role);
      setSuccess('Account created. Please sign in.');
      setTimeout(() => onSuccess?.(), 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <div className="login-form-title">Create your account</div>
      <div className="login-form-sub">Choose a role to tailor the tools you see.</div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="form-group">
        <label className="form-label">Username</label>
        <input className="form-input" value={form.username} onChange={e => update('username', e.target.value)} placeholder="Min 3 characters" />
      </div>
      <div className="form-group">
        <label className="form-label">Email</label>
        <input className="form-input" type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="your@email.com" />
      </div>
      <div className="form-group">
        <label className="form-label">Password</label>
        <input className="form-input" type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min 6 characters" />
      </div>
      <div className="form-group">
        <label className="form-label">Confirm Password</label>
        <input className="form-input" type="password" value={form.password2} onChange={e => update('password2', e.target.value)} placeholder="Repeat password" />
      </div>
      <div className="form-group">
        <label className="form-label">Role</label>
        <select className="form-select" value={form.role} onChange={e => update('role', e.target.value)}>
          <option value="reporter">Reporter</option>
          <option value="researcher">Researcher</option>
        </select>
      </div>

      <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Account'}
      </button>
    </form>
  );
}
