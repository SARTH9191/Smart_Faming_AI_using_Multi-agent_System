import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard({ farmId, apiUrl, onNavigate }) {
  const [dashboardData, setDashboardData]   = useState(null);
  const [sensorData, setSensorData]         = useState(null);
  const [realtimeRecs, setRealtimeRecs]     = useState([]);
  const [loading, setLoading]               = useState(true);
  const [lastUpdate, setLastUpdate]         = useState(null);
  const [isRunningAgents, setIsRunningAgents] = useState(false);
  const [showDevTools, setShowDevTools]     = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchRealtimeRecommendations();
    const d = setInterval(fetchDashboardData, 30000);
    const r = setInterval(fetchRealtimeRecommendations, 10000);
    return () => { clearInterval(d); clearInterval(r); };
  }, [farmId, apiUrl]);

  const fetchDashboardData = async () => {
    try {
      const res = await axios.get(`${apiUrl}/dashboard?farm_id=${farmId}`);
      setDashboardData(res.data);
      if (res.data.sensors) {
        setSensorData(Array.isArray(res.data.sensors) ? res.data.sensors[0] : res.data.sensors);
      }
    } catch (e) { /* silent */ }
    finally { setLoading(false); }
  };

  const fetchRealtimeRecommendations = async () => {
    try {
      const res = await axios.get(`${apiUrl}/realtime_recommendations?farm_id=${farmId}`);
      setRealtimeRecs(res.data.recommendations || []);
      setLastUpdate(new Date());
    } catch (e) { /* silent */ }
  };

  const triggerScenario = async (scenario) => {
    try {
      await axios.post(`${apiUrl}/test/scenario/${scenario}?farm_id=${encodeURIComponent(farmId)}`);
      await Promise.all([fetchDashboardData(), fetchRealtimeRecommendations()]);
    } catch (e) { alert(`❌ ${e.message}`); }
  };

  const handleRunAgents = async () => {
    setIsRunningAgents(true);
    try {
      await axios.post(`${apiUrl}/api/agent/run`, { farm_id: farmId, query: "Full farm analysis", location: "Pune", crop_type: "wheat" });
      await fetchDashboardData();
    } catch (e) { alert(`❌ Error running agents: ${e.message}`); }
    finally { setIsRunningAgents(false); }
  };

  if (loading) {
    return (
      <div className="sf-loading">
        <div className="sf-spinner" />
        <span>Loading farm data…</span>
      </div>
    );
  }

  const soil   = sensorData?.soil_moisture;
  const temp   = sensorData?.air_temperature;
  const ph     = sensorData?.soil_ph;

  const moistureStatus = !soil ? 'gray' : soil >= 50 ? 'green' : soil >= 35 ? 'amber' : 'red';
  const tempStatus     = !temp ? 'gray' : temp <= 30 ? 'green' : temp <= 35 ? 'amber' : 'red';
  const phStatus       = !ph ? 'gray' : (ph >= 6.0 && ph <= 7.5) ? 'green' : 'amber';

  const criticalRecs = realtimeRecs.filter(r => r.priority === 'critical');
  const otherRecs    = realtimeRecs.filter(r => r.priority !== 'critical');

  const SENSOR_CARDS = [
    {
      icon: '💧', label: 'Soil Moisture',
      value: soil?.toFixed(1) ?? '—',
      unit: '%',
      status: moistureStatus,
      statBg: moistureStatus === 'green' ? 'rgba(22,163,74,0.12)' : moistureStatus === 'amber' ? 'rgba(217,119,6,0.12)' : 'rgba(220,38,38,0.12)',
      statColor: moistureStatus === 'green' ? '#16a34a' : moistureStatus === 'amber' ? '#d97706' : '#dc2626',
    },
    {
      icon: '🌡️', label: 'Air Temperature',
      value: temp?.toFixed(1) ?? '—',
      unit: '°C',
      status: tempStatus,
      statBg: tempStatus === 'green' ? 'rgba(22,163,74,0.12)' : tempStatus === 'amber' ? 'rgba(217,119,6,0.12)' : 'rgba(220,38,38,0.12)',
      statColor: tempStatus === 'green' ? '#16a34a' : tempStatus === 'amber' ? '#d97706' : '#dc2626',
    },
    {
      icon: '🌱', label: 'Soil Temp',
      value: sensorData?.soil_temperature?.toFixed(1) ?? '—',
      unit: '°C',
      status: 'neutral',
      statBg: 'rgba(13,148,136,0.12)',
      statColor: '#0d9488',
    },
    {
      icon: '🧪', label: 'Soil pH',
      value: ph?.toFixed(1) ?? '—',
      unit: '',
      status: phStatus,
      statBg: phStatus === 'green' ? 'rgba(22,163,74,0.12)' : 'rgba(217,119,6,0.12)',
      statColor: phStatus === 'green' ? '#16a34a' : '#d97706',
    },
    {
      icon: '🌿', label: 'Nitrogen (N)',
      value: sensorData?.npk_nitrogen?.toFixed(0) ?? '—',
      unit: 'mg/kg',
      status: 'neutral',
      statBg: 'rgba(34,197,94,0.12)',
      statColor: '#16a34a',
    },
    {
      icon: '⚡', label: 'Phosphorus (P)',
      value: sensorData?.npk_phosphorus?.toFixed(0) ?? '—',
      unit: 'mg/kg',
      status: 'neutral',
      statBg: 'rgba(245,158,11,0.1)',
      statColor: '#d97706',
    },
    {
      icon: '🔋', label: 'Potassium (K)',
      value: sensorData?.npk_potassium?.toFixed(0) ?? '—',
      unit: 'mg/kg',
      status: 'neutral',
      statBg: 'rgba(37,99,235,0.1)',
      statColor: '#2563eb',
    },
  ];

  return (
    <div className="sf-page">

      {/* ── Page Header ── */}
      <div className="sf-section-header" style={{ marginBottom: 'var(--s5)' }}>
        <div className="sf-section-title">
          <h2>Farm Dashboard</h2>
          <p>
            Live sensor data from Farm {farmId}
            {lastUpdate && ` · Updated ${lastUpdate.toLocaleTimeString()}`}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--s3)', flexWrap: 'wrap' }}>
          <button
            className="sf-btn sf-btn-secondary sf-btn-sm"
            onClick={() => setShowDevTools(v => !v)}
          >
            🧪 {showDevTools ? 'Hide' : 'Scenarios'}
          </button>
          <button
            className="sf-btn sf-btn-primary"
            onClick={handleRunAgents}
            disabled={isRunningAgents}
            style={{ background: '#7c3aed', borderColor: '#7c3aed' }}
          >
            {isRunningAgents ? '⏳ Analyzing…' : '🧠 Run AI Analysis'}
          </button>
        </div>
      </div>

      {/* ── Dev Tools ── */}
      {showDevTools && (
        <div style={{
          background: 'var(--surface-2)', border: '1px solid var(--border)',
          borderRadius: 'var(--r-md)', padding: 'var(--s4)', marginBottom: 'var(--s5)',
          display: 'flex', flexWrap: 'wrap', gap: 'var(--s2)', alignItems: 'center'
        }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginRight: 'var(--s2)' }}>Test Scenarios:</span>
          {[
            { id: 'optimal',          label: '✅ Optimal',   color: '#16a34a' },
            { id: 'low_moisture',     label: '💧 Low Moisture', color: '#2563eb' },
            { id: 'high_temperature', label: '🔥 Heat Stress', color: '#d97706' },
            { id: 'multiple_issues',  label: '🚨 Emergency',   color: '#dc2626' },
          ].map(s => (
            <button key={s.id} onClick={() => triggerScenario(s.id)}
              className="sf-btn sf-btn-sm"
              style={{ background: s.color + '18', color: s.color, border: `1px solid ${s.color}40`, fontWeight: 600, fontSize: 12 }}>
              {s.label}
            </button>
          ))}
        </div>
      )}

      {/* ── Critical Alerts ── */}
      {criticalRecs.length > 0 && (
        <div style={{ marginBottom: 'var(--s5)' }}>
          {criticalRecs.map((rec, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 'var(--s3)',
              background: 'var(--red-dim)', border: '1px solid rgba(220,38,38,0.3)',
              borderRadius: 'var(--r-md)', padding: 'var(--s3) var(--s4)',
              marginBottom: 'var(--s2)', fontSize: 13
            }}>
              <span style={{ fontSize: 20 }}>🚨</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, color: 'var(--red)' }}>{rec.title}</div>
                <div style={{ color: '#374151' }}>{rec.message}</div>
                {rec.action && <div style={{ marginTop: 3, color: 'var(--text-3)', fontSize: 12 }}>💡 {rec.action}</div>}
              </div>
              <span className="sf-badge sf-badge-red">Critical</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Sensor KPI Grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 'var(--s4)', marginBottom: 'var(--s6)' }}>
        {SENSOR_CARDS.map(card => (
          <div key={card.label} className="sf-stat-card"
            style={{ '--stat-color': card.statColor, '--stat-bg': card.statBg }}>
            <div className="sf-stat-icon">{card.icon}</div>
            <div className="sf-stat-value">
              {card.value}
              {card.unit && <span style={{ fontSize: 14, fontWeight: 400, color: 'var(--text-3)', marginLeft: 3 }}>{card.unit}</span>}
            </div>
            <div className="sf-stat-label">{card.label}</div>
          </div>
        ))}
      </div>

      {/* ── Two Column: AI Recs + Alerts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--s5)', marginBottom: 'var(--s6)' }}>
        {/* AI Recommendations */}
        <div className="sf-card">
          <div style={{ padding: 'var(--s4) var(--s5)', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🧠</span> AI Recommendations
            </div>
            <button className="sf-btn sf-btn-ghost sf-btn-sm"
              style={{ color: '#7c3aed' }} onClick={handleRunAgents} disabled={isRunningAgents}>
              {isRunningAgents ? '⏳' : '🔄 Refresh'}
            </button>
          </div>
          <div style={{ padding: 'var(--s4) var(--s5)', maxHeight: 360, overflowY: 'auto' }}>
            {dashboardData?.recommendations?.length > 0 ? (
              dashboardData.recommendations.map((rec, i) => (
                <div key={i} style={{
                  padding: 'var(--s3) var(--s4)',
                  background: 'rgba(124,58,237,0.06)',
                  borderLeft: '3px solid #7c3aed',
                  borderRadius: 'var(--r-md)',
                  marginBottom: 'var(--s3)',
                  fontSize: 13,
                  whiteSpace: 'pre-wrap', lineHeight: 1.6,
                }}>
                  <div style={{ color: 'var(--text)' }}>{rec.recommendation_text}</div>
                  <div style={{ marginTop: 6, fontSize: 11, color: '#7c3aed', fontWeight: 600 }}>
                    🤖 {rec.agent_name} · {new Date(rec.timestamp).toLocaleString()}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: 'var(--s8)', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>🧠</div>
                <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--text-3)' }}>No recommendations yet</div>
                <div style={{ fontSize: 12 }}>Click "Run AI Analysis" to generate insights</div>
              </div>
            )}
          </div>
        </div>

        {/* Real-time Alerts */}
        <div className="sf-card">
          <div style={{ padding: 'var(--s4) var(--s5)', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🔔</span> Real-Time Alerts
            </div>
            {lastUpdate && (
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{lastUpdate.toLocaleTimeString()}</span>
            )}
          </div>
          <div style={{ padding: 'var(--s4) var(--s5)', maxHeight: 360, overflowY: 'auto' }}>
            {otherRecs.length > 0 ? (
              otherRecs.map((rec, i) => {
                const isWarn = rec.priority === 'warning';
                return (
                  <div key={i} style={{
                    padding: 'var(--s3) var(--s4)',
                    background: isWarn ? 'var(--amber-dim)' : 'var(--green-dim)',
                    borderLeft: `3px solid ${isWarn ? 'var(--amber)' : 'var(--green)'}`,
                    borderRadius: 'var(--r-md)',
                    marginBottom: 'var(--s3)',
                    fontSize: 13,
                  }}>
                    <div style={{ fontWeight: 700, color: isWarn ? 'var(--amber)' : 'var(--green)', marginBottom: 3 }}>{rec.title}</div>
                    <div style={{ color: 'var(--text-2)' }}>{rec.message}</div>
                    {rec.action && <div style={{ marginTop: 4, fontSize: 12, color: 'var(--text-3)' }}>💡 {rec.action}</div>}
                  </div>
                );
              })
            ) : (
              <div style={{ textAlign: 'center', padding: 'var(--s8)', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
                <div style={{ fontWeight: 600, color: 'var(--green)', marginBottom: 4 }}>All systems normal</div>
                <div style={{ fontSize: 12 }}>No active alerts for your farm</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Quick Actions ── */}
      <div className="sf-card sf-card-pad">
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 'var(--s4)', display: 'flex', alignItems: 'center', gap: 8 }}>
          ⚡ Quick Actions
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--s3)' }}>
          {[
            { label: 'Log an Action',    icon: '📝', tab: 'actions',    color: '#2563eb' },
            { label: 'Check Weather',    icon: '🌤️', tab: 'weather',    color: '#0d9488' },
            { label: 'View Market',      icon: '💰', tab: 'market',     color: '#d97706' },
            { label: 'Manage Crops',     icon: '🌾', tab: 'crops',      color: '#16a34a' },
            { label: 'Satellite View',   icon: '🛰️', tab: 'satellite',  color: '#7c3aed' },
            { label: 'Open Marketplace', icon: '🏪', tab: 'marketplace', color: '#dc2626' },
          ].map(qa => (
            <button key={qa.tab}
              onClick={() => onNavigate && onNavigate(qa.tab)}
              className="sf-btn sf-btn-secondary sf-btn-sm"
              style={{ gap: 6 }}>
              {qa.icon} {qa.label}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}

export default Dashboard;
