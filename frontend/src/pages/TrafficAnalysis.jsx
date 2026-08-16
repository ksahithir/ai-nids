import React, { useState } from 'react';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  ArrowDownToLine,
  Layers,
  Filter,
  RefreshCw
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend 
} from 'recharts';
import api from '../services/api';

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
};

export default function TrafficAnalysis({ onBatchComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.endsWith('.csv')) {
        setErrorMsg('Please select a valid .csv file.');
        return;
      }
      setSelectedFile(file);
      setErrorMsg(null);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const data = await api.predictBatch(formData);
      setBatchResults(data);
      if (onBatchComplete) {
        onBatchComplete();
      }
    } catch (err) {
      console.error('Batch upload error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to process CSV file. Ensure valid flow schema.');
    } finally {
      setIsUploading(false);
    }
  };

  const downloadSampleCsv = () => {
    window.open(api.getSampleCsvUrl(), '_blank');
  };

  const exportResultsCsv = () => {
    if (!batchResults?.sample_records) return;
    
    const records = batchResults.sample_records;
    const headers = ["id", "timestamp", "prediction", "is_attack", "confidence", "severity"];
    const csvRows = [headers.join(',')];

    records.forEach(r => {
      csvRows.push([
        r.id,
        `"${r.timestamp}"`,
        `"${r.prediction}"`,
        r.is_attack,
        r.confidence,
        `"${r.severity}"`
      ].join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_nids_prediction_results_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filter records
  const filteredRecords = (batchResults?.sample_records || []).filter(r => {
    const matchesSearch = searchTerm === '' || 
      r.prediction.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = filterSeverity === 'ALL' || r.severity === filterSeverity;
    return matchesSearch && matchesSeverity;
  });

  const attackDistData = Object.entries(batchResults?.summary?.attack_distribution || {}).map(([name, count]) => ({
    name,
    count
  })).sort((a, b) => b.count - a.count);

  const severityData = Object.entries(batchResults?.summary?.severity_distribution || {}).map(([name, value]) => ({
    name,
    value
  })).filter(d => d.value > 0);

  return (
    <div className="page-wrapper">
      {/* Top Banner & Sample Download */}
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
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Batch Network Traffic Analysis</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Upload raw network flow captures in CSV format for automated multi-class attack detection and threat severity triage.
          </p>
        </div>
        <div>
          <button className="btn btn-secondary" onClick={downloadSampleCsv}>
            <Download size={16} />
            <span>Download Sample Traffic CSV</span>
          </button>
        </div>
      </div>

      {/* Upload Box */}
      <div className="cyber-card" style={{ marginBottom: '24px' }}>
        <div style={{
          border: '2px dashed var(--border-highlight)',
          borderRadius: 'var(--radius-md)',
          padding: '36px 20px',
          textAlign: 'center',
          backgroundColor: 'rgba(15, 23, 42, 0.4)',
          cursor: 'pointer'
        }}>
          <UploadCloud size={44} color="var(--cyan-primary)" style={{ margin: '0 auto 12px auto' }} />
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {selectedFile ? selectedFile.name : 'Select or drag & drop network traffic CSV'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '6px' }}>
            Supports standard CICIDS2017 flow attribute schemas (up to 50MB)
          </div>

          <input 
            type="file" 
            accept=".csv" 
            id="csv-upload-input"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '12px' }}>
            <label htmlFor="csv-upload-input" className="btn btn-secondary">
              <FileSpreadsheet size={16} />
              <span>Browse CSV File</span>
            </label>

            {selectedFile && (
              <button 
                className="btn btn-primary"
                onClick={handleUploadAndAnalyze}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    <span>Analyzing Flows...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    <span>Execute AI-NIDS Analysis</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {errorMsg && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: 'var(--radius-sm)',
            color: '#f87171',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Batch Results View */}
      {batchResults && (
        <>
          {/* Summary KPIs */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Total Records Evaluated</div>
              <div className="stat-value">{batchResults.summary.total_records.toLocaleString()}</div>
              <div className="stat-subtext">Processed in memory</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Normal Flows</div>
              <div className="stat-value" style={{ color: 'var(--emerald-normal)' }}>
                {batchResults.summary.normal_records.toLocaleString()}
              </div>
              <div className="stat-subtext">
                {((batchResults.summary.normal_records / batchResults.summary.total_records) * 100).toFixed(1)}% benign
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Attacks Detected</div>
              <div className="stat-value" style={{ color: 'var(--red-critical)' }}>
                {batchResults.summary.attack_records.toLocaleString()}
              </div>
              <div className="stat-subtext">
                {((batchResults.summary.attack_records / batchResults.summary.total_records) * 100).toFixed(1)}% malicious
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Mean Confidence</div>
              <div className="stat-value" style={{ color: 'var(--cyan-primary)' }}>
                {(batchResults.summary.avg_confidence * 100).toFixed(1)}%
              </div>
              <div className="stat-subtext">Model certainty</div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid-2">
            <div className="cyber-card">
              <div className="cyber-card-header">
                <div className="card-title">
                  <span>Attack Distribution in Batch</span>
                </div>
              </div>
              <div style={{ height: 240 }}>
                {attackDistData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={attackDistData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
                      <XAxis dataKey="name" stroke="var(--text-dim)" fontSize={11} angle={-25} textAnchor="end" interval={0} />
                      <YAxis stroke="var(--text-dim)" fontSize={11} />
                      <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }} />
                      <Bar dataKey="count" fill="var(--cyan-primary)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
                    No attacks in this batch.
                  </div>
                )}
              </div>
            </div>

            <div className="cyber-card">
              <div className="cyber-card-header">
                <div className="card-title">
                  <span>Batch Severity Profile</span>
                </div>
              </div>
              <div style={{ height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={severityData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                      {severityData.map((entry) => (
                        <Cell key={`cell-${entry.name}`} fill={SEVERITY_COLORS[entry.name] || '#64748b'} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }} />
                    <Legend formatter={(v) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{v}</span>} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Results Table with Search and CSV Export */}
          <div className="cyber-card">
            <div className="cyber-card-header">
              <div className="card-title">
                <span>Predicted Flow Records (Sample View)</span>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <input 
                  type="text"
                  placeholder="Filter attack type..."
                  className="input-control"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{ width: '180px' }}
                />
                <select
                  className="select-control"
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                >
                  <option value="ALL">All Severities</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
                <button className="btn btn-secondary btn-sm" onClick={exportResultsCsv}>
                  <ArrowDownToLine size={14} />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            <div className="cyber-table-container" style={{ maxHeight: '420px', overflowY: 'auto' }}>
              <table className="cyber-table">
                <thead>
                  <tr>
                    <th>Record ID</th>
                    <th>Classification</th>
                    <th>Confidence</th>
                    <th>Severity</th>
                    <th>Intrusion Type</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((r, i) => (
                    <tr key={i}>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>#{r.id}</td>
                      <td>
                        <strong style={{ color: r.is_attack ? 'var(--red-critical)' : 'var(--emerald-normal)' }}>
                          {r.prediction}
                        </strong>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>
                        {(r.confidence * 100).toFixed(1)}%
                      </td>
                      <td>
                        <span className={`badge badge-${r.severity}`}>
                          {r.severity}
                        </span>
                      </td>
                      <td>
                        {r.is_attack ? (
                          <span style={{ color: 'var(--red-critical)', fontSize: '0.78rem' }}>● MALICIOUS</span>
                        ) : (
                          <span style={{ color: 'var(--emerald-normal)', fontSize: '0.78rem' }}>● BENIGN</span>
                        )}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                        {new Date(r.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
