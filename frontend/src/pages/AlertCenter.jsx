import React, { useState, useEffect } from 'react';
import { 
  BellRing, 
  Filter, 
  ShieldAlert, 
  CheckCircle, 
  Clock, 
  AlertOctagon,
  Search,
  RefreshCw,
  Eye
} from 'lucide-react';
import api from '../services/api';

export default function AlertCenter({ alerts, onAlertStatusChange, refreshAlerts }) {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusUpdate = async (alertId, newStatus) => {
    try {
      setIsUpdating(true);
      await api.updateAlertStatus(alertId, newStatus);
      if (selectedAlert && selectedAlert.id === alertId) {
        setSelectedAlert(prev => ({ ...prev, status: newStatus }));
      }
      if (onAlertStatusChange) {
        onAlertStatusChange(alertId, newStatus);
      }
    } catch (err) {
      console.error('Failed to update alert status:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const filteredAlerts = (alerts || []).filter(a => {
    const matchesStatus = statusFilter === 'ALL' || a.status === statusFilter;
    const matchesSeverity = severityFilter === 'ALL' || a.severity === severityFilter;
    const matchesSearch = searchQuery === '' || 
      a.attack_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSeverity && matchesSearch;
  });

  return (
    <div className="page-wrapper">
      {/* Header Banner */}
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
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>SOC Security Alert Center</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Incident triage queue for high-priority network intrusions requiring forensic investigation.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={refreshAlerts}>
            <RefreshCw size={14} />
            <span>Refresh Queue</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="cyber-card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '220px' }}>
            <Search size={16} color="var(--text-dim)" />
            <input 
              type="text"
              className="input-control"
              placeholder="Search alert description or attack vector..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Severity:</span>
            <select
              className="select-control"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Status:</span>
            <select
              className="select-control"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="cyber-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="cyber-table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Time</th>
                <th>Attack Vector</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Incident Status</th>
                <th>Triage Action</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => (
                  <tr key={alert.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      #{alert.id.toString().padStart(4, '0')}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                      {new Date(alert.timestamp).toLocaleString()}
                    </td>
                    <td>
                      <strong style={{ color: 'var(--text-main)' }}>{alert.attack_type}</strong>
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
                      <div style={{ display: 'flex', gap: '6px' }}>
                        {alert.status === 'OPEN' && (
                          <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleStatusUpdate(alert.id, 'INVESTIGATING')}
                            disabled={isUpdating}
                          >
                            Investigate
                          </button>
                        )}
                        {alert.status === 'INVESTIGATING' && (
                          <button 
                            className="btn btn-primary btn-sm"
                            onClick={() => handleStatusUpdate(alert.id, 'RESOLVED')}
                            disabled={isUpdating}
                          >
                            Resolve
                          </button>
                        )}
                        {alert.status === 'RESOLVED' && (
                          <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleStatusUpdate(alert.id, 'OPEN')}
                            disabled={isUpdating}
                          >
                            Re-Open
                          </button>
                        )}
                      </div>
                    </td>
                    <td>
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => setSelectedAlert(alert)}
                        title="View Full Forensic Details"
                      >
                        <Eye size={13} />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-dim)' }}>
                    No alerts match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Details Modal / Card */}
      {selectedAlert && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(7, 11, 20, 0.85)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px'
        }}>
          <div className="cyber-card" style={{ maxWidth: '600px', width: '100%', border: '1px solid var(--cyan-primary)' }}>
            <div className="cyber-card-header">
              <div className="card-title">
                <ShieldAlert size={20} color="var(--cyan-primary)" />
                <span>Alert Forensics #{selectedAlert.id.toString().padStart(4, '0')}</span>
              </div>
              <span className={`badge badge-${selectedAlert.severity}`}>
                {selectedAlert.severity}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Attack Classification</span>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--red-critical)' }}>
                  {selectedAlert.attack_type}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Description</span>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '2px' }}>
                  {selectedAlert.description}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ padding: '10px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>CONFIDENCE SCORE</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {(selectedAlert.confidence * 100).toFixed(2)}%
                  </div>
                </div>
                <div style={{ padding: '10px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>DETECTION TIMESTAMP</div>
                  <div style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                    {new Date(selectedAlert.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Change Incident Status</span>
                <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                  <button 
                    className={`btn btn-sm ${selectedAlert.status === 'OPEN' ? 'btn-danger' : 'btn-secondary'}`}
                    onClick={() => handleStatusUpdate(selectedAlert.id, 'OPEN')}
                  >
                    OPEN
                  </button>
                  <button 
                    className={`btn btn-sm ${selectedAlert.status === 'INVESTIGATING' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handleStatusUpdate(selectedAlert.id, 'INVESTIGATING')}
                  >
                    INVESTIGATING
                  </button>
                  <button 
                    className={`btn btn-sm ${selectedAlert.status === 'RESOLVED' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handleStatusUpdate(selectedAlert.id, 'RESOLVED')}
                  >
                    RESOLVED
                  </button>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedAlert(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
