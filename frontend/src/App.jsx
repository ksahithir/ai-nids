import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import LiveMonitoring from './pages/LiveMonitoring';
import TrafficAnalysis from './pages/TrafficAnalysis';
import AttackAnalytics from './pages/AttackAnalytics';
import AlertCenter from './pages/AlertCenter';
import ModelPerformance from './pages/ModelPerformance';
import SystemInfo from './pages/SystemInfo';
import api from './services/api';

const PAGE_TITLES = {
  'dashboard': 'AI-NIDS Security Operations Center',
  'live-monitoring': 'Live Network Flow & Simulation Stream',
  'traffic-analysis': 'Traffic Batch Analysis & CSV Triage',
  'attack-analytics': 'Attack Intelligence & Vector Analytics',
  'alerts': 'SOC Security Alert Queue',
  'model-performance': 'Machine Learning Validation Audit',
  'system-info': 'System Specifications & Hardware Profile',
};

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchGlobalData = useCallback(async () => {
    try {
      setLoading(true);
      const [s, a] = await Promise.all([
        api.getStatistics(),
        api.getAlerts({ limit: 100 })
      ]);
      setStats(s);
      setAlerts(a);
    } catch (err) {
      console.error('Failed to load global data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGlobalData();
  }, [fetchGlobalData]);

  const handleAlertStatusChange = async (alertId, newStatus) => {
    setAlerts((prev) => 
      prev.map((a) => a.id === alertId ? { ...a, status: newStatus } : a)
    );
    // Refresh stats to update threat status
    try {
      const s = await api.getStatistics();
      setStats(s);
    } catch (err) {
      console.error('Failed to refresh stats:', err);
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard 
            stats={stats} 
            alerts={alerts} 
            onAlertStatusChange={handleAlertStatusChange}
            onNavigate={setActiveTab}
          />
        );
      case 'live-monitoring':
        return (
          <LiveMonitoring 
            onPacketAnalyzed={fetchGlobalData}
          />
        );
      case 'traffic-analysis':
        return (
          <TrafficAnalysis 
            onBatchComplete={fetchGlobalData}
          />
        );
      case 'attack-analytics':
        return (
          <AttackAnalytics 
            stats={stats}
          />
        );
      case 'alerts':
        return (
          <AlertCenter 
            alerts={alerts}
            onAlertStatusChange={handleAlertStatusChange}
            refreshAlerts={fetchGlobalData}
          />
        );
      case 'model-performance':
        return <ModelPerformance />;
      case 'system-info':
        return <SystemInfo />;
      default:
        return <Dashboard stats={stats} alerts={alerts} onAlertStatusChange={handleAlertStatusChange} onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        <Header 
          title={PAGE_TITLES[activeTab] || 'AI-NIDS'} 
          stats={stats}
          onRefresh={fetchGlobalData}
          loading={loading}
        />
        {renderActivePage()}
      </div>
    </div>
  );
}
