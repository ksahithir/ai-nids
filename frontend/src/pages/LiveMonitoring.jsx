import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  StepForward, 
  Trash2, 
  Radio, 
  Search, 
  ShieldAlert,
  Info,
  CheckCircle2
} from 'lucide-react';
import api from '../services/api';

export default function LiveMonitoring({ onPacketAnalyzed }) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [intervalMs, setIntervalMs] = useState(1500);
  const [streamData, setStreamData] = useState([]);
  const [selectedPacket, setSelectedPacket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const timerRef = useRef(null);

  const fetchNextPacket = async () => {
    try {
      setIsLoading(true);
      const flow = await api.getSimulationFlow();
      if (flow && flow.prediction) {
        setStreamData((prev) => [flow, ...prev.slice(0, 49)]); // Keep last 50 packets
        if (!selectedPacket) {
          setSelectedPacket(flow);
        }
        if (onPacketAnalyzed) {
          onPacketAnalyzed();
        }
      }
    } catch (err) {
      console.error('Simulation stream error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isStreaming) {
      timerRef.current = setInterval(fetchNextPacket, intervalMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isStreaming, intervalMs]);

  const clearStream = () => {
    setStreamData([]);
    setSelectedPacket(null);
  };

  return (
    <div className="page-wrapper">
      {/* Simulation Info Notice */}
      <div style={{
        background: 'rgba(15, 23, 42, 0.8)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '14px 20px',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <Info size={20} color="var(--cyan-primary)" style={{ flexShrink: 0 }} />
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <strong>Dataset Simulation Mode:</strong> Telemetry is streamed sequentially from authentic CICIDS2017 test network flows through the active <strong>HistGradientBoosting</strong> machine learning pipeline.
        </div>
      </div>

      {/* Control Bar */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '16px 20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button 
            className={`btn ${isStreaming ? 'btn-danger' : 'btn-primary'}`}
            onClick={() => setIsStreaming(!isStreaming)}
          >
            {isStreaming ? (
              <>
                <Pause size={16} />
                <span>Pause Stream</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Start Stream</span>
              </>
            )}
          </button>

          <button 
            className="btn btn-secondary"
            onClick={fetchNextPacket}
            disabled={isStreaming || isLoading}
          >
            <StepForward size={16} />
            <span>Step (1 Flow)</span>
          </button>

          <button 
            className="btn btn-secondary"
            onClick={clearStream}
            disabled={streamData.length === 0}
          >
            <Trash2 size={16} />
            <span>Clear Log</span>
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Stream Interval:</span>
            <select 
              className="select-control"
              value={intervalMs}
              onChange={(e) => setIntervalMs(Number(e.target.value))}
            >
              <option value={500}>0.5s (Fast)</option>
              <option value={1000}>1.0s (Normal)</option>
              <option value={1500}>1.5s (Default)</option>
              <option value={3000}>3.0s (Slow)</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
            <Radio size={14} color={isStreaming ? 'var(--emerald-normal)' : 'var(--text-dim)'} className={isStreaming ? 'spin' : ''} />
            <span>{isStreaming ? 'STREAMING ACTIVE' : 'STREAM IDLE'}</span>
          </div>
        </div>
      </div>

      {/* Main Split: Stream Table & Packet Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '20px' }}>
        {/* Stream Table */}
        <div className="cyber-card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Live Network Flows ({streamData.length})</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Click row to inspect features</span>
          </div>

          <div style={{ maxHeight: '580px', overflowY: 'auto' }}>
            <table className="cyber-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>ML Classification</th>
                  <th>Confidence</th>
                  <th>Severity</th>
                  <th>Ground Truth</th>
                </tr>
              </thead>
              <tbody>
                {streamData.length > 0 ? (
                  streamData.map((pkt, idx) => {
                    const isSelected = selectedPacket === pkt;
                    return (
                      <tr 
                        key={idx}
                        onClick={() => setSelectedPacket(pkt)}
                        style={{ 
                          cursor: 'pointer',
                          backgroundColor: isSelected ? 'rgba(0, 240, 255, 0.08)' : undefined
                        }}
                      >
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                          {new Date(pkt.timestamp).toLocaleTimeString()}
                        </td>
                        <td>
                          <strong style={{ color: pkt.is_attack ? 'var(--red-critical)' : 'var(--emerald-normal)' }}>
                            {pkt.prediction}
                          </strong>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ width: '50px', height: '6px', background: 'var(--bg-surface)', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{ 
                                width: `${(pkt.confidence * 100)}%`, 
                                height: '100%', 
                                background: pkt.confidence > 0.8 ? 'var(--cyan-primary)' : 'var(--amber-medium)' 
                              }} />
                            </div>
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                              {(pkt.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </td>
                        <td>
                          <span className={`badge badge-${pkt.severity}`}>
                            {pkt.severity}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {pkt.actual_dataset_label || '—'}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-dim)' }}>
                      No streaming packets yet. Click <strong>Start Stream</strong> or <strong>Step</strong> to inspect traffic.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Packet Inspector Drawer */}
        <div className="cyber-card">
          <div className="cyber-card-header">
            <div className="card-title">
              <Search size={18} color="var(--cyan-primary)" />
              <span>Flow Feature Inspector</span>
            </div>
            {selectedPacket && (
              <span className={`badge badge-${selectedPacket.severity}`}>
                {selectedPacket.severity}
              </span>
            )}
          </div>

          {selectedPacket ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Prediction Summary Banner */}
              <div style={{
                background: selectedPacket.is_attack ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                border: `1px solid ${selectedPacket.is_attack ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                borderRadius: 'var(--radius-sm)',
                padding: '12px 16px'
              }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Model Decision
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: selectedPacket.is_attack ? 'var(--red-critical)' : 'var(--emerald-normal)' }}>
                  {selectedPacket.prediction}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Confidence: <strong>{(selectedPacket.confidence * 100).toFixed(2)}%</strong> • Ground Truth: <strong>{selectedPacket.actual_dataset_label}</strong>
                </div>
              </div>

              {/* Top Salient Features */}
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                  KEY SALIENT ATTRIBUTES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {selectedPacket.top_features?.map((f, i) => (
                    <div 
                      key={i}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        background: 'var(--bg-surface)',
                        borderRadius: 'var(--radius-sm)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.78rem'
                      }}
                    >
                      <span style={{ color: 'var(--cyan-primary)' }}>{f.feature}</span>
                      <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{f.value.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Multi-Class Probability Breakdown */}
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                  TOP CLASS PROBABILITIES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '180px', overflowY: 'auto' }}>
                  {Object.entries(selectedPacket.probabilities || {})
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 6)
                    .map(([clsName, prob], idx) => (
                      <div key={idx} style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                          <span style={{ color: clsName === selectedPacket.prediction ? 'var(--cyan-primary)' : 'var(--text-dim)' }}>
                            {clsName}
                          </span>
                          <span>{(prob * 100).toFixed(2)}%</span>
                        </div>
                        <div style={{ height: '4px', background: 'var(--bg-surface)', borderRadius: '2px', overflow: 'hidden' }}>
                          <div style={{ 
                            width: `${(prob * 100)}%`, 
                            height: '100%', 
                            background: clsName === selectedPacket.prediction ? 'var(--cyan-primary)' : 'var(--text-dim)' 
                          }} />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--text-dim)' }}>
              Select a network flow from the stream table to inspect its full feature vector and probabilistic score.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
