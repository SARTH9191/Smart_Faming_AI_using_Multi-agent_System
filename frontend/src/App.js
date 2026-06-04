import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import WeatherView from './components/WeatherView';
import MarketView from './components/MarketView';
import MarketplaceView from './components/MarketplaceView';

import VoiceAssistant from './components/VoiceAssistant';
import CropsManager from './components/CropsManager';
import ActionsLog from './components/ActionsLog';
import SatelliteView from './components/SatelliteView';
import ProfileView from './components/ProfileView';
import LanguageSelector from './components/LanguageSelector';
import AgroBrainOS from './components/AgroBrainOS';
import AdminPanel from './components/AdminPanel';
import { useLanguage } from './context/LanguageContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const getFarmIdFromFarmer = (farmerData) => {
  if (!farmerData) return 'FARM001';
  return farmerData.farmerId || farmerData.farmer_id || 'FARM001';
};

const TABS = [
  { id: 'dashboard',   icon: '📊', label: 'Dashboard' },
  { id: 'analytics',   icon: '🧠', label: 'AgroBrain OS' },
  { id: 'profile',     icon: '👤', label: 'Profile' },
  { id: 'crops',       icon: '🌾', label: 'Crops' },
  { id: 'actions',     icon: '📝', label: 'Actions Log' },
  { id: 'weather',     icon: '🌤️', label: 'Weather' },
  { id: 'market',      icon: '💰', label: 'Market' },
  { id: 'satellite',   icon: '🛰️', label: 'Satellite' },
  { id: 'marketplace', icon: '🏪', label: 'Marketplace' },
  { id: 'agents',      icon: '🤖', label: 'Run Agents', special: 'run' },
];

