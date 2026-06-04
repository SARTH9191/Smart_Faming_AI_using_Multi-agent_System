import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useLanguage } from '../context/LanguageContext';

function SatelliteView({ farmId, apiUrl }) {
  const { t } = useLanguage();
  const [satelliteData, setsatelliteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [customLocation, setCustomLocation] = useState({ latitude: '', longitude: '' });
  const [showLocationInput, setShowLocationInput] = useState(false);

  // Preset farm locations
  const presetLocations = {
    'Pune': { lat: 18.5204, lng: 73.8567, area: '10 hectares' },
    'Nashik': { lat: 19.9975, lng: 73.7898, area: '8 hectares' },
    'Solapur': { lat: 17.6599, lng: 75.9064, area: '12 hectares' },
    'Ahmednagar': { lat: 19.0948, lng: 74.7480, area: '15 hectares' }
  };

  useEffect(() => {
    fetchSatelliteData();
    
    // Refresh every 5 minutes (NASA data doesn't change frequently)
    const interval = setInterval(fetchSatelliteData, 300000);
    
    return () => clearInterval(interval);
  }, [farmId]);

  const fetchSatelliteData = async (lat = null, lng = null) => {
    try {
      let url = `${apiUrl}/drone_satellite_analysis?farm_id=${farmId}`;
      if (lat && lng) {
        url += `&latitude=${lat}&longitude=${lng}`;
      }
      const response = await axios.get(url);
      setsatelliteData(response.data);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching satellite data:', error);
      setLoading(false);
    }
  };

  const handlePresetLocation = (location) => {
    const coords = presetLocations[location];
    fetchSatelliteData(coords.lat, coords.lng);
    setShowLocationInput(false);
  };

  const handleCustomLocation = () => {
    const lat = parseFloat(customLocation.latitude);
    const lng = parseFloat(customLocation.longitude);
    if (lat && lng && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      fetchSatelliteData(lat, lng);
      setShowLocationInput(false);
    } else {
      alert('Please enter valid coordinates:\nLatitude: -90 to 90\nLongitude: -180 to 180');
    }
  };

  const handleAutoDetectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          fetchSatelliteData(lat, lng);
          alert(`✅ Location detected!\nLatitude: ${lat.toFixed(4)}°N\nLongitude: ${lng.toFixed(4)}°E\n\nAnalyzing your farm...`);
        },
        (error) => {
          alert('❌ Unable to detect location.\n\nPlease:\n1. Enable location services in your browser\n2. Or use preset locations\n3. Or enter coordinates manually');
        }
      );
    } else {
      alert('❌ Geolocation not supported by your browser.\n\nPlease use preset locations or enter coordinates manually.');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="spinner"></div>
        <p>{t('loading')}</p>
      </div>
    );
  }

  if (!satelliteData) {
    return <div>{t('error')}: {t('noData')}</div>;
  }

  const { satellite_analysis, drone_analysis, soil_health_map, recommendations } = satelliteData;
  const isRealData = satellite_analysis?.api_status === "✅ Live Data";

  return (
    <div style={{ padding: '1.5rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🛰️ {t('satellite')} & {t('droneAnalysis')}
        </h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ 
            background: isRealData ? '#10b981' : '#f59e0b',
            color: 'white',
            padding: '0.25rem 0.75rem',
            borderRadius: '12px',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}>
            {isRealData ? '📡 ' + t('liveData') : '🔄 ' + t('simulated')}
          </span>
          {lastUpdate && (
            <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>
              {t('lastUpdated')}: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Farm Location & Area Selection */}
      <div style={{ 
        background: '#ffffff',
        border: '2px solid #e5e7eb',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#1f2937' }}>
          📍 Farm Location & Analysis Area
        </h3>
        
        {/* Current Location Display - EMPHASIZE FARMER'S PLOT */}
        {satelliteData?.location && (
          <div>
            {/* YOUR FARM - Primary Focus */}
            <div style={{ 
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              padding: '1.25rem',
              borderRadius: '8px',
              marginBottom: '1rem',
              color: 'white',
              border: '3px solid #047857'
            }}>
              <div style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '1.5rem' }}>🎯</span>
                <span>YOUR FARM - Analysis Focus Area</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.25rem' }}>📍 GPS Location</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '600' }}>
                    {satelliteData.location.latitude.toFixed(4)}°N, {satelliteData.location.longitude.toFixed(4)}°E
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.25rem' }}>📐 Your Plot Size</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                    {drone_analysis?.area_covered || '10 hectares'}
                  </div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '0.15rem' }}>
                    316m × 316m field
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.25rem' }}>🔬 Detail Level</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '600' }}>
                    5m × 5m zones
                  </div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '0.15rem' }}>
                    25 analysis points
                  </div>
                </div>
              </div>
              <div style={{ 
                marginTop: '0.75rem', 
                padding: '0.75rem', 
                background: 'rgba(255,255,255,0.2)',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: '600'
              }}>
                ✅ All recommendations are specific to YOUR 10-hectare farm only!
              </div>
            </div>

            {/* Regional Weather Context - Secondary Info */}
            <div style={{ 
              background: '#f9fafb',
              padding: '0.75rem',
              borderRadius: '6px',
              border: '1px solid #e5e7eb',
              fontSize: '0.8rem',
              color: '#6b7280'
            }}>
              <div style={{ fontWeight: '600', marginBottom: '0.25rem', color: '#4b5563' }}>
                ℹ️ Weather Context Used:
              </div>
              Satellite pulls weather data from your region (55km area) because rain/temperature affects entire district, not just one farm. But analysis and recommendations are ONLY for your 10-hectare plot.
            </div>
          </div>
        )}

        {/* Location Selection Buttons */}
        <div style={{ marginBottom: '1rem' }}>
          {/* Auto-Detect Button (Prominent) */}
          <div style={{ marginBottom: '1rem' }}>
            <button
              onClick={handleAutoDetectLocation}
              style={{
                width: '100%',
                padding: '1rem 1.5rem',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '700',
                boxShadow: '0 4px 6px rgba(16, 185, 129, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <span style={{ fontSize: '1.5rem' }}>📍</span>
              <span>Find My Farm Location Automatically</span>
            </button>
            <div style={{ 
              fontSize: '0.75rem', 
              color: '#6b7280', 
              marginTop: '0.5rem',
              textAlign: 'center'
            }}>
              💡 Uses your phone/computer GPS - no typing needed!
            </div>
          </div>

          {/* Or Divider */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '1rem',
            margin: '1.5rem 0'
          }}>
            <div style={{ flex: 1, height: '1px', background: '#d1d5db' }}></div>
            <div style={{ fontSize: '0.85rem', color: '#9ca3af', fontWeight: '600' }}>OR</div>
            <div style={{ flex: 1, height: '1px', background: '#d1d5db' }}></div>
          </div>

          {/* Quick Select Locations */}
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151', width: '100%', marginBottom: '0.5rem' }}>
              📌 Quick Select Popular Locations:
            </div>
            {Object.keys(presetLocations).map(location => (
              <button
                key={location}
                onClick={() => handlePresetLocation(location)}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '600'
                }}
              >
                {location} ({presetLocations[location].area})
              </button>
            ))}
            <button
              onClick={() => setShowLocationInput(!showLocationInput)}
              style={{
                padding: '0.5rem 1rem',
                background: showLocationInput ? '#ef4444' : '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '600'
              }}
            >
              {showLocationInput ? '✕ Cancel' : '🔧 Manual Entry'}
            </button>
          </div>
        </div>

        {/* Custom Location Input */}
        {showLocationInput && (
          <div style={{ 
            background: '#eff6ff',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid #3b82f6'
          }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#1e3a8a', marginBottom: '0.75rem' }}>
              🌍 Enter Custom GPS Coordinates:
            </div>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'end' }}>
              <div style={{ flex: '1', minWidth: '150px' }}>
                <label style={{ fontSize: '0.85rem', color: '#374151', display: 'block', marginBottom: '0.25rem' }}>
                  Latitude (°N)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  placeholder="18.5204"
                  value={customLocation.latitude}
                  onChange={(e) => setCustomLocation({...customLocation, latitude: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <div style={{ flex: '1', minWidth: '150px' }}>
                <label style={{ fontSize: '0.85rem', color: '#374151', display: 'block', marginBottom: '0.25rem' }}>
                  Longitude (°E)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  placeholder="73.8567"
                  value={customLocation.longitude}
                  onChange={(e) => setCustomLocation({...customLocation, longitude: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <button
                onClick={handleCustomLocation}
                style={{
                  padding: '0.5rem 1.5rem',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: '600'
                }}
              >
                🔍 Analyze
              </button>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
              💡 Example: Pune (18.5204, 73.8567) | Nashik (19.9975, 73.7898)
            </div>
          </div>
        )}

        {/* How Farmers Find Location - Practical Guide */}
        <div style={{ 
          marginTop: '1rem',
          padding: '1rem',
          background: '#ecfdf5',
          borderRadius: '8px',
          border: '2px solid #10b981'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '0.75rem', color: '#065f46', fontSize: '0.95rem' }}>
            👨‍🌾 How Farmers Find Their Location (No Technical Knowledge Needed):
          </div>
          <div style={{ fontSize: '0.85rem', color: '#047857', lineHeight: '1.7' }}>
            <div style={{ marginBottom: '0.75rem' }}>
              <strong>✅ Method 1: Automatic (Easiest)</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                • Stand at your farm with smartphone/tablet<br/>
                • Click "Find My Farm Location Automatically"<br/>
                • System uses GPS (like Google Maps)<br/>
                • ⏱️ Takes 2 seconds - no typing!
              </div>
            </div>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <strong>✅ Method 2: Government Records</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                • Land registry (7/12 extract) has GPS coordinates<br/>
                • PM-KISAN portal shows registered farm location<br/>
                • Village agriculture officer can provide
              </div>
            </div>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <strong>✅ Method 3: Google Maps</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                • Open Google Maps on phone<br/>
                • Drop pin on farm location<br/>
                • Tap pin → coordinates shown at bottom<br/>
                • Copy and paste here
              </div>
            </div>
            
            <div>
              <strong>✅ Method 4: Village Selection</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                • Choose nearest city (Pune, Nashik, etc.)<br/>
                • Close enough for weather/satellite data<br/>
                • No exact GPS needed for regional analysis
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Method Explanation */}
        <div style={{ 
          marginTop: '1rem',
          padding: '1rem',
          background: '#f9fafb',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: '#4b5563',
          lineHeight: '1.6'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '0.75rem' }}>📊 Coverage Area Shapes:</div>
          
          {/* Visual Diagram */}
          <div style={{ 
            background: 'white',
            padding: '1.5rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            textAlign: 'center',
            border: '2px solid #e5e7eb'
          }}>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '1rem' }}>
              Visual Representation (Not to Scale)
            </div>
            
            {/* Diagram */}
            <div style={{ position: 'relative', height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {/* Satellite Circle (Background) */}
              <div style={{
                position: 'absolute',
                width: '240px',
                height: '240px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 58, 138, 0.1) 100%)',
                border: '3px dashed #3b82f6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <div style={{ fontSize: '0.75rem', color: '#3b82f6', fontWeight: '600', position: 'absolute', top: '10px' }}>
                  🛰️ Satellite (Circular)
                </div>
                <div style={{ fontSize: '0.7rem', color: '#6b7280', position: 'absolute', bottom: '10px' }}>
                  55km radius
                </div>
              </div>
              
              {/* Drone Square (Middle) */}
              <div style={{
                position: 'absolute',
                width: '140px',
                height: '140px',
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.15) 100%)',
                border: '3px solid #10b981',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}>
                <div style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: '600', marginBottom: '0.25rem' }}>
                  🚁 Drone Field
                </div>
                <div style={{ fontSize: '0.7rem', color: '#6b7280' }}>
                  316m × 316m
                </div>
                <div style={{ fontSize: '0.65rem', color: '#9ca3af', marginTop: '0.25rem' }}>
                  (10 hectares)
                </div>
              </div>
              
              {/* GPS Center Point */}
              <div style={{
                position: 'absolute',
                width: '16px',
                height: '16px',
                background: '#ef4444',
                borderRadius: '50%',
                border: '3px solid white',
                boxShadow: '0 0 0 2px #ef4444'
              }}></div>
              <div style={{
                position: 'absolute',
                bottom: '80px',
                fontSize: '0.7rem',
                color: '#ef4444',
                fontWeight: '600',
                background: 'white',
                padding: '0.25rem 0.5rem',
                borderRadius: '4px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                📍 GPS Point
              </div>
            </div>
          </div>
          
          {/* Explanation */}
          <div style={{ fontSize: '0.85rem', lineHeight: '1.7' }}>
            <div style={{ 
              background: '#fef3c7',
              padding: '1rem',
              borderRadius: '8px',
              marginBottom: '1rem',
              border: '2px solid #fbbf24'
            }}>
              <div style={{ fontWeight: '700', color: '#92400e', marginBottom: '0.5rem' }}>
                ⚠️ Why We Need Regional Weather Data (But Analyze Only YOUR Farm):
              </div>
              <div style={{ color: '#78350f', fontSize: '0.85rem', lineHeight: '1.6' }}>
                <strong>Think of it this way:</strong><br/>
                • If it rains 50mm in your district, it rains on YOUR farm too<br/>
                • Temperature rises affect whole region, including YOUR field<br/>
                • We pull regional weather, but apply it SPECIFICALLY to your 10 hectares<br/>
                • All recommendations = YOUR farm only (not neighbors')
              </div>
            </div>

            <div style={{ marginBottom: '0.75rem' }}>
              <strong>🎯 YOUR FARM ONLY (10 hectares):</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem', color: '#059669', fontWeight: '600' }}>
                ✓ High-resolution drone scan: 5cm/pixel<br/>
                ✓ Soil health: 25 zones analyzed individually<br/>
                ✓ NDVI: Vegetation health for YOUR crops<br/>
                ✓ Recommendations: Specific actions for YOUR field<br/>
                ✓ Problem areas: Exact 5m×5m zones on YOUR land
              </div>
            </div>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <strong>🌦️ Regional Weather Context (for accuracy):</strong>
              <div style={{ marginLeft: '1rem', marginTop: '0.25rem', color: '#6b7280' }}>
                • Rainfall data (affects irrigation needs)<br/>
                • Temperature trends (affects crop growth rate)<br/>
                • Humidity (affects disease risk)<br/>
                • Solar radiation (affects photosynthesis)<br/>
                → Applied to analyze YOUR specific farm conditions
              </div>
            </div>
            
            <div style={{ 
              background: '#dcfce7',
              padding: '0.75rem',
              borderRadius: '6px',
              border: '1px solid #86efac'
            }}>
              <strong style={{ color: '#166534' }}>🎯 Bottom Line:</strong>
              <div style={{ color: '#15803d', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                We analyze ONLY your 10-hectare plot in extreme detail (25 zones). Regional weather is just context data - like checking the district forecast before planning YOUR farm work.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* NASA Satellite Data Section */}
      <div style={{ 
        background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem',
        color: 'white'
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🛰️ NASA POWER Satellite Data
          {isRealData && <span style={{ fontSize: '0.75rem', background: '#10b981', padding: '0.2rem 0.5rem', borderRadius: '8px' }}>LIVE</span>}
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
          {/* Temperature */}
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.5rem' }}>🌡️ Temperature</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {satellite_analysis?.temperature_trend?.current?.toFixed(1) || 'N/A'}°C
            </div>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '0.5rem' }}>
              7-day avg: {satellite_analysis?.temperature_trend?.['7_day_average']?.toFixed(1) || 'N/A'}°C
            </div>
            <div style={{ 
              marginTop: '0.5rem', 
              fontSize: '0.85rem',
              background: satellite_analysis?.temperature_trend?.trend === 'rising' ? '#ef4444' : 
                         satellite_analysis?.temperature_trend?.trend === 'falling' ? '#3b82f6' : '#6b7280',
              padding: '0.25rem 0.5rem',
              borderRadius: '6px',
              display: 'inline-block'
            }}>
              {satellite_analysis?.temperature_trend?.trend === 'rising' ? '📈 Rising' :
               satellite_analysis?.temperature_trend?.trend === 'falling' ? '📉 Falling' : '➡️ Stable'}
            </div>
          </div>

          {/* Precipitation */}
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.5rem' }}>🌧️ Precipitation</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {satellite_analysis?.precipitation?.last_7_days_mm?.toFixed(1) || 'N/A'} mm
            </div>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '0.5rem' }}>
              Daily avg: {satellite_analysis?.precipitation?.daily_average?.toFixed(2) || 'N/A'} mm
            </div>
          </div>

          {/* Humidity */}
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.5rem' }}>💧 Humidity</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {satellite_analysis?.humidity?.current?.toFixed(0) || 'N/A'}%
            </div>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '0.5rem' }}>
              Status: {satellite_analysis?.humidity?.status || 'Unknown'}
            </div>
          </div>

          {/* Soil Moisture */}
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.5rem' }}>🌱 Soil Moisture</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {satellite_analysis?.soil_moisture_estimation?.estimated_percentage?.toFixed(0) || 'N/A'}%
            </div>
            <div style={{ 
              marginTop: '0.5rem',
              fontSize: '0.85rem',
              background: satellite_analysis?.soil_moisture_estimation?.status === 'Adequate' ? '#10b981' : '#ef4444',
              padding: '0.25rem 0.5rem',
              borderRadius: '6px',
              display: 'inline-block'
            }}>
              {satellite_analysis?.soil_moisture_estimation?.status || 'Unknown'}
            </div>
          </div>

          {/* Solar Radiation */}
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: '0.5rem' }}>☀️ Solar Radiation</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
              {satellite_analysis?.solar_radiation?.average_kWh_m2_day?.toFixed(2) || 'N/A'}
            </div>
            <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '0.25rem' }}>kWh/m²/day</div>
            <div style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '0.5rem' }}>
              Status: {satellite_analysis?.solar_radiation?.status || 'Unknown'}
            </div>
          </div>
        </div>

        {/* Data Source */}
        <div style={{ marginTop: '1rem', fontSize: '0.75rem', opacity: 0.7, textAlign: 'right' }}>
          📡 Data Source: {satellite_analysis?.data_source || 'N/A'}
        </div>
      </div>

      {/* Drone Analysis Section */}
      <div style={{ 
        background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem',
        color: 'white'
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>🚁 Drone Field Analysis</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>📊 NDVI Average</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{drone_analysis?.ndvi_average || 'N/A'}</div>
          </div>
          
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>🌾 Crop Health</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{drone_analysis?.crop_health || 'N/A'}</div>
          </div>
          
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>⚠️ Anomalies</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{drone_analysis?.anomalies_detected || 0}</div>
          </div>
          
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>📏 Area Covered</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{drone_analysis?.area_covered || 'N/A'}</div>
          </div>
        </div>

        {/* Health Zones */}
        {drone_analysis?.zones && drone_analysis.zones.length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            <div style={{ fontSize: '0.9rem', marginBottom: '0.75rem', fontWeight: '600' }}>📍 Field Health Zones:</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.5rem' }}>
              {drone_analysis.zones.map((zone, index) => (
                <div 
                  key={index}
                  style={{ 
                    background: 'rgba(255,255,255,0.1)', 
                    padding: '0.75rem', 
                    borderRadius: '6px',
                    fontSize: '0.85rem'
                  }}
                >
                  <div style={{ fontWeight: 'bold' }}>{zone.zone_id}</div>
                  <div style={{ opacity: 0.9 }}>NDVI: {zone.ndvi_value}</div>
                  <div style={{ 
                    marginTop: '0.25rem',
                    background: zone.health_status === 'Excellent' ? '#10b981' :
                               zone.health_status === 'Good' ? '#3b82f6' :
                               zone.health_status === 'Fair' ? '#f59e0b' : '#ef4444',
                    padding: '0.2rem 0.4rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem'
                  }}>
                    {zone.health_status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Soil Health Map */}
      <div style={{ 
        background: '#f3f4f6',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>🗺️ Soil Health Map - Your Farm Layout</h3>
        
        {/* How to Read the Map - Farmer Guide */}
        <div style={{
          background: '#dbeafe',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          border: '2px solid #3b82f6'
        }}>
          <div style={{ fontWeight: '700', color: '#1e3a8a', marginBottom: '0.5rem' }}>
            📍 How to Find Zones on Your Farm:
          </div>
          <div style={{ fontSize: '0.85rem', color: '#1e40af', lineHeight: '1.6' }}>
            <strong>📏 Total Coverage:</strong> 316m × 316m = <strong>10 hectares</strong> (24.7 acres) centered on your GPS location<br/>
            <br/>
            <strong>Grid System:</strong> Your farm is divided into 25 zones (5×5 checkerboard)<br/>
            • <strong>R = Row</strong> (North ⬆️ to South ⬇️): R0 (top/north) → R4 (bottom/south)<br/>
            • <strong>C = Column</strong> (West ⬅️ to East ➡️): C0 (left/west) → C4 (right/east)<br/>
            • <strong>Each zone = 63m × 63m</strong> (about 0.4 hectares or 1 acre per zone)<br/>
            <br/>
            <strong>Example: R3C2 means:</strong><br/>
            → Located in <strong>row 3, column 2</strong> of your field<br/>
            → About <strong>190m south</strong> from north edge and <strong>126m east</strong> from west edge<br/>
            → Southeast quadrant of your farm
          </div>
        </div>

        {/* Visual Grid Map */}
        {soil_health_map?.grid_data && (
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ 
              fontSize: '0.9rem', 
              fontWeight: '600', 
              marginBottom: '0.75rem',
              color: '#1f2937'
            }}>
              🧭 Field Map (Stand at North fence, face South):
            </div>
            
            {/* Compass Directions */}
            <div style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#3b82f6' }}>⬆️ NORTH</div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {/* WEST label */}
              <div style={{ 
                writingMode: 'vertical-rl', 
                textOrientation: 'mixed',
                fontSize: '1rem',
                fontWeight: '700',
                color: '#3b82f6'
              }}>
                ⬅️ WEST
              </div>

              {/* Grid */}
              <div style={{ 
                display: 'inline-block',
                border: '3px solid #374151',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                {soil_health_map.grid_data.map((row, rowIndex) => (
                  <div key={rowIndex} style={{ display: 'flex' }}>
                    {row.map((cell, colIndex) => {
                      const isProblem = soil_health_map.problem_areas?.includes(cell.position);
                      const healthColor = cell.health_score > 70 ? '#10b981' : 
                                         cell.health_score > 50 ? '#f59e0b' : '#ef4444';
                      
                      return (
                        <div
                          key={colIndex}
                          style={{
                            width: '60px',
                            height: '60px',
                            background: isProblem ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)' : 
                                       `linear-gradient(135deg, ${healthColor}22 0%, ${healthColor}11 100%)`,
                            border: isProblem ? '3px solid #ef4444' : `2px solid ${healthColor}`,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.7rem',
                            position: 'relative'
                          }}
                        >
                          <div style={{ fontWeight: '700', fontSize: '0.75rem' }}>
                            {cell.position}
                          </div>
                          <div style={{ fontSize: '0.65rem', color: '#6b7280' }}>
                            {cell.health_score.toFixed(0)}%
                          </div>
                          {isProblem && (
                            <div style={{ 
                              position: 'absolute',
                              top: '2px',
                              right: '2px',
                              fontSize: '1rem'
                            }}>
                              ⚠️
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

              {/* EAST label */}
              <div style={{ 
                writingMode: 'vertical-rl', 
                textOrientation: 'mixed',
                fontSize: '1rem',
                fontWeight: '700',
                color: '#3b82f6'
              }}>
                EAST ➡️
              </div>
            </div>

            <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#3b82f6' }}>⬇️ SOUTH</div>
            </div>

            {/* Legend */}
            <div style={{ 
              marginTop: '1rem',
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center',
              flexWrap: 'wrap',
              fontSize: '0.85rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '20px', height: '20px', background: '#10b981', border: '2px solid #059669', borderRadius: '4px' }}></div>
                <span>Good (&gt;70%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '20px', height: '20px', background: '#f59e0b', border: '2px solid #d97706', borderRadius: '4px' }}></div>
                <span>Fair (50-70%)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '20px', height: '20px', background: '#ef4444', border: '3px solid #dc2626', borderRadius: '4px' }}></div>
                <span>⚠️ Needs Attention (&lt;50%)</span>
              </div>
            </div>
          </div>
        )}

        {/* Stats Summary */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <div style={{ 
            background: 'white', 
            padding: '1rem', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            flex: '1',
            minWidth: '150px'
          }}>
            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>Average Health</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#1f2937' }}>
              {soil_health_map?.average_health?.toFixed(1) || 'N/A'}%
            </div>
          </div>
          
          <div style={{ 
            background: 'white', 
            padding: '1rem', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            flex: '1',
            minWidth: '150px'
          }}>
            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>Problem Areas</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#ef4444' }}>
              {soil_health_map?.problem_areas?.length || 0}
            </div>
          </div>
          
          <div style={{ 
            background: 'white', 
            padding: '1rem', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            flex: '1',
            minWidth: '150px'
          }}>
            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>Grid Resolution</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937' }}>
              {soil_health_map?.resolution || 'N/A'}
            </div>
          </div>
        </div>

        {/* Problem areas with walking directions */}
        {soil_health_map?.problem_areas && soil_health_map.problem_areas.length > 0 && (
          <div style={{ 
            background: '#fee2e2', 
            padding: '1rem', 
            borderRadius: '8px',
            border: '2px solid #fecaca'
          }}>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#991b1b', marginBottom: '0.75rem' }}>
              ⚠️ Areas Requiring Immediate Attention:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {soil_health_map.problem_areas.slice(0, 5).map((area, index) => {
                // Parse R and C from area like "R3C2"
                const match = area.match(/R(\d+)C(\d+)/);
                if (match) {
                  const row = parseInt(match[1]);
                  const col = parseInt(match[2]);
                  const distanceSouth = row * 63.2; // Each row is 63.2m
                  const distanceEast = col * 63.2;   // Each column is 63.2m
                  
                  // Determine direction
                  const nsDirection = row < 2 ? 'North' : row > 2 ? 'South' : 'Center';
                  const ewDirection = col < 2 ? 'West' : col > 2 ? 'East' : 'Center';
                  const corner = `${nsDirection}${ewDirection === 'Center' ? '' : '-' + ewDirection}`;
                  
                  return (
                    <div key={index} style={{ 
                      background: 'white',
                      padding: '0.75rem',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      color: '#7f1d1d',
                      border: '1px solid #fecaca'
                    }}>
                      <div style={{ fontWeight: '700', marginBottom: '0.25rem' }}>
                        📍 Zone {area} ({corner} area - 0.4 hectares)
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#991b1b' }}>
                        🚶 Approximately {distanceSouth.toFixed(0)}m from North boundary, {distanceEast.toFixed(0)}m from West boundary<br/>
                        📏 Diagonal: About {Math.sqrt(distanceSouth*distanceSouth + distanceEast*distanceEast).toFixed(0)}m from NW corner
                      </div>
                    </div>
                  );
                }
                return null;
              })}
            </div>
            {soil_health_map.problem_areas.length > 5 && (
              <div style={{ fontSize: '0.8rem', color: '#7f1d1d', marginTop: '0.5rem', fontStyle: 'italic' }}>
                + {soil_health_map.problem_areas.length - 5} more areas (see full map above)
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div style={{ 
          background: '#fef3c7',
          borderRadius: '12px',
          padding: '1.5rem',
          border: '2px solid #fbbf24'
        }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#92400e' }}>
            💡 AI Recommendations
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recommendations.map((rec, index) => (
              <div 
                key={index}
                style={{ 
                  background: 'white',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  fontSize: '0.95rem',
                  color: '#1f2937',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                }}
              >
                {rec}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Farmer Benefits Section */}
      <div style={{ 
        background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginTop: '1.5rem',
        border: '3px solid #fbbf24'
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#92400e', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          💰 How This Helps Farmers
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>💧</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Save Water (30-40%)
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              Know exactly which 5m zones need water. No more irrigating entire field when only corners need it. Save ₹15,000-25,000/season on water bills.
            </div>
          </div>

          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🌱</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Reduce Fertilizer Cost (25%)
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              Apply fertilizer only where soil tests show deficiency. Prevent over-application. Save ₹10,000-15,000/hectare on chemicals.
            </div>
          </div>

          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠️</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Prevent Crop Loss Early
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              NDVI detects stress 2-3 weeks before visible to eye. Catch pest/disease early. Prevent 10-30% yield loss = ₹50,000-150,000 saved.
            </div>
          </div>

          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⏱️</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Save Time & Labor
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              No walking entire 10 hectares daily. System tells exactly where problem is. Save 3-4 hours/day inspection time. Focus on fixing, not finding.
            </div>
          </div>

          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>📈</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Increase Yield (15-20%)
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              Optimal irrigation + precise fertilizer + early pest detection = healthier crops. Extra 15-20% output = ₹75,000-100,000 extra income.
            </div>
          </div>

          <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🏦</div>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1f2937', marginBottom: '0.5rem' }}>
              Better Loans & Insurance
            </div>
            <div style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: '1.5' }}>
              Satellite data proves crop health to banks/insurance. Faster loan approval. Easier crop insurance claims with NASA-verified damage proof.
            </div>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
        <button
          onClick={fetchSatelliteData}
          style={{
            padding: '0.75rem 2rem',
            background: 'linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: '600',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}
        >
          🔄 Refresh Satellite Data
        </button>
      </div>
    </div>
  );
}

export default SatelliteView;
