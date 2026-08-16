

import { useState } from 'react';
import { analyzeArticle } from '../api/client';
import PageHeader from '../components/PageHeader';
import SectionLabel from '../components/SectionLabel';
import CredibilityGauge from '../components/CredibilityGauge';
import RiskBadge from '../components/RiskBadge';
import EntityTags from '../components/EntityTags';
import SentimentBar from '../components/SentimentBar';
import SourceList from '../components/SourceList';
import FlagsList from '../components/FlagsList';
import BreakdownTable from '../components/BreakdownTable';

const MODELS = [
  { value: 'lightgbm', label: 'LightGBM (Best)' },
  { value: 'randomforest', label: 'Random Forest' },
  { value: 'bernoullinb', label: 'Bernoulli NB' },
  { value: 'multinomialnb', label: 'Multinomial NB' },
];

export default function AnalyzerPage() {
  const [inputMode, setInputMode] = useState('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [model, setModel] = useState('lightgbm');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const canAnalyze = inputMode === 'text' ? text.trim().length > 10 : url.trim().length > 5;

  const handleAnalyze = async () => {
    setError('');
    setResults(null);
    setLoading(true);
    setProgress(10);

    const ticker = setInterval(() => {
      setProgress(prev => Math.min(prev + 8, 90));
    }, 400);

    try {
      const data = await analyzeArticle(
        inputMode === 'text' ? text : '',
        inputMode === 'url' ? url : '',
        model,
      );
      setResults(data);
      setProgress(100);
    } catch (err) {
      setError(err.message);
    } finally {
      clearInterval(ticker);
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Article Analyzer"
        subtitle="Paste an article or enter a URL to run a full credibility analysis."
        eyebrow="Analysis"
      />

      {}
      <div className="tabs">
        <button className={`tab ${inputMode === 'text' ? 'active' : ''}`} onClick={() => setInputMode('text')}>
          Paste Text
        </button>
        <button className={`tab ${inputMode === 'url' ? 'active' : ''}`} onClick={() => setInputMode('url')}>
          Enter URL
        </button>
      </div>

      {inputMode === 'text' ? (
        <>
          <SectionLabel>Article text</SectionLabel>
          <textarea
            className="form-textarea"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Paste the full article text here..."
            style={{ minHeight: 220 }}
          />
        </>
      ) : (
        <>
          <SectionLabel>Article URL</SectionLabel>
          <input
            className="form-input"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/article"
          />
        </>
      )}

      {}
      <div className="flex items-center gap-md mt-md" style={{ gap: 16 }}>
        <div style={{ flex: 2 }}>
          <select className="form-select" value={model} onChange={e => setModel(e.target.value)}>
            {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <button className="btn btn-primary btn-block" onClick={handleAnalyze} disabled={!canAnalyze || loading}>
            {loading ? 'Analyzing...' : 'Analyze Article'}
          </button>
        </div>
      </div>

      {}
      {loading && (
        <div className="mt-md">
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {error && <div className="alert alert-danger mt-md">{error}</div>}

      {}
      {results && <AnalysisResults results={results} />}
    </>
  );
}

function AnalysisResults({ results }) {
  const [activeTab, setActiveTab] = useState('breakdown');
  const cred = results.credibility || {};
  const ml = results.ml_prediction || {};
  const sentiment = results.sentiment || {};
  const entities = results.entities || {};
  const keywords = results.keywords || [];
  const classification = results.classification || {};
  const verification = results.verification || {};
  const lang = results.language || {};

  const labelColor = ml.label === 'FAKE' ? '#b42318' : ml.label === 'REAL' ? '#067647' : '#b54708';

  return (
    <div className="mt-lg">
      <hr style={{ border: 'none', borderTop: '1px solid var(--line)', margin: '24px 0' }} />

      {}
      {lang.was_translated && (
        <div className="alert alert-info">
          Language detected: <strong>{lang.name}</strong> — Translated to English for analysis
        </div>
      )}

      {}
      <div className="grid grid-2-1-1">
        <div>
          <SectionLabel>Credibility score</SectionLabel>
          <CredibilityGauge score={cred.score || 50} riskColor={cred.risk_color || '#b54708'} />
        </div>
        <div>
          <SectionLabel>Risk level</SectionLabel>
          <RiskBadge level={cred.risk_level || 'Medium'} color={cred.risk_color || '#b54708'} />
          <div className="mt-md">
            <SectionLabel>Model prediction</SectionLabel>
            <div className="surface-card text-center" style={{ border: `1px solid ${labelColor}30`, background: `${labelColor}08` }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: labelColor }}>{ml.label}</div>
              <div className="text-muted text-sm">{((ml.confidence || 0) * 100).toFixed(1)}% confidence</div>
            </div>
          </div>
        </div>
        <div>
          <SectionLabel>Content type</SectionLabel>
          <div className="surface-card text-center" style={{ background: '#eff6ff', borderColor: '#bfdbfe' }}>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--brand)' }}>
              {classification.primary_type || 'Unknown'}
            </div>
          </div>
          <div className="mt-md">
            <SectionLabel>Sentiment</SectionLabel>
            <div className="surface-card text-center">
              <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{sentiment.sentiment_label || 'Neutral'}</div>
              <div className="text-muted text-sm">Polarity: {(sentiment.polarity || 0) >= 0 ? '+' : ''}{(sentiment.polarity || 0).toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>

      {}
      {cred.summary && (
        <div className="surface-card mt-md" style={{ borderLeft: '4px solid var(--brand)', fontWeight: 600, fontSize: '0.95rem', lineHeight: 1.55 }}>
          {cred.summary.replace(/^[⛔⚠️🔶✅\s]+/, '')}
        </div>
      )}

      {}
      <div className="tabs mt-lg">
        {['breakdown', 'sentiment', 'entities', 'verification', 'flags'].map(t => (
          <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {
              { breakdown: 'Score Breakdown', sentiment: 'Sentiment', entities: 'Entities', verification: 'Verification', flags: 'Flags' }[t]
            }
          </button>
        ))}
      </div>

      {activeTab === 'breakdown' && (
        <>
          <SectionLabel>Credibility score breakdown</SectionLabel>
          <BreakdownTable breakdown={cred.breakdown || {}} />
        </>
      )}

      {activeTab === 'sentiment' && (
        <>
          <SectionLabel>Sentiment analysis</SectionLabel>
          <SentimentBar polarity={sentiment.polarity || 0} subjectivity={sentiment.subjectivity || 0} />
          <p className="mt-sm text-soft"><strong>Subjectivity:</strong> {sentiment.subjectivity_label || 'Unknown'}</p>
          {sentiment.flags?.map((f, i) => <div className="flag-item" key={i}>{f}</div>)}
        </>
      )}

      {activeTab === 'entities' && (
        <div className="grid grid-2">
          <div>
            <SectionLabel>Named entities</SectionLabel>
            <EntityTags entities={entities.entities || []} />
          </div>
          <div>
            <SectionLabel>Top keywords</SectionLabel>
            {keywords.slice(0, 10).map((kw, i) => (
              <div key={i} className="text-sm mb-sm">
                <code style={{ background: 'var(--surface-3)', padding: '2px 6px', borderRadius: 4 }}>{kw.word}</code>
                <span className="text-muted"> — {kw.count} occurrences</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'verification' && (
        <>
          <SectionLabel>Real-time source verification</SectionLabel>
          {(() => {
            const status = verification.status || 'error';
            const display = {
              verified: { label: 'Verified', color: 'var(--success)' },
              partially_verified: { label: 'Partially Verified', color: 'var(--warning)' },
              no_matches: { label: 'Unverified', color: 'var(--danger)' },
              error: { label: 'Verification Unavailable', color: 'var(--ink-muted)' },
            };
            const { label, color } = display[status] || display.error;
            return <div style={{ fontSize: '1rem', fontWeight: 700, color, marginBottom: 12 }}>{label}</div>;
          })()}
          {verification.query_used && <p className="text-muted text-sm mb-sm">Search query: "{verification.query_used}"</p>}
          <SourceList sources={verification.matching_sources || []} />
        </>
      )}

      {activeTab === 'flags' && (
        <>
          <SectionLabel>Misinformation indicators</SectionLabel>
          <FlagsList flags={cred.flags || []} />
        </>
      )}

      {results.analysis_id && (
        <p className="text-muted text-sm mt-md">Analysis ID: #{results.analysis_id} — Saved to database</p>
      )}
    </div>
  );
}
