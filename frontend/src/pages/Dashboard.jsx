import React from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Activity, 
  Layers, 
  ArrowUpRight,
  TrendingUp,
  Radio,
  FileSpreadsheet
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend 
} from 'recharts';

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
};

export default function Dashboard({ stats, alerts, onAlertStatusChange, onNavigate }) {
  const totalFlows = stats?.total_traffic_analyzed || 0;
  const normalTraffic = stats?.normal_traffic || 0;
  const attacksDetected = stats?.attacks_detected || 0;
  const attackRate = stats?.attack_rate || 0;
  const activeAlerts = stats?.active_alerts_count || 0;
  
  // Format attack distribution for chart
  const attackDistData = Object.entries(stats?.attack_distribution || {}).map(([name, count]) => ({
    name,
    count
  })).sort((a, b) => b.count - a.count).slice(0, 7);

  // Format severity distribution for pie chart
  const severityData = Object.entries(stats?.severity_distribution || {}).map(([name, value]) => ({
    name,
    value
  })).filter(d => d.value > 0);

  const recentAlerts = alerts?.slice(0, 6) || [];

  return (
    <div className="page-wrapper">
      {/* Quick Action Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(0, 240, 255, 0.08) 0%, rgba(13, 21, 39, 0.6) 100%)',
        border: '1px solid rgba(0, 240, 255, 0.25)',
        borderRadius: 'var(--radius-md)',
        padding: '18px 24px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
            AI-Powered Network Intrusion Detection Active
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Multi-class anomaly & threat classification trained on CICIDS2017 flow telemetry.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-primary" onClick={() => onNavigate('traffic-analysis')}>
            <FileSpreadsheet size={16} />
            <span>Upload Traffic CSV</span>
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('live-monitoring')}>
            <Radio size={16} />
            <span>Launch Simulation</span>
          </button>
        </div>
      </div>

      {/* KPI Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Total Flows Analyzed</div>
          <div className="stat-value">{totalFlows.toLocaleString()}</div>
          <div className="stat-subtext">Real-time database records</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Normal / Benign Flows</div>
          <div className="stat-value" style={{ color: 'var(--emerald-normal)' }}>
            {normalTraffic.toLocaleString()}
          </div>
          <div className="stat-subtext">
            {totalFlows > 0 ? `${((normalTraffic / totalFlows) * 100).toFixed(1)}% benign baseline` : '0%'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Malicious Intrusions</div>
          <div className="stat-value" style={{ color: 'var(--red-critical)' }}>
            {attacksDetected.toLocaleString()}
          </div>
          <div className="stat-subtext" style={{ color: attackRate > 0 ? 'var(--orange-high)' : 'var(--text-dim)' }}>
            {attackRate}% detection rate
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Active SOC Alerts</div>
          <div className="stat-value" style={{ color: activeAlerts > 0 ? 'var(--amber-medium)' : 'var(--emerald-normal)' }}>
            {activeAlerts}
          </div>
          <div className="stat-subtext">
            {stats?.alerts_by_status?.OPEN || 0} Open • {stats?.alerts_by_status?.INVESTIGATING || 0} In Progress
          </div>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid-2">
        {/* Top Attack Classes Bar Chart */}
        <div className="cyber-card">
          <div className="cyber-card-header">
            <div className="card-title">
              <TrendingUp size={18} color="var(--cyan-primary)" />
              <span>Top Detected Attack Vectors</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              LIVE METRICS
            </span>
          </div>

          <div style={{ height: 260 }}>
            {attackDistData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={attackDistData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
                  <XAxis 
                    dataKey="name" 
                    stroke="var(--text-dim)" 
                    fontSize={11} 
                    angle={-25} 
                    textAnchor="end" 
                    interval={0} 
                  />
                  <YAxis stroke="var(--text-dim)" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--bg-card)', 
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-main)',
                      borderRadius: 'var(--radius-sm)',
                      fontFamily: 'var(--font-mono)'
                    }} 
                  />
                  <Bar dataKey="count" fill="var(--cyan-primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
                No attacks detected yet. Upload network traffic or launch simulation.
              </div>
            )}
          </div>
        </div>

        {/* Threat Severity Distribution Donut */}
        <div className="cyber-card">
          <div className="cyber-card-header">
            <div className="card-title">
              <Layers size={18} color="var(--amber-medium)" />
              <span>Threat Severity Profile</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              ALL FLOWS
            </span>
          </div>

          <div style={{ height: 260 }}>
            {severityData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {severityData.map((entry) => (
                      <Cell key={`cell-${entry.name}`} fill={SEVERITY_COLORS[entry.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--bg-card)', 
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-main)',
                      borderRadius: 'var(--radius-sm)',
                      fontFamily: 'var(--font-mono)'
                    }} 
                  />
                  <Legend 
                    formatter={(value) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
                No severity data available.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Security Incidents Feed */}
      <div className="cyber-card">
        <div className="cyber-card-header">
          <div className="card-title">
            <AlertTriangle size={18} color="var(--red-critical)" />
            <span>Recent Intrusion Alerts Queue</span>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('alerts')}>
            <span>View All Alerts</span>
            <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="cyber-table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Timestamp</th>
                <th>Attack Vector</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Incident Action</th>
              </tr>
            </thead>
            <tbody>
              {recentAlerts.length > 0 ? (
                recentAlerts.map((alert) => (
                  <tr key={alert.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      #{alert.id.toString().padStart(4, '0')}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </td>
                    <td>
                      <strong>{alert.attack_type}</strong>
                    </td>
                    <td>
                      <span className={`badge badge-${alert.severity}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {(alert.confidence * 100).toFixed(1)}%
                    </td>
                    <td>
                      <span className={`badge badge-${alert.status}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td>
                      {alert.status === 'OPEN' && (
                        <button 
                          className="btn btn-secondary btn-sm"
                          onClick={() => onAlertStatusChange(alert.id, 'INVESTIGATING')}
                        >
                          Investigate
                        </button>
                      )}
                      {alert.status === 'INVESTIGATING' && (
                        <button 
                          className="btn btn-primary btn-sm"
                          onClick={() => onAlertStatusChange(alert.id, 'RESOLVED')}
                        >
                          Resolve
                        </button>
                      )}
                      {alert.status === 'RESOLVED' && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--emerald-normal)' }}>
                          ✓ Resolved
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-dim)' }}>
                    No security alerts generated yet. All network traffic is currently clean.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
