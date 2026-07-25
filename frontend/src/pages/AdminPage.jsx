

import { useState, useEffect } from 'react';
import {
  getAdminUsers, updateUserRole, toggleUserActive,
  getAdminMetrics, getAdminFlagged, reviewFlag,
} from '../api/client';
import PageHeader from '../components/PageHeader';
import SectionLabel from '../components/SectionLabel';
import MetricCard from '../components/MetricCard';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('users');

  return (
    <>
      <PageHeader title="Admin Panel" subtitle="Manage users, monitor system health and review flagged articles." eyebrow="Administration" />

      <div className="tabs">
        {['users', 'models', 'flagged'].map(t => (
          <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {{ users: 'Users', models: 'Model Metrics', flagged: 'Flagged Articles' }[t]}
          </button>
        ))}
      </div>

      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'models' && <ModelsTab />}
      {activeTab === 'flagged' && <FlaggedTab />}
    </>
  );
}

function UsersTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    setLoading(true);
    try { setUsers(await getAdminUsers()); } catch {  }
    setLoading(false);
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleRoleChange = async (userId, role) => {
    try { await updateUserRole(userId, role); fetchUsers(); } catch {  }
  };

  const handleToggle = async (userId) => {
    try { await toggleUserActive(userId); fetchUsers(); } catch {  }
  };

  if (loading) return <div className="spinner" />;

  return (
    <>
      <SectionLabel>User management</SectionLabel>

      <div className="grid grid-3 mb-md">
        <MetricCard label="Total Users" value={users.length} />
        <MetricCard label="Active" value={users.filter(u => u.is_active).length} />
        <MetricCard label="Admins" value={users.filter(u => u.role === 'admin').length} />
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td><strong>{u.username}</strong></td>
                <td>{u.email}</td>
                <td>
                  <select
                    className="form-select"
                    value={u.role}
                    onChange={e => handleRoleChange(u.id, e.target.value)}
                    style={{ width: 'auto', padding: '4px 8px', fontSize: '0.82rem' }}
                  >
                    <option value="reporter">Reporter</option>
                    <option value="researcher">Researcher</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td>
                  <span className="tag" style={{
                    background: u.is_active ? 'var(--success-soft)' : 'var(--danger-soft)',
                    color: u.is_active ? 'var(--success)' : 'var(--danger)',
                  }}>
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="text-sm text-muted">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                <td>
                  <button className="btn btn-sm" onClick={() => handleToggle(u.id)}>
                    {u.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function ModelsTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminMetrics().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;
  if (!data?.metrics) return <div className="alert alert-info">No model metrics found. Run model training first.</div>;

  const metrics = data.metrics;

  return (
    <>
      <SectionLabel>Model performance comparison</SectionLabel>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Accuracy</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1 Score</th>
              <th>ROC AUC</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(metrics).map(([name, m]) => (
              <tr key={name}>
                <td><strong>{name}</strong></td>
                <td>{(m.accuracy * 100).toFixed(1)}%</td>
                <td>{(m.precision * 100).toFixed(1)}%</td>
                <td>{(m.recall * 100).toFixed(1)}%</td>
                <td>{(m.f1_score * 100).toFixed(1)}%</td>
                <td>{(m.roc_auc * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function FlaggedTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  const fetchFlagged = async () => {
    setLoading(true);
    try { setItems(await getAdminFlagged(filter)); } catch {  }
    setLoading(false);
  };

  useEffect(() => { fetchFlagged(); }, [filter]);

  const handleReview = async (flagId, status) => {
    try { await reviewFlag(flagId, status, ''); fetchFlagged(); } catch {  }
  };

  if (loading) return <div className="spinner" />;

  return (
    <>
      <SectionLabel>Flagged articles review queue</SectionLabel>

      <div className="mb-md" style={{ maxWidth: 200 }}>
        <select className="form-select" value={filter} onChange={e => setFilter(e.target.value)}>
          <option>All</option>
          <option value="pending">Pending</option>
          <option value="reviewed">Reviewed</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>

      {items.length === 0 ? (
        <div className="alert alert-success">No flagged articles.</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Flag ID</th>
              <th>Analysis</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map(f => (
              <tr key={f.id}>
                <td>#{f.id}</td>
                <td>#{f.analysis_id}</td>
                <td className="text-sm">{f.reason || '—'}</td>
                <td>
                  <span className="tag" style={{
                    background: f.status === 'pending' ? 'var(--warning-soft)' : 'var(--success-soft)',
                    color: f.status === 'pending' ? 'var(--warning)' : 'var(--success)',
                  }}>{f.status}</span>
                </td>
                <td className="text-sm text-muted">{f.created_at ? new Date(f.created_at).toLocaleDateString() : '—'}</td>
                <td>
                  {f.status === 'pending' && (
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-sm" onClick={() => handleReview(f.id, 'reviewed')}>Approve</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleReview(f.id, 'dismissed')}>Dismiss</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
