
import createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const Plot = createPlotlyComponent(Plotly);

export default function CredibilityGauge({ score, riskColor }) {
  const data = [
    {
      type: 'indicator',
      mode: 'gauge+number',
      value: score,
      number: { suffix: '/100', font: { size: 38, color: '#101828', family: 'Sora, Inter' } },
      gauge: {
        axis: { range: [0, 100], tickwidth: 1, tickcolor: '#cfd6e4' },
        bar: { color: riskColor, thickness: 0.32 },
        bgcolor: '#f7f8fb',
        borderwidth: 0,
        steps: [
          { range: [0, 25], color: '#fef3f2' },
          { range: [25, 50], color: '#fff6ed' },
          { range: [50, 75], color: '#fefbe8' },
          { range: [75, 100], color: '#edfcf2' },
        ],
        threshold: {
          line: { color: '#101828', width: 2 },
          thickness: 0.82,
          value: score,
        },
      },
    },
  ];

  const layout = {
    height: 250,
    margin: { l: 30, r: 30, t: 30, b: 10 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#101828', family: 'Inter' },
  };

  return (
    <Plot
      data={data}
      layout={layout}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%' }}
    />
  );
}
