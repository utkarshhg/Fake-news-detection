

import { useState, useEffect } from 'react';
import createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';
import { getDashboardStats } from '../api/client';
import PageHeader from '../components/PageHeader';
import SectionLabel from '../components/SectionLabel';
import MetricCard from '../components/MetricCard';

const Plot = createPlotlyComponent(Plotly);

const CHART_LAYOUT = {
  height: 300,
  margin: { l: 20, r: 20, t: 20, b: 40 },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#374151', family: 'Inter' },
};

const RISK_COLORS = { Critical: '#b42318', High: '#c4320a', Medium: '#b54708', Low: '#067647' };
const LABEL_COLORS = { FAKE: '#b42318', REAL: '#067647' };

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats().then(setStats).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-between"><div className="spinner" /></div>;

  if (!stats || stats.total_analyses === 0) {
    return (
      <>
        <PageHeader title="Analytics Dashboard" subtitle="Aggregate insights across every article analyzed." eyebrow="Overview" />
        <div className="alert alert-info">No analyses yet. Head to the Article Analyzer to get started.</div>
      </>
    );
  }

  const risk = stats.risk_distribution || {};
  const labels = stats.label_distribution || {};
  const types = stats.content_type_distribution || {};
  const langs = stats.language_distribution || {};
  const scores = stats.score_distribution || [];

  return (
    <>
      <PageHeader title="Analytics Dashboard" subtitle="Aggregate insights across every article analyzed." eyebrow="Overview" />

      {}
      <div className="grid grid-4">
        <MetricCard label="Total Analyzed" value={stats.total_analyses} />
        <MetricCard label="Avg Credibility" value={`${stats.avg_credibility?.toFixed(0) || 0}/100`} />
        <MetricCard label="Fake Detected" value={labels.FAKE || 0} />
        <MetricCard label="High Risk" value={(risk.Critical || 0) + (risk.High || 0)} />
      </div>

      {}
      <div className="grid grid-2 mt-lg">
        <div>
          <SectionLabel>Risk level distribution</SectionLabel>
          <div className="surface-card">
            {Object.keys(risk).length > 0 ? (
              <Plot
                data={[{
                  type: 'pie', labels: Object.keys(risk), values: Object.values(risk),
                  hole: 0.45, textinfo: 'label+percent', textfont: { size: 13 },
                  marker: { colors: Object.keys(risk).map(k => RISK_COLORS[k] || '#6b7280') },
                }]}
                layout={{ ...CHART_LAYOUT, showlegend: false }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%' }}
              />
            ) : <p className="text-muted text-sm">No data available.</p>}
          </div>
        </div>
        <div>
          <SectionLabel>Fake vs real distribution</SectionLabel>
          <div className="surface-card">
            {Object.keys(labels).length > 0 ? (
              <Plot
                data={[{
                  type: 'bar', x: Object.keys(labels), y: Object.values(labels),
                  marker: { color: Object.keys(labels).map(k => LABEL_COLORS[k] || '#6b7280') },
                  text: Object.values(labels), textposition: 'auto',
                }]}
                layout={{ ...CHART_LAYOUT, xaxis: { showgrid: false }, yaxis: { showgrid: true, gridcolor: '#f3f4f6' } }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%' }}
              />
            ) : <p className="text-muted text-sm">No data available.</p>}
          </div>
        </div>
      </div>

      {}
      <div className="grid grid-2 mt-lg">
        <div>
          <SectionLabel>Content type breakdown</SectionLabel>
          <div className="surface-card">
            {Object.keys(types).length > 0 ? (
              <Plot
                data={[{
                  type: 'bar', x: Object.values(types), y: Object.keys(types), orientation: 'h',
                  marker: { color: '#3538cd' }, text: Object.values(types), textposition: 'auto',
                }]}
                layout={{ ...CHART_LAYOUT, xaxis: { showgrid: true, gridcolor: '#f3f4f6' }, yaxis: { showgrid: false } }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%' }}
              />
            ) : <p className="text-muted text-sm">No data available.</p>}
          </div>
        </div>
        <div>
          <SectionLabel>Language distribution</SectionLabel>
          <div className="surface-card">
            {Object.keys(langs).length > 0 ? (
              <Plot
                data={[{
                  type: 'pie', labels: Object.keys(langs), values: Object.values(langs),
                  hole: 0.45, textinfo: 'label+percent', textfont: { size: 13 },
                }]}
                layout={{ ...CHART_LAYOUT, showlegend: false }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%' }}
              />
            ) : <p className="text-muted text-sm">No data available.</p>}
          </div>
        </div>
      </div>

      {}
      {scores.length > 0 && (
        <div className="mt-lg">
          <SectionLabel>Credibility score distribution</SectionLabel>
          <div className="surface-card">
            <Plot
              data={[{
                type: 'histogram', x: scores, nbinsx: 20,
                marker: { color: '#3538cd', opacity: 0.8 },
              }]}
              layout={{
                ...CHART_LAYOUT, height: 250,
                xaxis: { title: 'Credibility Score', showgrid: false },
                yaxis: { title: 'Count', showgrid: true, gridcolor: '#f3f4f6' },
                shapes: [{
                  type: 'line', x0: scores.reduce((a, b) => a + b, 0) / scores.length,
                  x1: scores.reduce((a, b) => a + b, 0) / scores.length,
                  y0: 0, y1: 1, yref: 'paper', line: { color: '#c4320a', width: 2, dash: 'dash' },
                }],
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}
    </>
  );
}
