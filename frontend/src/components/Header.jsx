import React, { useState, useEffect } from 'react';
import { ShieldCheck, Cpu, RefreshCw } from 'lucide-react';

export default function Header({ title, stats, onRefresh, loading }) {
  const [timeStr, setTimeStr] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const threatStatus = stats?.security_threat_status || 'NORMAL';
  const threatClass = `threat-${threatStatus.replace(/\s+/g, '-')}`;

  return (
    <header className="top-header">
      <div className="header-left">
        <h1 className="header-title">{title}</h1>
      </div>

      <div className="header-right">
        {/* Threat Posture Badge */}
        <div className={`threat-status-badge ${threatClass}`}>
          <span className="status-dot"></span>
          <span>POSTURE: {threatStatus}</span>
        </div>

        {/* Model Tag */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          background: 'var(--bg-surface)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-color)',
          fontSize: '0.78rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-muted)'
        }}>
          <Cpu size={14} color="var(--cyan-primary)" />
          <span>HistGradientBoosting (98.75%)</span>
        </div>

        {/* Live Clock */}
        <div style={{
          fontSize: '0.8rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-dim)'
        }}>
          {timeStr}
        </div>

        {/* Refresh Button */}
        <button 
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh Data"
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
        </button>
      </div>
    </header>
  );
}
