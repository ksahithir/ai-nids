import React from 'react';
import { 
  ShieldAlert, 
  Activity, 
  UploadCloud, 
  BarChart3, 
  BellRing, 
  Cpu, 
  Info,
  Terminal
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'SOC Dashboard', icon: ShieldAlert },
  { id: 'live-monitoring', label: 'Live Monitoring', icon: Activity },
  { id: 'traffic-analysis', label: 'Traffic Analysis (CSV)', icon: UploadCloud },
  { id: 'attack-analytics', label: 'Attack Analytics', icon: BarChart3 },
  { id: 'alerts', label: 'Alert Center', icon: BellRing },
  { id: 'model-performance', label: 'Model Performance', icon: Cpu },
  { id: 'system-info', label: 'System Information', icon: Info },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Terminal size={20} />
        </div>
        <div>
          <div className="brand-title">AI-NIDS</div>
          <div className="brand-subtitle">ENTERPRISE SOC EDITION</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div>Model: <strong>HistGradientBoosting</strong></div>
        <div style={{ marginTop: '4px', color: 'var(--cyan-primary)' }}>CICIDS2017 Preprocessed</div>
      </div>
    </aside>
  );
}
