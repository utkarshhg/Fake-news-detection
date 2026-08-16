

import { useState, useEffect, useCallback } from 'react';
import { getHistory, getHistoryDetail } from '../api/client';
import PageHeader from '../components/PageHeader';
import SectionLabel from '../components/SectionLabel';

export default function HistoryPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState('All');
  const [langFilter, setLangFilter] = useState('All');
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getHistory(50, riskFilter, langFilter);
      setRecords(data);
    } catch {  }
    setLoading(false);
  }, [riskFilter, langFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleViewDetail = async (id) => {
    setDetailLoading(true);
    try {
      const data = await getHistoryDetail(id);
      setDetail(data);
    } catch {  }
    setDetailLoading(false);
  };

  return (
    <>
      <PageHeader title="Analysis History" subtitle="Browse, filter and export every past article analysis." eyebrow="Records" />

      {}
      <SectionLabel>Filters</SectionLabel>
      <div className="grid grid-3 mb-md">
        <div>
          <label className="form-label">Risk Level</label>
          <select className="form-select" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
            <option>All</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>
        </div>
        <div>
          <label className="form-label">Language</label>
          <select className="form-select" value={langFilter} onChange={e => setLangFilter(e.target.value)}>
            <option>All</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="hi">Hindi</option>
          </select>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn btn-block" onClick={fetchData}>Refresh</button>
        </div>
      </div>

      {}
      <SectionLabel>Showing {records.length} results</SectionLabel>

      {loading ? (
        <div className="flex items-center justify-between"><div className="spinner" /></div>
      ) : records.length === 0 ? (
        <div className="alert alert-info">No results found.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Prediction</th>
                <th>Confidence</th>
                <th>Credibility</th>
                <th>Risk</th>
                <th>Type</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {records.map(r => {
                const labelColor = r.prediction === 'FAKE' ? 'var(--danger)' : r.prediction === 'REAL' ? 'var(--success)' : 'var(--ink-muted)';
                return (
                  <tr key={r.id}>
                    <td>#{r.id}</td>
                    <td>{r.date ? new Date(r.date).toLocaleDateString() : '—'}</td>
                    <td><span style={{ fontWeight: 600, color: labelColor }}>{r.prediction}</span></td>
                    <td>{r.confidence ? `${(r.confidence * 100).toFixed(0)}%` : '—'}</td>
                    <td>{r.credibility ?? '—'}</td>
                    <td>{r.risk || '—'}</td>
                    <td>{r.content_type || '—'}</td>
                    <td>
                      <button className="btn btn-sm" onClick={() => handleViewDetail(r.id)}>View</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {}
      {records.length > 0 && (
        <div className="mt-md">
          <button className="btn btn-sm" onClick={() => {
            const csv = ['ID,Date,Prediction,Confidence,Credibility,Risk,Type']
              .concat(records.map(r => `${r.id},${r.date},${r.prediction},${r.confidence},${r.credibility},${r.risk},${r.content_type}`))
              .join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'analysis_history.csv';
            link.click();
          }}>
            Export CSV
          </button>
        </div>
      )}

      {}
      {detail && (
        <div className="mt-lg">
          <hr style={{ border: 'none', borderTop: '1px solid var(--line)', margin: '16px 0' }} />
          <SectionLabel>Analysis detail — #{detail.id}</SectionLabel>
          {detailLoading ? <div className="spinner" /> : (
            <div className="surface-card">
              <div className="grid grid-3 mb-md">
                <div><span className="text-muted text-sm">Prediction</span><br /><strong>{detail.prediction}</strong></div>
                <div><span className="text-muted text-sm">Credibility</span><br /><strong>{detail.credibility}/100</strong></div>
                <div><span className="text-muted text-sm">Risk</span><br /><strong>{detail.risk}</strong></div>
              </div>
              {detail.article_url && <p className="text-sm text-muted">URL: <a href={detail.article_url} target="_blank" rel="noreferrer">{detail.article_url}</a></p>}
              <details style={{ marginTop: 12 }}>
                <summary className="text-sm" style={{ cursor: 'pointer' }}>Full Article Text</summary>
                <p className="text-sm text-soft" style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{detail.article_text}</p>
              </details>
              <button className="btn btn-sm mt-md" onClick={() => setDetail(null)}>Close</button>
            </div>
          )}
        </div>
      )}
    </>
  );
}