// ── Run All Agents Tab ────────────────────────────────────────────
function RunAgentsView({ farmId, apiUrl }) {
  const [loading, setLoading] = useState(false);
  const [agentLogs, setAgentLogs] = useState([]);
  const [lastRun, setLastRun] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | running | done | error

  const agents = [
    { id: 'crop_advisor',     name: 'Crop Advisor Agent',      icon: '🌾', description: 'Analyzes soil and crop conditions to provide planting recommendations.' },
    { id: 'irrigation',       name: 'Irrigation Agent',         icon: '💧', description: 'Monitors soil moisture and schedules intelligent irrigation cycles.' },
    { id: 'pest_detection',   name: 'Pest Detection Agent',     icon: '🐛', description: 'Scans satellite and sensor data for early pest or disease signals.' },
    { id: 'market_intel',     name: 'Market Intelligence',      icon: '📈', description: 'Tracks crop prices and identifies best selling windows.' },
    { id: 'weather_agent',    name: 'Weather Risk Agent',       icon: '🌩️', description: 'Analyzes forecasts and flags weather-related crop risks.' },
    { id: 'token_agent',      name: 'Green Token Verifier',     icon: '🌱', description: 'Validates eco-actions and calculates token rewards.' },
    { id: 'satellite_agent',  name: 'Satellite Analysis Agent', icon: '🛰️', description: 'Processes satellite imagery for NDVI and field zone analysis.' },
  ];

  const handleRunAll = async () => {
    setLoading(true);
    setStatus('running');
    setAgentLogs([]);

    try {
      const res = await axios.post(`${apiUrl}/run_agents?farm_id=${farmId}`);
      const ts = new Date().toLocaleTimeString();
      setLastRun(ts);

      if (res.data?.error) {
        setStatus('error');
        setAgentLogs([{ type: 'error', msg: res.data.error, time: ts }]);
      } else {
        setStatus('done');
        setAgentLogs([
          { type: 'success', msg: '✅ All AI agents executed successfully!', time: ts },
          { type: 'info', msg: `📋 Recommendations updated. Check the Dashboard for insights.`, time: ts },
        ]);
      }
    } catch (err) {
      const ts = new Date().toLocaleTimeString();
      setLastRun(ts);
      setStatus('error');
      const msg = err.code === 'ERR_NETWORK'
        ? 'Backend server is not running. Please start the backend first.'
        : err.response?.data?.detail || err.message || 'Unknown error';
      setAgentLogs([{ type: 'error', msg: `❌ ${msg}`, time: ts }]);
    } finally {
      setLoading(false);
    }
  };

  const statusColors = { idle: '#6b7280', running: '#7c3aed', done: '#16a34a', error: '#dc2626' };
  const statusLabels = { idle: 'Ready', running: 'Running…', done: 'Completed', error: 'Error' };

  return (
    <div className="sf-page">
      {/* Header */}
      <div className="sf-section-header">
        <div className="sf-section-title">
          <h2>🤖 Run All Agents</h2>
          <p>Execute the full AI agent orchestration pipeline for Farm {farmId}</p>
        </div>
        <button
          className="sf-btn sf-btn-primary sf-btn-lg"
          onClick={handleRunAll}
          disabled={loading}
          style={{ background: '#7c3aed', borderColor: '#7c3aed', boxShadow: '0 2px 8px rgba(124,58,237,0.3)' }}
        >
          {loading ? '⏳ Running All Agents…' : '🚀 Run All Agents'}
        </button>
      </div>

      {/* System Health */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 'var(--s4)', marginBottom: 'var(--s6)' }}>
        {[
          { label: 'System Status', value: statusLabels[status], color: statusColors[status] },
          { label: 'Total Agents',  value: agents.length, color: '#16a34a' },
          { label: 'Farm ID',       value: farmId, color: '#2563eb' },
          { label: 'Last Run',      value: lastRun || '—', color: '#6b7280' },
        ].map(s => (
          <div key={s.label} className="sf-stat-card" style={{ '--stat-color': s.color, '--stat-bg': s.color + '18' }}>
            <div className="sf-stat-icon" style={{ fontSize: 14 }}>
              {s.label === 'System Status' ? (status === 'running' ? '⚡' : status === 'done' ? '✅' : status === 'error' ? '❌' : '💤') :
               s.label === 'Total Agents' ? '🤖' : s.label === 'Farm ID' ? '🏡' : '🕐'}
            </div>
            <div className="sf-stat-value" style={{ fontSize: 18 }}>{s.value}</div>
            <div className="sf-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Warning Banner */}
      {status === 'running' && (
        <div style={{ background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.3)', borderRadius: 'var(--r-md)', padding: 'var(--s4)', marginBottom: 'var(--s5)', display: 'flex', gap: 'var(--s3)', alignItems: 'center', color: '#7c3aed', fontSize: 13 }}>
          <span style={{ fontSize: 18 }}>⚡</span>
          <span><strong>Agents are running.</strong> This may take 30–60 seconds. Do not close the tab.</span>
        </div>
      )}

      {/* Agent Cards */}
      <div style={{ marginBottom: 'var(--s6)' }}>
        <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 'var(--s3)' }}>
          Agent Pipeline
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s3)' }}>
          {agents.map((ag, i) => (
            <div key={ag.id} className="sf-card sf-card-pad" style={{ display: 'flex', alignItems: 'center', gap: 'var(--s4)' }}>
              <div style={{ width: 44, height: 44, borderRadius: 'var(--r-md)', background: 'rgba(124,58,237,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0 }}>
                {ag.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text)', marginBottom: 3 }}>{ag.name}</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{ag.description}</div>
              </div>
              <div>
                <span className="sf-badge" style={{
                  background: status === 'running' ? 'rgba(124,58,237,0.1)' : status === 'done' ? 'var(--green-dim)' : status === 'error' ? 'var(--red-dim)' : 'var(--surface-3)',
                  color: status === 'running' ? '#7c3aed' : status === 'done' ? 'var(--green)' : status === 'error' ? 'var(--red)' : 'var(--text-muted)',
                }}>
                  {status === 'running' ? '⏳ Running' : status === 'done' ? '✅ Done' : status === 'error' ? '❌ Failed' : '💤 Idle'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Activity Log */}
      {agentLogs.length > 0 && (
        <div className="sf-card">
          <div style={{ padding: 'var(--s4) var(--s5)', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: 14 }}>
            📋 Run Output
          </div>
          <div style={{ padding: 'var(--s4) var(--s5)' }}>
            {agentLogs.map((log, i) => (
              <div key={i} style={{
                padding: 'var(--s3) var(--s4)',
                background: log.type === 'error' ? 'var(--red-dim)' : log.type === 'success' ? 'var(--green-dim)' : 'var(--surface-2)',
                borderRadius: 'var(--r-md)',
                marginBottom: 'var(--s2)',
                fontSize: 13,
                color: log.type === 'error' ? 'var(--red)' : log.type === 'success' ? 'var(--green)' : 'var(--text-2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 'var(--s3)',
              }}>
                <span>{log.msg}</span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', flexShrink: 0 }}>{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────
function App() {
  const { t } = useLanguage();
  const [farmer, setFarmer]         = useState(null);
  const [activeTab, setActiveTab]   = useState('dashboard');
  const [farmId, setFarmId]         = useState('FARM001');
  const [showAdminApp, setShowAdminApp] = useState(() => !!localStorage.getItem('admin_token'));

  useEffect(() => {
    const storedFarmer = localStorage.getItem('farmer');
    if (storedFarmer) {
      const p = JSON.parse(storedFarmer);
      setFarmer(p);
      setFarmId(getFarmIdFromFarmer(p));
    }
  }, []);

  useEffect(() => {
    if (farmer) initializeSensors(getFarmIdFromFarmer(farmer));
  }, [farmer]);

  const initializeSensors = async (targetFarmId = farmId) => {
    try {
      await axios.post(`${API_BASE_URL}/simulate_sensors`, { farm_id: targetFarmId, duration_minutes: 10 });
    } catch (e) { /* silent */ }
  };

  const handleLogin = (data) => { setFarmer(data); setFarmId(getFarmIdFromFarmer(data)); };
  const handleLogout = () => { localStorage.removeItem('farmer'); setFarmer(null); setActiveTab('dashboard'); };
  const handleAdminLogout = () => setShowAdminApp(false);

  if (showAdminApp) return <AdminPanel onLogout={handleAdminLogout} />;
  if (!farmer)      return <Login onLogin={handleLogin} onAdminClick={() => setShowAdminApp(true)} />;

  const farmerName  = farmer?.name || 'Farmer';
  const farmIdShort = farmId;

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">🌾</div>
          <div>
            <h1>Smart Farming AI</h1>
            <div className="header-sub">Powered by AgroBrain OS</div>
          </div>
        </div>
        <div className="header-actions">
          <LanguageSelector />
          <div className="header-farmer-pill">
            <div className="header-farmer-avatar">{farmerName[0].toUpperCase()}</div>
            <span>{farmerName}</span>
            <span style={{ opacity: 0.6, fontSize: 11 }}>· {farmIdShort}</span>
          </div>
          <button className="header-logout" onClick={handleLogout}>
            🚪 {t('logout')}
          </button>
        </div>
      </header>

      {/* ── Navigation ── */}
      <nav className="nav">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`nav-btn${tab.special === 'run' ? ' nav-run' : ''}${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="nav-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ── Content ── */}
      <div className="container">
        {activeTab === 'dashboard'   && <Dashboard farmId={farmId} apiUrl={API_BASE_URL} onNavigate={setActiveTab} />}
        {activeTab === 'analytics'   && <AgroBrainOS farmId={farmId} apiUrl={API_BASE_URL} />}
        {activeTab === 'profile'     && <ProfileView farmer={farmer} apiUrl={API_BASE_URL} />}
        {activeTab === 'crops'       && <CropsManager farmId={farmId} apiUrl={API_BASE_URL} />}
        {activeTab === 'actions'     && <ActionsLog farmId={farmId} farmer={farmer} />}
        {activeTab === 'weather'     && <WeatherView apiUrl={API_BASE_URL} />}
        {activeTab === 'market'      && <MarketView apiUrl={API_BASE_URL} />}
        {activeTab === 'satellite'   && <SatelliteView farmId={farmId} apiUrl={API_BASE_URL} />}
        {activeTab === 'marketplace' && <MarketplaceView />}
        {activeTab === 'agents'      && <RunAgentsView farmId={farmId} apiUrl={API_BASE_URL} />}
      </div>

      {/* ── Voice Assistant ── */}
      <VoiceAssistant apiUrl={API_BASE_URL} farmer={farmer} />
    </div>
  );
}

export default App;
