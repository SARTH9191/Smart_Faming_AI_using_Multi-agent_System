import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard({ farmId, apiUrl }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [sensorData, setSensorData] = useState(null);
  const [realtimeRecs, setRealtimeRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRunningAgents, setIsRunningAgents] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchRealtimeRecommendations();
   
    


    
    // Refresh dashboard every 30 seconds
    const dashboardInterval = setInterval(fetchDashboardData, 30000);
    
    // Refresh real-time recommendations every 10 seconds
    const recsInterval = setInterval(fetchRealtimeRecommendations, 10000);
    
    return () => {
      clearInterval(dashboardInterval);
      clearInterval(recsInterval);
    };
  }, [farmId]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${apiUrl}/dashboard?farm_id=${farmId}`);
      setDashboardData(response.data);
      
      if (response.data.sensors && response.data.sensors.length > 0) {
        setSensorData(response.data.sensors[0]);
      }
      
      setLoading(false);
    } catch (error) {
      if (error.code === 'ERR_NETWORK') {
        console.warn('Backend not available - will retry...');
      } else {
        console.error('Error fetching dashboard data:', error);
      }
      setLoading(false);
    }
  };

  const fetchRealtimeRecommendations = async () => {
    try {
      const response = await axios.get(`${apiUrl}/realtime_recommendations?farm_id=${farmId}`);
      setRealtimeRecs(response.data.recommendations || []);
      setLastUpdate(new Date());
    } catch (error) {
      if (error.code !== 'ERR_NETWORK') {
        console.error('Error fetching real-time recommendations:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  const triggerScenario = async (scenario) => {
    try {
      const targetFarmId = farmId || 'FARM001';
      const response = await axios.post(`${apiUrl}/test/scenario/${scenario}?farm_id=${encodeURIComponent(targetFarmId)}`);
      await fetchDashboardData();
      await fetchRealtimeRecommendations();
      alert(`Γ£à ${response.data.message}\n\nDashboard updated successfully.`);
    } catch (error) {
      if (error.code === 'ERR_NETWORK') {
        alert(`Γ¥î Network Error: Backend server is not running.\n\nPlease start the backend server first.`);
      } else {
        alert(`Γ¥î Error: ${error.response?.data?.detail || error.message}\n\nMake sure backend is running!`);
      }
    }
  };

  const handleRunAgents = async () => {
    setIsRunningAgents(true);
    try {
      const targetFarmId = farmId || 'FARM001';
      await axios.post(`${apiUrl}/run_agents?farm_id=${encodeURIComponent(targetFarmId)}`);
      await fetchDashboardData(); 
      alert("Γ£à Agents successfully executed and conflicts resolved via Mistral!");
    } catch (error) {
      alert(`Γ¥î Error running orchestrator: ${error.message}`);
    }
    setIsRunningAgents(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.75rem', margin: 0 }}>≡ƒÄ¢∩╕Å Real-Time Farm Dashboard</h2>
        
        {/* Test Scenario Buttons */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => triggerScenario('low_moisture')}
            style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '600'
            }}
            title="Simulate critical low moisture"
          >
            ≡ƒÜ¿ Test: Low Moisture
          </button>
          <button
            onClick={() => triggerScenario('high_temperature')}
            style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '600'
            }}
            title="Simulate high temperature"
          >
            ≡ƒîí∩╕Å Test: Heat Stress
          </button>
          <button
            onClick={() => triggerScenario('optimal')}
            style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '600'
            }}
            title="Simulate optimal conditions"
          >
            Γ£à Test: Optimal
          </button>
          <button
            onClick={() => triggerScenario('multiple_issues')}
            style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '600'
            }}
            title="Simulate multiple critical issues"
          >
            ≡ƒöÑ Test: Emergency
          </button>
        </div>
      </div>
      
      {/* Sensor Readings */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">≡ƒÆº Soil Moisture</h3>
            <span className={`status-badge ${getSoilMoistureStatus(sensorData?.soil_moisture)}`}>
              {getSoilMoistureStatus(sensorData?.soil_moisture)}
            </span>
          </div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-label">Current Level</div>
              <div className="metric-value">
                {sensorData?.soil_moisture?.toFixed(1) || 0}
                <span className="metric-unit">%</span>
              </div>
            </div>
            <p style={{ marginTop: '1rem', color: '#6b7280' }}>
              {sensorData?.soil_moisture < 40 ? 'ΓÜá∩╕Å Irrigation recommended' : 'Γ£à Moisture adequate'}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">≡ƒîí∩╕Å Temperature</h3>
          </div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-label">Air Temperature</div>
              <div className="metric-value">
                {sensorData?.air_temperature?.toFixed(1) || 0}
                <span className="metric-unit">┬░C</span>
              </div>
            </div>
            <div className="metric" style={{ marginTop: '1rem' }}>
              <div className="metric-label">Soil Temperature</div>
              <div className="metric-value" style={{ fontSize: '1.25rem' }}>
                {sensorData?.soil_temperature?.toFixed(1) || 0}
                <span className="metric-unit">┬░C</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">≡ƒº¬ Soil pH</h3>
            <span className={`status-badge ${getPhStatus(sensorData?.soil_ph)}`}>
              {getPhStatus(sensorData?.soil_ph)}
            </span>
          </div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-label">pH Level</div>
              <div className="metric-value">
                {sensorData?.soil_ph?.toFixed(1) || 0}
              </div>
            </div>
            <p style={{ marginTop: '1rem', color: '#6b7280' }}>
              {sensorData?.soil_ph >= 6.0 && sensorData?.soil_ph <= 7.5 
                ? 'Γ£à Optimal range' 
                : 'ΓÜá∩╕Å Adjustment needed'}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">≡ƒî▒ NPK Levels</h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: '600' }}>Nitrogen (N):</span>
              <span>{sensorData?.npk_nitrogen?.toFixed(0) || 0} mg/kg</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: '600' }}>Phosphorus (P):</span>
              <span>{sensorData?.npk_phosphorus?.toFixed(0) || 0} mg/kg</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: '600' }}>Potassium (K):</span>
              <span>{sensorData?.npk_potassium?.toFixed(0) || 0} mg/kg</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mistral Multi-Agent Orchestration Card */}
      <div className="card" style={{ marginTop: '1.5rem', border: '2px solid #8b5cf6', boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.1)' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(to right, #f3e8ff, #ffffff)' }}>
          <h3 className="card-title" style={{ color: '#6d28d9', margin: 0 }}>≡ƒºá Mistral Multi-Agent Orchestrator</h3>
          <button 
            onClick={handleRunAgents} 
            disabled={isRunningAgents}
            style={{
              padding: '0.6rem 1.2rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunningAgents ? 'wait' : 'pointer',
              fontWeight: 'bold',
              opacity: isRunningAgents ? 0.7 : 1,
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(109, 40, 217, 0.3)'
            }}
          >
            {isRunningAgents ? 'ΓÅ│ Initializing Mistral...' : '≡ƒÜÇ Run Agent Context Bus'}
          </button>
        </div>
        <div className="card-content">
          {dashboardData?.recommendations && dashboardData.recommendations.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {dashboardData.recommendations.map((rec, index) => (
                <div key={index} style={{
                  padding: '1.2rem',
                  background: '#faf5ff',
                  borderLeft: '4px solid #8b5cf6',
                  borderRadius: '0 8px 8px 0',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace',
                  fontSize: '0.95rem',
                  color: '#4c1d95',
                  lineHeight: '1.5',
                  boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
                }}>
                  {rec.recommendation_text}
                  <div style={{ marginTop: '0.8rem', fontSize: '0.75rem', color: '#7c3aed', fontStyle: 'italic', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Generated by: {rec.agent_name}</span>
                    <span>{new Date(rec.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
             <div style={{ textAlign: 'center', padding: '3rem 2rem', color: '#8b5cf6', background: '#faf5ff', borderRadius: '8px', border: '1px dashed #c4b5fd' }}>
               <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>≡ƒñû</div>
               <strong style={{ fontSize: '1.1rem', display: 'block' }}>Awaiting Orchestration</strong>
               <p style={{ marginTop: '0.5rem', opacity: 0.8 }}>Click the button above to execute the multi-agent system and resolve logical conflicts via Mistral LLM.</p>
             </div>
          )}
        </div>
      </div>

      {/* Real-Time AI Recommendations */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="card-title">≡ƒñû Real-Time AI Recommendations</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {lastUpdate && (
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                Updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            <span style={{ 
              fontSize: '0.65rem', 
              padding: '0.25rem 0.5rem', 
              background: '#10b981', 
              color: 'white', 
              borderRadius: '12px',
              fontWeight: '600',
              animation: 'pulse 2s infinite'
            }}>
              LIVE
            </span>
          </div>
        </div>
        <div className="card-content">
          {realtimeRecs && realtimeRecs.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {realtimeRecs.map((rec, index) => (
                <div 
                  key={index} 
                  style={{
                    padding: '1rem',
                    background: rec.priority === 'critical' ? '#fee2e2' : 
                               rec.priority === 'high' ? '#fef3c7' : 
                               rec.priority === 'medium' ? '#dbeafe' : '#f0fdf4',
                    borderLeft: `4px solid ${rec.priority === 'critical' ? '#ef4444' : 
                                            rec.priority === 'high' ? '#f59e0b' : 
                                            rec.priority === 'medium' ? '#3b82f6' : '#10b981'}`,
                    borderRadius: '8px',
                    animation: 'slideIn 0.5s ease-out'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <strong style={{ 
                      fontSize: '1rem',
                      color: rec.priority === 'critical' ? '#991b1b' : 
                             rec.priority === 'high' ? '#92400e' : 
                             rec.priority === 'medium' ? '#1e40af' : '#166534'
                    }}>
                      {rec.title}
                    </strong>
                    <span style={{
                      fontSize: '0.7rem',
                      padding: '0.2rem 0.5rem',
                      background: rec.priority === 'critical' ? '#dc2626' : 
                                 rec.priority === 'high' ? '#f59e0b' : 
                                 rec.priority === 'medium' ? '#3b82f6' : '#10b981',
                      color: 'white',
                      borderRadius: '12px',
                      fontWeight: '600',
                      textTransform: 'uppercase'
                    }}>
                      {rec.priority}
                    </span>
                  </div>
                  <p style={{ 
                    margin: '0.5rem 0',
                    color: '#374151',
                    fontSize: '0.95rem'
                  }}>
                    {rec.message}
                  </p>
                  <div style={{
                    marginTop: '0.75rem',
                    padding: '0.5rem',
                    background: 'white',
                    borderRadius: '6px',
                    fontSize: '0.9rem'
                  }}>
                    <strong>≡ƒÆí Action:</strong> {rec.action}
                  </div>
                  <div style={{ 
                    fontSize: '0.75rem', 
                    color: '#6b7280', 
                    marginTop: '0.5rem',
                    fontStyle: 'italic'
                  }}>
                    {rec.agent}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '2rem',
              color: '#10b981'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>Γ£à</div>
              <strong style={{ fontSize: '1.1rem', display: 'block', marginBottom: '0.5rem' }}>
                All Systems Optimal!
              </strong>
              <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                No immediate actions required. Monitoring continues automatically.
              </p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes slideIn {
          from { transform: translateX(-10px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>

      {/* Green Token Wallet */}
      <div className="token-wallet" style={{ marginTop: '1.5rem' }}>
        <h3>≡ƒîƒ Green Token Wallet</h3>
        <div className="token-balance">
          {dashboardData?.blockchain?.total_tokens_issued || 0}
        </div>
        <p>Total Tokens Earned</p>
        <p style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.5rem' }}>
          Earn tokens for sustainable farming practices!
        </p>
      </div>
    </div>
  );
}

function getSoilMoistureStatus(moisture) {
  if (!moisture) return 'unknown';
  if (moisture >= 50) return 'excellent';
  if (moisture >= 40) return 'good';
  if (moisture >= 30) return 'fair';
  return 'critical';
}

function getPhStatus(ph) {
  if (!ph) return 'unknown';
  if (ph >= 6.0 && ph <= 7.5) return 'good';
  if ((ph >= 5.5 && ph < 6.0) || (ph > 7.5 && ph <= 8.0)) return 'fair';
  return 'critical';
}

export default Dashboard;
