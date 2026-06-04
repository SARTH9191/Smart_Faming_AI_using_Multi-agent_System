import React, { useState, useEffect } from 'react';
import axios from 'axios';

function WeatherView({ apiUrl }) {
  const [weatherData, setWeatherData] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [advisory, setAdvisory] = useState(null);
  const [advisoryLoading, setAdvisoryLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [location, setLocation] = useState('Pune');
  const [inputValue, setInputValue] = useState('Pune');

  useEffect(() => {
    fetchWeatherData();
  }, [location]);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setAdvisory(null);
      const searchLocation = location || 'Pune';
      const timestamp = new Date().getTime();

      const [weatherResponse, forecastResponse] = await Promise.all([
        axios.get(`${apiUrl}/get_weather?location=${searchLocation}&_t=${timestamp}`, {
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        }),
        axios.get(`${apiUrl}/get_forecast?location=${searchLocation}&hours=24&_t=${timestamp}`, {
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        }),
      ]);

      setWeatherData(weatherResponse.data);
      setForecast(forecastResponse.data);
      setLoading(false);

      // Fetch AI advisory in background (non-blocking — page loads instantly)
      fetchAdvisory(searchLocation);
    } catch (error) {
      console.error('Error fetching weather:', error);
      alert('Error fetching weather. Please check the location name and try again.');
      setLoading(false);
    }
  };

  const fetchAdvisory = async (loc) => {
    setAdvisoryLoading(true);
    try {
      const res = await axios.get(`${apiUrl}/get_weather_advisory?location=${loc}`);
      setAdvisory(res.data);
    } catch (e) {
      console.error('Advisory fetch error:', e);
    } finally {
      setAdvisoryLoading(false);
    }
  };

  const handleSearch = () => {
    if (inputValue.trim()) {
      const weatherConditions = ['rain', 'sunny', 'cloudy', 'storm', 'snow', 'fog', 'mist', 'drizzle', 'thunder', 'wind', 'hot', 'cold', 'warm', 'cool'];
      const lowerInput = inputValue.trim().toLowerCase();
      if (weatherConditions.includes(lowerInput)) {
        alert('⚠️ Please enter a city name, not a weather condition.\n\nExamples: Mumbai, Delhi, Bangalore, Pune');
        return;
      }
      if (inputValue.trim().length < 2) {
        alert('⚠️ Please enter a valid city name (at least 2 characters)');
        return;
      }
      setLocation(inputValue.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  // ── helpers ──────────────────────────────────────────────────────────
  const riskColors = { low: '#16a34a', medium: '#f59e0b', high: '#dc2626', critical: '#7c2d12', unknown: '#6b7280' };
  const riskBg    = { low: '#f0fdf4', medium: '#fffbeb', high: '#fef2f2', critical: '#fff7ed', unknown: '#f9fafb' };

  const getConditionEmoji = (cond) => {
    if (!cond) return '🌤️';
    const c = cond.toLowerCase();
    if (c.includes('rain') || c.includes('drizzle')) return '🌧️';
    if (c.includes('thunder')) return '⛈️';
    if (c.includes('cloud')) return '☁️';
    if (c.includes('fog') || c.includes('mist') || c.includes('haze')) return '🌫️';
    if (c.includes('snow')) return '❄️';
    if (c.includes('clear') || c.includes('sunny')) return '☀️';
    return '🌤️';
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div>

      {/* ── Header + Search ────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', margin: 0, marginBottom: '0.5rem' }}>🌤️ Weather &amp; Forecast</h2>
          {weatherData?.data_source && (
            <span style={{
              fontSize: '0.875rem',
              color: weatherData.data_source.includes('OpenWeather') ? '#16a34a' : '#f59e0b',
              fontWeight: '600',
              background: weatherData.data_source.includes('OpenWeather') ? '#f0fdf4' : '#fef3c7',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              border: weatherData.data_source.includes('OpenWeather') ? '1px solid #bbf7d0' : '1px solid #fde68a'
            }}>
              {weatherData.data_source.includes('OpenWeather') ? '🌐 Real-time OpenWeather API' : '⚠️ Demo Mode (Simulated)'}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', fontSize: '1.2rem' }}>📍</span>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter location (e.g., Mumbai, Delhi)"
              disabled={loading}
              style={{ padding: '0.5rem 1rem 0.5rem 2.5rem', borderRadius: '8px', border: '2px solid #e5e7eb', fontSize: '1rem', minWidth: '250px', opacity: loading ? 0.6 : 1 }}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading}
            style={{ padding: '0.5rem 1.5rem', background: loading ? '#9ca3af' : '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '1rem', fontWeight: '600', transition: 'all 0.3s ease' }}
            onMouseEnter={(e) => { if (!loading) { e.target.style.background = '#2563eb'; e.target.style.transform = 'translateY(-2px)'; } }}
            onMouseLeave={(e) => { if (!loading) { e.target.style.background = '#3b82f6'; e.target.style.transform = 'translateY(0)'; } }}
          >
            {loading ? '⏳ Loading...' : '🔍 Search'}
          </button>
        </div>
      </div>

      {/* ── Location banner ─────────────────────────────────────────────── */}
      <div style={{ marginBottom: '1rem', padding: '0.75rem 1rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '8px', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.2rem' }}>📍</span>
          <span style={{ fontSize: '1rem', fontWeight: '600' }}>{weatherData?.location || location}</span>
        </div>
        {weatherData?.coordinates && (
          <span style={{ fontSize: '0.875rem', opacity: 0.9 }}>
            {weatherData.coordinates.lat.toFixed(2)}°N, {weatherData.coordinates.lon.toFixed(2)}°E
          </span>
        )}
      </div>

      {/* ── Current weather / summary / risk (unchanged) ─────────────────── */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header"><h3 className="card-title">🌡️ Current Weather</h3></div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-label">Temperature</div>
              <div className="metric-value">{weatherData?.current?.temperature || 0}<span className="metric-unit">°C</span></div>
              {weatherData?.current?.feels_like && (
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>Feels like {weatherData.current.feels_like}°C</div>
              )}
            </div>
            <div style={{ marginTop: '1rem' }}>
              {[
                ['Humidity',       `${weatherData?.current?.humidity || 0}%`],
                ['Wind Speed',     `${weatherData?.current?.wind_speed || 0} km/h`],
                ['Wind Direction', weatherData?.current?.wind_direction || 'N/A'],
                ['Cloud Cover',    `${weatherData?.current?.cloud_cover || 0}%`],
                ['Pressure',       `${weatherData?.current?.pressure || 0} hPa`],
                ['Visibility',     `${weatherData?.current?.visibility || 0} km`],
              ].map(([label, val]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>{label}:</span><span style={{ fontWeight: '600' }}>{val}</span>
                </div>
              ))}
              <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#f3f4f6', borderRadius: '6px', textAlign: 'center', fontWeight: '600' }}>
                {weatherData?.current?.conditions || 'N/A'}
                {weatherData?.current?.description && (
                  <div style={{ fontSize: '0.875rem', fontWeight: 'normal', color: '#6b7280', marginTop: '0.25rem' }}>{weatherData.current.description}</div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h3 className="card-title">📊 Forecast Summary</h3></div>
          <div className="card-content">
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}><span>Avg Temperature:</span><span>{forecast?.summary?.avg_temperature || 0}°C</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}><span>Max Temperature:</span><span>{forecast?.summary?.max_temperature || 0}°C</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}><span>Rain Probability:</span><span>{forecast?.summary?.max_rain_probability || 0}%</span></div>
            </div>
            <div className={`status-badge ${forecast?.summary?.rain_expected ? 'status-critical' : 'status-good'}`}>
              {forecast?.summary?.rain_expected ? '🌧️ Rain Expected' : '☀️ Clear'}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h3 className="card-title">⚠️ Weather Risk</h3></div>
          <div className="card-content">
            <div className="metric">
              <div className="metric-label">Risk Level</div>
              <div className={`status-badge status-${forecast?.risk_score?.level || 'good'}`}>{forecast?.risk_score?.level?.toUpperCase() || 'LOW'}</div>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <strong>Risk Factors:</strong>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                {forecast?.risk_score?.factors?.length > 0
                  ? forecast.risk_score.factors.map((f, i) => <li key={i}>{f}</li>)
                  : <li>No significant risks</li>}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* ── Recommendations (unchanged) ─────────────────────────────────── */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header"><h3 className="card-title">💡 Recommendations</h3></div>
        <div className="card-content">
          <ul className="recommendations">
            {forecast?.recommendations?.map((rec, i) => (
              <li key={i} className="recommendation-item">{rec}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* ── Hourly forecast table (unchanged) ───────────────────────────── */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title">📅 {forecast?.data_source?.includes('OpenWeather') ? 'Real-time' : 'Simulated'} Forecast</h3>
          {forecast?.data_source && (
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Data source: {forecast.data_source}</div>
          )}
        </div>
        <div className="card-content">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Time</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Temp (°C)</th>
                  {forecast?.hourly_forecast?.[0]?.feels_like && <th style={{ padding: '0.75rem', textAlign: 'left' }}>Feels Like</th>}
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Humidity</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Rain %</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Wind</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Conditions</th>
                </tr>
              </thead>
              <tbody>
                {forecast?.hourly_forecast?.slice(0, 12).map((hour, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '0.75rem', fontWeight: '600' }}>
                      {new Date(hour.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '0.75rem' }}>{hour.temperature}°C</td>
                    {hour.feels_like && <td style={{ padding: '0.75rem', color: '#6b7280' }}>{hour.feels_like}°C</td>}
                    <td style={{ padding: '0.75rem' }}>{hour.humidity}%</td>
                    <td style={{ padding: '0.75rem', color: hour.rain_probability > 60 ? '#dc2626' : hour.rain_probability > 30 ? '#f59e0b' : '#16a34a', fontWeight: '600' }}>
                      {hour.rain_probability}%
                    </td>
                    <td style={{ padding: '0.75rem' }}>{hour.wind_speed} km/h</td>
                    <td style={{ padding: '0.75rem' }}>
                      <div>{hour.conditions}</div>
                      {hour.description && <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{hour.description}</div>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#6b7280', textAlign: 'center' }}>
            {forecast?.data_source?.includes('OpenWeather') ? '🌐 Real-time data from OpenWeather API' : '⚠️ Simulated forecast for demonstration'}
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════
          NEW: 4-Day Outlook + Groq AI Advisory
          ══════════════════════════════════════════════════════════════════ */}
      <div style={{ marginTop: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <h3 style={{ margin: 0, fontSize: '1.3rem', fontWeight: '800' }}>📆 4-Day Outlook</h3>
          <span style={{ fontSize: '0.72rem', color: '#6b7280', background: '#f3f4f6', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontWeight: '600' }}>OpenWeather API</span>
          {advisoryLoading && (
            <span style={{ fontSize: '0.78rem', color: '#3b82f6', fontStyle: 'italic' }}>⏳ Generating AI advisory…</span>
          )}
        </div>

        {/* ── Day cards ── */}
        {advisory?.daily_forecast?.length > 0 ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${Math.min(advisory.daily_forecast.length, 4)}, 1fr)`,
            gap: '1rem',
            marginBottom: '1.75rem',
          }}>
            {advisory.daily_forecast.map((day, i) => (
              <div
                key={i}
                style={{
                  background: day.rain_expected
                    ? 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)'
                    : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                  border: `1.5px solid ${day.rain_expected ? '#bfdbfe' : '#bbf7d0'}`,
                  borderRadius: '1rem',
                  padding: '1.25rem',
                  textAlign: 'center',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.06)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'default',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(0,0,0,0.12)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.06)'; }}
              >
                <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
                  {formatDate(day.date)}
                </div>
                <div style={{ fontSize: '2.6rem', marginBottom: '0.5rem', lineHeight: 1 }}>
                  {advisory.ai_advisory?.daily_advice?.[i]?.condition_emoji || getConditionEmoji(day.dominant_condition)}
                </div>
                <div style={{ fontWeight: '800', fontSize: '1.5rem', color: '#111827' }}>
                  {day.max_temp}°<span style={{ fontSize: '1rem', color: '#6b7280', fontWeight: '400' }}>/{day.min_temp}°C</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#374151', marginTop: '0.25rem' }}>{day.dominant_condition}</div>

                <div style={{ marginTop: '0.6rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{
                    fontSize: '0.7rem', padding: '0.2rem 0.55rem', borderRadius: '1rem', fontWeight: '700',
                    background: day.max_rain_prob > 50 ? '#dbeafe' : '#f3f4f6',
                    color: day.max_rain_prob > 50 ? '#1d4ed8' : '#6b7280',
                  }}>
                    💧 {day.max_rain_prob}% rain
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#6b7280' }}>💨 {day.avg_wind_speed} km/h</span>
                </div>

                {/* Per-day AI advice chip */}
                {advisory.ai_advisory?.daily_advice?.[i] && (
                  <div style={{ marginTop: '0.85rem', padding: '0.6rem 0.75rem', background: 'rgba(255,255,255,0.75)', borderRadius: '0.6rem', fontSize: '0.73rem', color: '#374151', textAlign: 'left' }}>
                    <div style={{ fontWeight: '700', color: '#1e293b', marginBottom: '0.25rem' }}>
                      🤖 {advisory.ai_advisory.daily_advice[i].key_advice}
                    </div>
                    <div style={{ color: '#16a34a' }}>✅ {advisory.ai_advisory.daily_advice[i].do}</div>
                    <div style={{ color: '#dc2626' }}>❌ {advisory.ai_advisory.daily_advice[i].avoid}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : advisoryLoading ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: '#6b7280' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
            <p>Fetching 4-day forecast…</p>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af', background: '#f9fafb', borderRadius: '1rem', marginBottom: '1.5rem', border: '1px solid #f3f4f6' }}>
            ⚠️ 4-day forecast unavailable — configure your OpenWeather API key to enable this feature
          </div>
        )}

        {/* ── AI Advisory dark panel ── */}
        {advisory?.ai_advisory && (
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '1.25rem',
            padding: '2rem',
            color: 'white',
            boxShadow: '0 10px 40px rgba(0,0,0,0.22)',
          }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.6rem' }}>🧠</span>
              <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '900' }}>AI Farming Advisory</h3>
              <span style={{ fontSize: '0.68rem', background: '#4f46e5', padding: '0.2rem 0.65rem', borderRadius: '1rem', fontWeight: '700' }}>
                Groq · llama-3.1-8b-instant
              </span>
              <span style={{
                fontSize: '0.75rem', padding: '0.2rem 0.75rem', borderRadius: '1rem', fontWeight: '700',
                background: riskBg[advisory.ai_advisory.risk_level] || '#f9fafb',
                color: riskColors[advisory.ai_advisory.risk_level] || '#6b7280',
              }}>
                Risk: {(advisory.ai_advisory.risk_level || 'unknown').toUpperCase()}
              </span>
            </div>

            {/* Overall outlook */}
            <p style={{ margin: '0 0 1.5rem', lineHeight: 1.7, color: '#e2e8f0', fontSize: '0.95rem' }}>
              {advisory.ai_advisory.overall_outlook}
            </p>

            {/* Risk reason */}
            {advisory.ai_advisory.risk_reason && (
              <div style={{ background: 'rgba(255,255,255,0.05)', borderLeft: '3px solid #6366f1', padding: '0.6rem 1rem', borderRadius: '0 0.5rem 0.5rem 0', marginBottom: '1.5rem', fontSize: '0.85rem', color: '#cbd5e1' }}>
                ℹ️ {advisory.ai_advisory.risk_reason}
              </div>
            )}

            {/* Critical alerts */}
            {advisory.ai_advisory.critical_alerts?.filter(Boolean).length > 0 && (
              <div style={{ background: 'rgba(220,38,38,0.15)', border: '1px solid rgba(220,38,38,0.4)', borderRadius: '0.75rem', padding: '0.85rem 1rem', marginBottom: '1.5rem' }}>
                <div style={{ fontWeight: '700', marginBottom: '0.5rem', color: '#fca5a5', fontSize: '0.85rem' }}>🚨 Critical Alerts</div>
                {advisory.ai_advisory.critical_alerts.filter(Boolean).map((a, i) => (
                  <div key={i} style={{ color: '#fecaca', fontSize: '0.875rem', marginBottom: '0.25rem' }}>{a}</div>
                ))}
              </div>
            )}

            {/* 3-column advisory grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {[
                { icon: '🌿', label: 'Best Farming Window',    value: advisory.ai_advisory.best_farming_window },
                { icon: '💧', label: 'Irrigation Plan',         value: advisory.ai_advisory.irrigation_recommendation },
                { icon: '🧪', label: 'Pesticide Spray Window',  value: advisory.ai_advisory.pesticide_spray_window },
              ].map((item) => (
                <div key={item.label} style={{ background: 'rgba(255,255,255,0.07)', borderRadius: '0.85rem', padding: '1.1rem' }}>
                  <div style={{ fontSize: '1.4rem', marginBottom: '0.4rem' }}>{item.icon}</div>
                  <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#94a3b8', marginBottom: '0.35rem', fontWeight: '700' }}>
                    {item.label}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.55 }}>{item.value || '—'}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '1.25rem', fontSize: '0.68rem', color: '#475569', textAlign: 'right' }}>
              Generated {advisory.generated_at ? new Date(advisory.generated_at).toLocaleString('en-IN') : '—'} · {advisory.data_source}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}

export default WeatherView;
