import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MarketView({ apiUrl }) {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [crop, setCrop] = useState('wheat');

  useEffect(() => {
    fetchMarketData();
  }, [crop]);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiUrl}/get_market_forecast?crop=${crop}`);
      setMarketData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching market data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  const predictions = marketData?.predictions || [];
  const modelPerf = marketData?.model_performance || {};

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>💰 Market Prices & AI Forecast</h2>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ 
              fontSize: '0.875rem', 
              color: '#16a34a', 
              fontWeight: '600',
              background: '#f0fdf4',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              border: '1px solid #bbf7d0'
            }}>
              🤖 {marketData?.algorithm_used || 'ML-Powered'}
            </span>
          </div>
        </div>
        <select 
          value={crop}
          onChange={(e) => setCrop(e.target.value)}
          style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '2px solid #e5e7eb', fontSize: '1rem' }}
        >
          <option value="wheat">🌾 Wheat</option>
          <option value="rice">🌾 Rice</option>
          <option value="cotton">☁️ Cotton</option>
          <option value="maize">🌽 Maize</option>
          <option value="soybean">🫘 Soybean</option>
          <option value="sugarcane">🎋 Sugarcane</option>
        </select>
      </div>

      {/* Price Overview */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">💵 Current Price</h3>
          </div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-value">
                ₹{marketData?.current_price || 0}
                <span className="metric-unit">/quintal</span>
              </div>
            </div>
            <div className={`status-badge status-${marketData?.trend === 'rising' ? 'good' : marketData?.trend === 'falling' ? 'critical' : 'fair'}`} style={{ marginTop: '1rem' }}>
              {marketData?.trend === 'rising' ? '📈 Rising' : marketData?.trend === 'falling' ? '📉 Falling' : '➡️ Stable'}
              {' '}({marketData?.trend_percentage || 0}%)
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🎯 Best Selling Window</h3>
          </div>
          <div className="card-content">
            <div style={{ marginBottom: '1rem' }}>
              <div className="metric-label">Optimal Day</div>
              <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#16a34a' }}>
                Day {marketData?.best_sell_day || 'N/A'}
              </div>
            </div>
            <div style={{ marginBottom: '0.5rem' }}>
              <strong>Expected Price:</strong>
              <span style={{ float: 'right', fontWeight: '600' }}>₹{marketData?.best_expected_price || 0}</span>
            </div>
            <div>
              <strong>Potential Gain:</strong>
              <span style={{ 
                float: 'right', 
                color: marketData?.trend_percentage >= 0 ? '#16a34a' : '#dc2626', 
                fontWeight: '600' 
              }}>
                {marketData?.trend_percentage >= 0 ? '+' : ''}{marketData?.trend_percentage || 0}%
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🎯 ML Model Performance</h3>
          </div>
          <div className="card-content">
            {Object.entries(modelPerf).map(([modelName, metrics]) => (
              <div key={modelName} style={{ marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid #f3f4f6' }}>
                <div style={{ fontWeight: '600', textTransform: 'capitalize', color: '#7c3aed' }}>{modelName.replace('_', ' ')}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '0.25rem' }}>
                  <span>MAE: <strong>₹{metrics.mae?.toFixed(0)}</strong></span>
                  <span>RMSE: <strong>₹{metrics.rmse?.toFixed(0)}</strong></span>
                  <span>R²: <strong>{metrics.r2?.toFixed(3)}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Price Forecast Table */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title">📈 30-Day ML Price Forecast</h3>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            XGBoost | Gradient Boosting | Random Forest | Ridge Ensemble
          </div>
        </div>
        <div className="card-content">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'center' }}>Day</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Date</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#7c3aed' }}>XGBoost</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#059669' }}>Gradient Boost</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#dc2626' }}>Random Forest</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', color: '#f59e0b' }}>Ridge</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', fontWeight: 'bold' }}>Ensemble</th>
                </tr>
              </thead>
              <tbody>
                {predictions.slice(0, 15).map((forecast, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '0.75rem', textAlign: 'center', fontWeight: '600' }}>{forecast.day}</td>
                    <td style={{ padding: '0.75rem' }}>{forecast.date}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>₹{forecast.xgboost?.toFixed(0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>₹{forecast.gradient_boosting?.toFixed(0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>₹{forecast.random_forest?.toFixed(0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>₹{forecast.ridge?.toFixed(0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontWeight: '700', background: '#f0fdf4' }}>₹{forecast.ensemble}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#6b7280', textAlign: 'center' }}>
            📊 Showing 15 of {predictions.length} predictions | Training Data: {marketData?.training_data_points} days
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title">💡 AI-Powered Recommendations</h3>
        </div>
        <div className="card-content">
          <ul className="recommendations">
            <li className="recommendation-item">
              {marketData?.trend === 'rising' 
                ? '📈 Prices expected to RISE. Consider HOLDING your crop for better prices.'
                : marketData?.trend === 'falling'
                ? '📉 Prices expected to FALL. Consider SELLING soon to maximize returns.'
                : '➡️ Prices are STABLE. Monitor market for optimal selling window.'}
            </li>
            <li className="recommendation-item">
              🎯 Best selling window: <strong>Day {marketData?.best_sell_day}</strong> at expected price <strong>₹{marketData?.best_expected_price}</strong>
            </li>
            <li className="recommendation-item">
              📊 ML Models used: XGBoost, Gradient Boosting, Random Forest, Ridge Regression (Ensemble)
            </li>
            <li className="recommendation-item">
              🎯 Model with best R²: {Object.entries(modelPerf).sort((a,b) => b[1].r2 - a[1].r2)[0]?.[0]?.replace('_', ' ').toUpperCase()}
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default MarketView;
