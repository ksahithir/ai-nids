import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  Award, 
  CheckCircle2, 
  BarChart2, 
  Image as ImageIcon,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer 
} from 'recharts';
import api from '../services/api';

export default function ModelPerformance() {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeVisualTab, setActiveVisualTab] = useState('cm'); // 'cm' or 'fi'

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        setLoading(true);
        const data = await api.getModelInfo();
        setModelInfo(data);
      } catch (err) {
        console.error('Failed to load model metadata:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, []);

  if (loading) {
    return (
      <div className="page-wrapper" style={{ textAlign: 'center', padding: '60px' }}>
        <Activity size={32} className="spin" color="var(--cyan-primary)" style={{ margin: '0 auto 16px auto' }} />
        <p style={{ color: 'var(--text-muted)' }}>Loading verified model evaluation telemetry...</p>
      </div>
    );
  }

  const metrics = modelInfo?.metrics || {};
  const perClass = modelInfo?.per_class_metrics || {};
  const topFeatures = modelInfo?.top_features || [];

  return (
    <div className="page-wrapper">
      {/* Top Banner */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '20px 24px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Model Performance & Validation Audit</h2>
            <span className="badge badge-LOW">
              <Sparkles size={12} />
              <span>ACTIVE IN PRODUCTION</span>
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Evaluated on completely unseen CICIDS2017 test partition (14,345 flows) with strict zero-leakage guarantees.
          </p>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
          Trained: <strong>{modelInfo?.trained_date || '2026-08-15'}</strong>
        </div>
      </div>

      {/* Model KPI Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Model Architecture</div>
          <div className="stat-value" style={{ fontSize: '1.3rem', color: 'var(--cyan-primary)' }}>
            {modelInfo?.model_name || 'HistGradientBoosting'}
          </div>
          <div className="stat-subtext">{modelInfo?.total_classes || 15} Output Classes • 69 Features</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Unseen Test Accuracy</div>
          <div className="stat-value" style={{ color: 'var(--emerald-normal)' }}>
            {((metrics.accuracy || 0) * 100).toFixed(2)}%
          </div>
          <div className="stat-subtext">Overall correct classifications</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Macro Average F1</div>
          <div className="stat-value" style={{ color: 'var(--cyan-primary)' }}>
            {((metrics.macro_f1 || 0) * 100).toFixed(2)}%
          </div>
          <div className="stat-subtext">Balanced across rare & major classes</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Weighted Average F1</div>
          <div className="stat-value" style={{ color: 'var(--emerald-normal)' }}>
            {((metrics.weighted_f1 || 0) * 100).toFixed(2)}%
          </div>
          <div className="stat-subtext">Volume-weighted performance</div>
        </div>
      </div>

      {/* Candidate Models Comparison Table */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div className="cyber-card-header">
          <div className="card-title">
            <Award size={18} color="var(--amber-medium)" />
            <span>Classical ML Candidate Model Comparison</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            8 GB RAM OPTIMIZED
          </span>
        </div>

        <div className="cyber-table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Model Candidate</th>
                <th>Test Accuracy</th>
                <th>Macro Precision</th>
                <th>Macro Recall</th>
                <th>Macro F1-Score</th>
                <th>Weighted F1</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>HistGradientBoosting</strong></td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.75%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>90.41%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>94.02%</td>
                <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--cyan-primary)', fontWeight: 700 }}>91.32%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.79%</td>
                <td><span className="badge badge-LOW">★ Selected Best</span></td>
              </tr>
              <tr>
                <td><strong>Decision Tree</strong></td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.71%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>90.17%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>90.10%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>90.13%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.73%</td>
                <td><span className="badge" style={{ background: 'var(--bg-surface)', color: 'var(--text-dim)' }}>Candidate</span></td>
              </tr>
              <tr>
                <td><strong>Random Forest</strong></td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.46%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>88.16%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>88.12%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>88.14%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>98.50%</td>
                <td><span className="badge" style={{ background: 'var(--bg-surface)', color: 'var(--text-dim)' }}>Candidate</span></td>
              </tr>
              <tr>
                <td><strong>Logistic Regression</strong></td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>18.11%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>10.72%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>21.17%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>10.71%</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>18.69%</td>
                <td><span className="badge" style={{ background: 'var(--bg-surface)', color: 'var(--text-dim)' }}>Baseline</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-Class Metrics Table for All 15 Classes */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div className="cyber-card-header">
          <div className="card-title">
            <Layers size={18} color="var(--cyan-primary)" />
            <span>Per-Class Detailed Evaluation (15 Output Classes)</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Unseen Test Samples: 14,345
          </span>
        </div>

        <div className="cyber-table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Attack Class</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>Test Support</th>
                <th>Severity Tier</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(perClass).map(([clsName, metrics], idx) => (
                <tr key={idx}>
                  <td><strong>{clsName}</strong></td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{(metrics.precision * 100).toFixed(1)}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{(metrics.recall * 100).toFixed(1)}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: metrics.f1_score >= 0.9 ? 'var(--emerald-normal)' : metrics.f1_score >= 0.7 ? 'var(--cyan-primary)' : 'var(--amber-medium)' }}>
                    {(metrics.f1_score * 100).toFixed(1)}%
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{metrics.support.toLocaleString()}</td>
                  <td>
                    <span className={`badge badge-${metrics.severity}`}>
                      {metrics.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Artifacts Section */}
      <div className="cyber-card">
        <div className="cyber-card-header">
          <div className="card-title">
            <ImageIcon size={18} color="var(--cyan-primary)" />
            <span>Evaluation Figures & Explainability Artifacts</span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className={`btn btn-sm ${activeVisualTab === 'cm' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveVisualTab('cm')}
            >
              Confusion Matrix
            </button>
            <button 
              className={`btn btn-sm ${activeVisualTab === 'fi' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveVisualTab('fi')}
            >
              Feature Importance
            </button>
          </div>
        </div>

        <div style={{ textAlign: 'center', padding: '16px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)' }}>
          {activeVisualTab === 'cm' ? (
            <div>
              <img 
                src={api.getFigureUrl('confusion_matrix.png')} 
                alt="Confusion Matrix" 
                style={{ maxWidth: '100%', height: 'auto', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}
              />
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                Figure 1: Multi-class Confusion Matrix across all 15 network attack classes on the unseen test set.
              </div>
            </div>
          ) : (
            <div>
              <img 
                src={api.getFigureUrl('feature_importance.png')} 
                alt="Feature Importance" 
                style={{ maxWidth: '100%', height: 'auto', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}
              />
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                Figure 2: Top 20 predictive network flow features ranked by ensemble decision tree importance.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
