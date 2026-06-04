import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FarmAnalytics.css';

function FarmAnalytics({ apiUrl, farmId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${apiUrl}/farm_analytics`, {
          params: { farm_id: farmId }
        });
        setData(response.data);
      } catch (err) {
        setError("Failed to load analytics: " + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [apiUrl, farmId]);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Action Autopilot Analytics... ⏳</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;
  if (!data || !data.health_score) return <div style={{ padding: '2rem' }}>No analytics data available.</div>;

  const { health_score, yield_prediction, cost_optimization, anomalies, crop_rotation, benchmarking } = data;

  // Determine gradient based on health score
  let statusClass = 'health-status-optimal';
  if (health_score.score < 50) statusClass = 'health-status-poor';
  else if (health_score.score <= 75) statusClass = 'health-status-average';

  return (
    <div className="analytics-container">
      {/* Dynamic Health Banner */}
      <div className={`health-banner ${statusClass}`}>
        <div className="health-score">
          <p>Comprehensive Health Score</p>
          <h2>{health_score.score}<span>/100</span></h2>
          <p>Grade: {health_score.grade} ({health_score.trend})</p>
        </div>
        <div className="health-factors">
          <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Key Drivers:</p>
          <ul>
            {health_score.factors.map((factor, idx) => (
              <li key={idx}>• {factor}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Grid for other features */}
      <div className="analytics-grid">
        
        {/* Yield Prediction */}
        <div className="glass-card">
          <h4>🌾 Predictive Yield Trend</h4>
          <p className="metric-value">{yield_prediction.predicted_yield_kg.toLocaleString()} {yield_prediction.unit}</p>
          <p className="metric-subtext">Confidence: {yield_prediction.confidence_percentage}%</p>
          <p className="metric-subtext" style={{ marginTop: '0.5rem' }}>Margin of Error: ±{yield_prediction.margin_of_error_kg.toLocaleString()} {yield_prediction.unit}</p>
        </div>

        {/* Cost Optimization */}
        <div className="glass-card">
          <h4>💰 Cost Analysis</h4>
          <p className="metric-value">₹{cost_optimization.estimated_current_cost_inr.toLocaleString()}</p>
          <p className="metric-subtext" style={{ marginBottom: '1rem' }}>Estimated total input cost</p>
          
          {cost_optimization.optimization_suggestions.map((sug, idx) => (
            <div key={idx} className="cost-saving-item">
              <strong>{sug.strategy} (Save ~{sug.savings_pct.toFixed(0)}%)</strong>
              <p>{sug.message}</p>
            </div>
          ))}
        </div>

        {/* Anomaly Detection */}
        <div className="glass-card">
          <h4>🚨 "Guard-Dog" Anomalies</h4>
          {anomalies.length > 0 ? (
            anomalies.map((anom, idx) => (
              <div key={idx} className="anomaly-alert">
                <p>{anom.message}</p>
              </div>
            ))
          ) : (
            <div style={{ color: '#059669', fontWeight: '500', padding: '1rem 0' }}>
              ✅ No critical anomalies detected. All sensors normal.
            </div>
          )}
        </div>

        {/* AI Crop Rotation Strategy */}
        <div className="glass-card">
          <h4>🌱 AI Crop Rotation Planner</h4>
          <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '1rem' }}>
            <h5 style={{ margin: '0 0 0.5rem 0', color: '#1e40af' }}>Next Recommended Crop:</h5>
            <p className="metric-value" style={{ fontSize: '1.5rem', color: '#1d4ed8' }}>{crop_rotation.suggested_next_crop}</p>
            <p className="metric-subtext" style={{ color: '#3b82f6', marginTop: '0.5rem' }}>{crop_rotation.reasoning}</p>
          </div>
        </div>

        {/* Regional Benchmarking */}
        <div className="glass-card" style={{ gridColumn: 'span 2' }}>
          <h4>🗺️ Regional Benchmarking</h4>
          <p style={{ fontSize: '1.1rem', color: '#374151' }}>{benchmarking}</p>
        </div>

      </div>
    </div>
  );
}

export default FarmAnalytics;
