import React from 'react';
import { 
  BarChart3, 
  PieChart as PieIcon, 
  ShieldAlert, 
  Target, 
  Flame,
  Activity,
  Layers
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from 'recharts';

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
};

const ATTACK_GROUPINGS = {
  "DoS/DDoS": ["DoS Hulk", "DDoS", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest"],
  "Brute Force": ["FTP-Patator", "SSH-Patator", "Web Attack - Brute Force"],
  "Web Application": ["Web Attack - XSS", "Web Attack - SQL Injection"],
  "Reconnaissance": ["PortScan"],
  "Malware & C2": ["Bot"],
  "Advanced Threats": ["Infiltration", "Heartbleed"]
};

export default function AttackAnalytics({ stats }) {
  const attackDist = stats?.attack_distribution || {};
  const totalAttacks = stats?.attacks_detected || 0;
  const normalTraffic = stats?.normal_traffic || 0;
  const totalFlows = stats?.total_traffic_analyzed || 0;

  // Attack categories for bar chart
  const attackBarData = Object.entries(attackDist).map(([name, count]) => ({
    name,
    count,
    percentage: totalAttacks > 0 ? ((count / totalAttacks) * 100).toFixed(1) : 0
  })).sort((a, b) => b.count - a.count);

  // Normal vs Attack Pie
  const binaryData = [
    { name: 'Benign Traffic', value: normalTraffic, color: '#10b981' },
    { name: 'Malicious Traffic', value: totalAttacks, color: '#ef4444' }
  ];

  // Grouped Categories
  const categoryGroupData = Object.entries(ATTACK_GROUPINGS).map(([groupName, attacks]) => {
    const groupCount = attacks.reduce((sum, att) => sum + (attackDist[att] || 0), 0);
    return {
      category: groupName,
      count: groupCount,
      fullMark: totalAttacks > 0 ? totalAttacks : 100
    };
  });

  return (
    <div className="page-wrapper">
      {/* Top Banner */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '20px 24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Attack Intelligence & Threat Analytics</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Deep-dive telemetry analysis across all 14 malicious attack signatures detected by the AI-NIDS classification engine.
        </p>
      </div>

      {/* Grid: Attack Breakdown & Normal vs Attack */}
      <div className="grid-2">
        {/* Normal vs Attack Distribution */}
        <div className="cyber-card">
          <div className="cyber-card-header">
            <div className="card-title">
              <PieIcon size={18} color="var(--cyan-primary)" />
              <span>Traffic Composition (Benign vs Malicious)</span>
            </div>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={binaryData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value">
                  {binaryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }} />
                <Legend formatter={(v) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '8px' }}>
            Total Analyzed: <strong>{totalFlows.toLocaleString()}</strong> flows
          </div>
        </div>

        {/* Grouped Category Radar */}
        <div className="cyber-card">
          <div className="cyber-card-header">
            <div className="card-title">
              <Target size={18} color="var(--orange-high)" />
              <span>Threat Vector Radar Profile</span>
            </div>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={categoryGroupData}>
                <PolarGrid stroke="var(--border-color)" />
                <PolarAngleAxis dataKey="category" stroke="var(--text-muted)" fontSize={11} />
                <PolarRadiusAxis stroke="var(--border-color)" />
                <Radar name="Attacks" dataKey="count" stroke="var(--cyan-primary)" fill="var(--cyan-primary)" fillOpacity={0.4} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Full Attack Class Frequency Table & Bar Chart */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div className="cyber-card-header">
          <div className="card-title">
            <BarChart3 size={18} color="var(--cyan-primary)" />
            <span>Attack Signatures Frequency Distribution</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            DATABASE AUDIT
          </span>
        </div>

        <div style={{ height: 280, marginBottom: '20px' }}>
          {attackBarData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={attackBarData} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
                <XAxis dataKey="name" stroke="var(--text-dim)" fontSize={10} angle={-30} textAnchor="end" interval={0} />
                <YAxis stroke="var(--text-dim)" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }} />
                <Bar dataKey="count" fill="var(--red-critical)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
              No attacks detected in system yet.
            </div>
          )}
        </div>

        {/* Detailed Attack Classes Table */}
        <div className="cyber-table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Attack Class</th>
                <th>Category</th>
                <th>Incident Count</th>
                <th>Share of Total Attacks</th>
                <th>Typical Severity Tier</th>
              </tr>
            </thead>
            <tbody>
              {attackBarData.map((item, idx) => {
                let cat = 'Other';
                for (const [group, list] of Object.entries(ATTACK_GROUPINGS)) {
                  if (list.includes(item.name)) {
                    cat = group;
                    break;
                  }
                }
                return (
                  <tr key={idx}>
                    <td><strong>{item.name}</strong></td>
                    <td style={{ color: 'var(--text-muted)' }}>{cat}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{item.count.toLocaleString()}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{item.percentage}%</td>
                    <td>
                      <span className={`badge badge-${item.name.includes('Heartbleed') || item.name.includes('Infiltration') || item.name.includes('SQL') || item.name.includes('Bot') ? 'CRITICAL' : item.name.includes('DDoS') || item.name.includes('Hulk') ? 'HIGH' : 'MEDIUM'}`}>
                        {item.name.includes('Heartbleed') || item.name.includes('Infiltration') || item.name.includes('SQL') || item.name.includes('Bot') ? 'CRITICAL' : item.name.includes('DDoS') || item.name.includes('Hulk') ? 'HIGH' : 'MEDIUM'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
