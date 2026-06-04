import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import './CropsManager.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ============================================================
// DISEASE SCANNER SUB-COMPONENT
// ============================================================
function DiseaseScanner() {
  const [selectedCrop, setSelectedCrop] = useState('wheat');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const CROP_TYPES = [
    { value: 'wheat', label: '🌾 Wheat' },
    { value: 'rice', label: '🍚 Rice' },
    { value: 'cotton', label: '☁️ Cotton' },
    { value: 'tomato', label: '🍅 Tomato' },
    { value: 'corn', label: '🌽 Corn' },
    { value: 'potato', label: '🥔 Potato' },
    { value: 'sugarcane', label: '🎋 Sugarcane' },
    { value: 'soybean', label: '🫘 Soybean' },
    { value: 'onion', label: '🧅 Onion' },
  ];

  const ANALYSIS_STEPS = [
    '🔍 Extracting image color features...',
    '🧠 Running ML disease classifier...',
    '📊 Calculating severity score...',
    '📅 Predicting spread timeline...',
    '💊 Generating treatment plan...',
  ];

  const handleFileSelect = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload a valid image file (JPG, PNG, WEBP).');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Image too large. Please use an image under 10MB.');
      return;
    }
    setError(null);
    setResult(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
      setImageBase64(reader.result); // already data URL with prefix
    };
    reader.readAsDataURL(file);
  }, []);

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleAnalyze = async () => {
    if (!imageBase64) {
      setError('Please upload a crop photo first.');
      return;
    }
    setAnalyzing(true);
    setResult(null);
    setError(null);
    setAnalysisStep(0);

    // Step-by-step animation
    for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
      await new Promise(r => setTimeout(r, 600));
      setAnalysisStep(i + 1);
    }

    try {
      const response = await axios.post(`${API_URL}/detect_disease_image`, {
        image_base64: imageBase64,
        crop_type: selectedCrop,
      });
      const payload = response.data || {};

      // Normalize/guard for backend error payloads
      if (payload.error) {
        setError(`❌ ${payload.error}`);
        setResult(null);
      } else if (payload.message && !payload.disease_detected && !payload.display_name) {
        setError(`❌ ${payload.message}`);
        setResult(null);
      } else {
        const parsedConfidence = Number(payload.confidence);
        const safeConfidence = Number.isFinite(parsedConfidence)
          ? Math.max(0, Math.min(100, parsedConfidence))
          : 0;

        const normalized = {
          ...payload,
          disease_detected: Boolean(payload.disease_detected),
          display_name: payload.display_name || payload.disease_name || 'Healthy Crop',
          disease_name: payload.disease_name || (payload.disease_detected ? 'unknown' : 'healthy'),
          confidence: safeConfidence,
          severity: (payload.severity || (payload.disease_detected ? 'mild' : 'none')).toLowerCase(),
          recommendations: Array.isArray(payload.recommendations) ? payload.recommendations : [],
          treatment: Array.isArray(payload.treatment) ? payload.treatment : [],
          organic_treatment: Array.isArray(payload.organic_treatment) ? payload.organic_treatment : [],
          prevention: Array.isArray(payload.prevention) ? payload.prevention : [],
          spread_prediction: payload.spread_prediction || { risk: 'none', timeline: [] },
          treatment_effectiveness: payload.treatment_effectiveness || {},
        };

        setResult(normalized);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Analysis failed.';
      setError(`❌ ${msg}`);
    } finally {
      setAnalyzing(false);
      setAnalysisStep(0);
    }
  };

  const clearImage = () => {
    setPreviewUrl(null);
    setImageBase64(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // ---- Confidence Ring ----
  const ConfidenceRing = ({ confidence, diseased }) => {
    const r = 36;
    const circ = 2 * Math.PI * r;
    const parsed = Number(confidence);
    const pct = Number.isFinite(parsed) ? Math.min(100, Math.max(0, parsed)) : 0;
    const offset = circ - (pct / 100) * circ;
    const color = diseased ? (pct > 80 ? '#ef4444' : pct > 60 ? '#f59e0b' : '#3b82f6') : '#10b981';
    return (
      <div className="confidence-ring-wrap">
        <svg viewBox="0 0 90 90">
          <circle className="ring-bg" cx="45" cy="45" r={r} />
          <circle
            className="ring-fill"
            cx="45" cy="45" r={r}
            stroke={color}
            strokeDasharray={circ}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="confidence-center">
          <span className="conf-pct">{pct}%</span>
          <span className="conf-label">conf</span>
        </div>
      </div>
    );
  };

  // ---- Spread Timeline Chart ----
  const SpreadTimeline = ({ spreadData }) => {
    if (!spreadData || spreadData.risk === 'none' || !spreadData.timeline?.length) {
      return (
        <div style={{ textAlign: 'center', padding: '20px', color: '#10b981', fontSize: '14px' }}>
          ✅ No spread risk detected
        </div>
      );
    }

    const { timeline, risk, days_to_critical, without_treatment_loss_pct } = spreadData;
    const maxPct = 100;

    const barColor = (level) => {
      const colors = { low: '#10b981', medium: '#3b82f6', high: '#f59e0b', critical: '#ef4444' };
      return colors[level] || '#6b7280';
    };

    return (
      <div className="spread-timeline">
        <div className="spread-risk-header">
          <span className={`spread-risk-badge ${risk}`}>
            {risk === 'critical' ? '🚨' : risk === 'high' ? '⚠️' : '📊'} {risk.toUpperCase()} RISK
          </span>
          {days_to_critical < 14 && (
            <span className="spread-days-warning">
              Critical in {days_to_critical} days
            </span>
          )}
        </div>
        <div className="timeline-chart">
          {timeline.map((t, i) => (
            <div
              key={i}
              className="timeline-bar"
              style={{
                height: `${(t.affected_area_pct / maxPct) * 100}%`,
                background: barColor(t.risk_level),
                opacity: 0.7 + (i / timeline.length) * 0.3,
              }}
            >
              <span className="bar-tooltip">{t.date}: {t.affected_area_pct}%</span>
            </div>
          ))}
        </div>
        <div className="timeline-labels">
          <span>Day 1</span>
          <span>Day 7</span>
          <span>Day 14</span>
        </div>
        {without_treatment_loss_pct > 0 && (
          <div className="spread-summary">
            <p>Without treatment:</p>
            <strong>{without_treatment_loss_pct}% crop affected in 14 days</strong>
          </div>
        )}
      </div>
    );
  };

  // ---- Results Panel ----
  const ResultsPanel = ({ data }) => {
    const isHealthy = !data.disease_detected;
    const eff = data.treatment_effectiveness || {};
    const spread = data.spread_prediction || {};

    const cardClass = isHealthy ? 'healthy' : data.severity === 'severe' ? 'diseased' : 'warning';
    const severityIcon = { severe: '🚨', moderate: '⚠️', mild: 'ℹ️', none: '✅' };

    return (
      <div className="scan-results">
        {/* Header summary card */}
        <div className={`results-header-card ${cardClass}`}>
          <ConfidenceRing confidence={data.confidence} diseased={data.disease_detected} />
          <div className="results-summary">
            <div className="disease-name-display">
              <span>{data.emoji}</span>
              <span>{data.display_name}</span>
            </div>
            <div className={`severity-badge ${data.severity || 'none'}`}>
              {severityIcon[data.severity] || '✅'} {(data.severity || 'none').toUpperCase()} SEVERITY
            </div>
            <div className="result-quick-recs">
              {(data.recommendations || []).slice(0, 3).map((r, i) => (
                <p key={i}>{r}</p>
              ))}
            </div>
          </div>
        </div>

        {isHealthy ? (
          <div className="result-card">
            <div className="healthy-result">
              <span className="healthy-icon">🌿</span>
              <h3>Your Crop is Healthy!</h3>
              <p>AI analysis found no signs of disease. Keep monitoring regularly.</p>
              <div className="prevention-list">
                {(data.prevention || []).map((p, i) => (
                  <div key={i} className="prevention-item">{p}</div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="results-grid">
            {/* Chemical Treatment */}
            {data.treatment?.length > 0 && (
              <div className="result-card">
                <div className="result-card-title">
                  <span>💊</span> Chemical Treatment
                </div>
                <div className="treatment-list">
                  {data.treatment.map((t, i) => (
                    <div key={i} className="treatment-item chemical">
                      <span className="step-num">{i + 1}</span>
                      <span>{t}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Organic Treatment */}
            {data.organic_treatment?.length > 0 && (
              <div className="result-card">
                <div className="result-card-title">
                  <span>🌿</span> Organic Alternative
                </div>
                <div className="treatment-list">
                  {data.organic_treatment.map((t, i) => (
                    <div key={i} className="treatment-item organic">
                      <span className="step-num">{i + 1}</span>
                      <span>{t}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Treatment Effectiveness */}
            {Object.keys(eff).length > 0 && (
              <div className="result-card">
                <div className="result-card-title">
                  <span>📈</span> Treatment Effectiveness
                </div>
                <div className="effectiveness-bars">
                  {[
                    { key: 'chemical_treatment', label: 'Chemical Treatment', cls: 'chemical' },
                    { key: 'organic_treatment', label: 'Organic Treatment', cls: 'organic' },
                    { key: 'combined_approach', label: 'Combined Approach ⭐', cls: 'combined' },
                  ].map(({ key, label, cls }) => eff[key] ? (
                    <div key={key} className="eff-row">
                      <div className="eff-label-row">
                        <span className="eff-label">{label}</span>
                        <span className="eff-pct">{eff[key]}%</span>
                      </div>
                      <div className="eff-bar-track">
                        <div className={`eff-bar-fill ${cls}`} style={{ width: `${eff[key]}%` }} />
                      </div>
                    </div>
                  ) : null)}
                  {eff.estimated_yield_saved_pct && (
                    <p style={{ fontSize: '12px', color: '#6ee7b7', margin: '8px 0 0', fontWeight: 600 }}>
                      💰 Save ~{eff.estimated_yield_saved_pct}% of yield with prompt treatment
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Disease Spread Timeline */}
            <div className="result-card">
              <div className="result-card-title">
                <span>📅</span> 14-Day Spread Prediction
              </div>
              <SpreadTimeline spreadData={spread} />
            </div>

            {/* Prevention */}
            {data.prevention?.length > 0 && (
              <div className="result-card">
                <div className="result-card-title">
                  <span>🛡️</span> Prevention
                </div>
                <div className="prevention-list">
                  {data.prevention.map((p, i) => (
                    <div key={i} className="prevention-item">{p}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Alternative Diagnosis */}
            {data.alternative_diagnosis && (
              <div className="result-card">
                <div className="result-card-title">
                  <span>🔎</span> Alternative Diagnosis
                </div>
                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px' }}>
                  <p style={{ color: '#cbd5e1', fontWeight: 700, margin: '0 0 4px' }}>
                    {data.alternative_diagnosis.display_name}
                  </p>
                  <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>
                    Confidence: {data.alternative_diagnosis.confidence}% — Consider if treatment is ineffective
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="disease-scanner-section">
      {/* Header */}
      <div className="scanner-header">
        <div className="scanner-header-left">
          <div className="scanner-icon-wrap">🔬</div>
          <div>
            <h3>AI Crop Disease Scanner</h3>
            <p>Upload a photo → instant disease detection, severity & treatment plan</p>
          </div>
        </div>
        <div className="scanner-badge">AI POWERED</div>
      </div>

      {/* Controls: Upload + Crop Selector */}
      <div className="scanner-controls">
        {/* Upload area */}
        {!previewUrl ? (
          <div
            className={`upload-area${dragOver ? ' drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleInputChange}
            />
            <div className="upload-placeholder">
              <span className="upload-big-icon">📷</span>
              <h4>Click or Drag & Drop</h4>
              <p>Take a photo or upload from gallery</p>
              <div className="upload-formats">
                <span>📸 Camera</span>
                <span>JPG</span>
                <span>PNG</span>
                <span>WEBP</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="image-preview-container">
            <img src={previewUrl} alt="Crop preview" />
            <div className="image-preview-overlay">
              <div className="image-preview-actions">
                <button className="btn-clear-image" onClick={clearImage}>🗑️ Remove</button>
                {result && (
                  <button className="btn-analyze-again" onClick={() => { setResult(null); setError(null); }}>
                    🔄 Re-scan
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Right panel */}
        <div className="scanner-right-panel">
          <div className="crop-selector">
            <label>SELECT CROP TYPE</label>
            <select value={selectedCrop} onChange={e => setSelectedCrop(e.target.value)}>
              {CROP_TYPES.map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <button
            className="scan-button"
            onClick={handleAnalyze}
            disabled={analyzing || !imageBase64}
          >
            {analyzing ? (
              <>⏳ Analyzing...</>
            ) : (
              <>🔬 Scan for Diseases</>
            )}
          </button>

          <div className="scan-tips">
            <p>📸 Photo Tips</p>
            <ul>
              <li>Focus on affected leaves / stems</li>
              <li>Use natural daylight for best results</li>
              <li>Include visible symptoms in frame</li>
              <li>Avoid blurry or dark images</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Loader with step progress */}
      {analyzing && (
        <div className="analyzing-loader">
          <div className="loader-circle" />
          <div className="loader-text">
            <h4>AI Analysis in Progress</h4>
            <p>Running Random Forest ML model on image features</p>
          </div>
          <div className="analyzing-steps">
            {ANALYSIS_STEPS.map((step, i) => (
              <div
                key={i}
                className={`step-item ${i < analysisStep - 1 ? 'done' : i === analysisStep - 1 ? 'active' : ''}`}
              >
                <span>{i < analysisStep - 1 ? '✓' : i === analysisStep - 1 ? '⚡' : '○'}</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '16px',
          padding: '14px 20px',
          background: 'rgba(239,68,68,0.12)',
          border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '12px',
          color: '#fca5a5',
          fontSize: '14px',
        }}>
          {error}
        </div>
      )}

      {/* Results */}
      {result && !analyzing && <ResultsPanel data={result} />}
    </div>
  );
}

// ============================================================
// MAIN CROPS MANAGER COMPONENT
// ============================================================
function CropsManager({ farmId, apiUrl }) {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  const effectiveApiUrl = apiUrl || API_URL;
  const effectiveFarmId = farmId || 'FARM001';

  const [newCrop, setNewCrop] = useState({
    crop_type: '',
    planted_date: '',
    expected_harvest_date: '',
    area_hectares: '',
    status: 'growing',
    latitude: '',
    longitude: ''
  });

  useEffect(() => {
    fetchCrops();
    const interval = setInterval(fetchCrops, 30000);
    return () => clearInterval(interval);
  }, [filterStatus, effectiveFarmId]);

  const fetchCrops = async () => {
    try {
      const timestamp = new Date().getTime();
      const statusParam = filterStatus !== 'all' ? `&status=${filterStatus}` : '';
      const response = await axios.get(
        `${effectiveApiUrl}/crops?farm_id=${effectiveFarmId}${statusParam}&_t=${timestamp}`,
        { headers: { 'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache' } }
      );
      setCrops(response.data.crops || []);
    } catch (error) {
      console.error('Error fetching crops:', error);
    }
  };

  const addCrop = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const lat = newCrop.latitude || (18.5 + Math.random() * 0.1).toFixed(4);
      const lon = newCrop.longitude || (73.8 + Math.random() * 0.1).toFixed(4);

      await axios.post(`${effectiveApiUrl}/crops`, {
        farm_id: effectiveFarmId,
        ...newCrop,
        area_hectares: parseFloat(newCrop.area_hectares),
        latitude: parseFloat(lat),
        longitude: parseFloat(lon)
      });
      alert('✅ Crop added successfully!');
      setShowAddForm(false);
      setNewCrop({ 
        crop_type: '', 
        planted_date: '', 
        expected_harvest_date: '', 
        area_hectares: '', 
        status: 'growing',
        latitude: '',
        longitude: ''
      });
      fetchCrops();
    } catch (error) {
      alert('❌ Error adding crop. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateCropStatus = async (cropId, newStatus) => {
    try {
      await axios.put(`${effectiveApiUrl}/crops/${cropId}/status?status=${newStatus}`);
      alert(`✅ Crop status updated to ${newStatus}!`);
      fetchCrops();
    } catch (error) {
      alert('❌ Error updating crop status.');
    }
  };

  const deleteCrop = async (cropId) => {
    if (window.confirm('Are you sure you want to delete this crop?')) {
      try {
        await axios.delete(`${effectiveApiUrl}/crops/${cropId}`);
        alert('✅ Crop deleted successfully!');
        fetchCrops();
      } catch (error) {
        alert('❌ Error deleting crop.');
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = { growing: '#10b981', ready: '#f59e0b', harvested: '#6366f1', failed: '#ef4444' };
    return colors[status] || '#6b7280';
  };

  const getStatusIcon = (status) => {
    const icons = { growing: '🌱', ready: '✅', harvested: '🚜', failed: '❌' };
    return icons[status] || '📦';
  };

  const getCropIcon = (cropType) => {
    const icons = { wheat: '🌾', rice: '🍚', corn: '🌽', tomatoes: '🍅', tomato: '🍅', potatoes: '🥔', onions: '🧅', carrots: '🥕', sugarcane: '🎋', cotton: '☁️', soybeans: '🫘', soybean: '🫘' };
    return icons[cropType?.toLowerCase()] || '🌿';
  };

  const calculateTotalArea = () => crops.reduce((sum, crop) => sum + (crop.area_hectares || 0), 0).toFixed(2);
  const getCropsByStatus = (status) => crops.filter(crop => crop.status === status).length;

  const cropTypes = ['wheat', 'rice', 'corn', 'tomatoes', 'potatoes', 'onions', 'carrots', 'sugarcane', 'cotton', 'soybeans'];

  return (
    <div className="crops-manager">
      {/* -------- DISEASE SCANNER (always visible at top) -------- */}
      <DiseaseScanner />

      {/* -------- CROPS MANAGEMENT -------- */}
      <div className="crops-header">
        <div className="header-title">
          <h2>🌾 Crops Management</h2>
          <p>Track your crops from planting to harvest</p>
        </div>
        <div className="header-actions">
          <button className="btn-refresh" onClick={fetchCrops} title="Refresh data">🔄 Refresh</button>
          <button className="btn-add" onClick={() => setShowAddForm(!showAddForm)}>
            {showAddForm ? '❌ Cancel' : '➕ Add Crop'}
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="crops-stats">
        {[
          { icon: '🌾', value: crops.length, label: 'Total Crops' },
          { icon: '🌱', value: getCropsByStatus('growing'), label: 'Growing' },
          { icon: '✅', value: getCropsByStatus('ready'), label: 'Ready' },
          { icon: '🚜', value: getCropsByStatus('harvested'), label: 'Harvested' },
          { icon: '📏', value: calculateTotalArea(), label: 'Total Hectares' },
        ].map((stat, i) => (
          <div key={i} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-info">
              <h3>{stat.value}</h3>
              <p>{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Add Crop Form */}
      {showAddForm && (
        <div className="add-crop-form">
          <h3>➕ Add New Crop</h3>
          <form onSubmit={addCrop}>
            <div className="form-row">
              <div className="form-group">
                <label>Crop Type</label>
                <select value={newCrop.crop_type} onChange={(e) => setNewCrop({ ...newCrop, crop_type: e.target.value })} required>
                  <option value="">Select crop type</option>
                  {cropTypes.map(type => (
                    <option key={type} value={type}>{getCropIcon(type)} {type.charAt(0).toUpperCase() + type.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Area (Hectares)</label>
                <input type="number" step="0.1" min="0.1" value={newCrop.area_hectares} onChange={(e) => setNewCrop({ ...newCrop, area_hectares: e.target.value })} placeholder="e.g., 5.5" required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Latitude</label>
                <input type="text" value={newCrop.latitude} onChange={(e) => setNewCrop({ ...newCrop, latitude: e.target.value })} placeholder="Auto-fills if empty" />
              </div>
              <div className="form-group">
                <label>Longitude</label>
                <input type="text" value={newCrop.longitude} onChange={(e) => setNewCrop({ ...newCrop, longitude: e.target.value })} placeholder="Auto-fills if empty" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Planted Date</label>
                <input type="date" value={newCrop.planted_date} onChange={(e) => setNewCrop({ ...newCrop, planted_date: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Expected Harvest Date</label>
                <input type="date" value={newCrop.expected_harvest_date} onChange={(e) => setNewCrop({ ...newCrop, expected_harvest_date: e.target.value })} required />
              </div>
            </div>
            <div className="form-group">
              <label>Initial Status</label>
              <select value={newCrop.status} onChange={(e) => setNewCrop({ ...newCrop, status: e.target.value })}>
                <option value="growing">🌱 Growing</option>
                <option value="ready">✅ Ready</option>
              </select>
            </div>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? '⏳ Adding...' : '✅ Add Crop'}
            </button>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="crops-filters">
        {[
          { status: 'all', label: '📦 All', count: crops.length },
          { status: 'growing', label: '🌱 Growing', count: getCropsByStatus('growing') },
          { status: 'ready', label: '✅ Ready', count: getCropsByStatus('ready') },
          { status: 'harvested', label: '🚜 Harvested', count: getCropsByStatus('harvested') },
        ].map(f => (
          <button key={f.status} className={filterStatus === f.status ? 'filter-btn active' : 'filter-btn'} onClick={() => setFilterStatus(f.status)}>
            {f.label} ({f.count})
          </button>
        ))}
      </div>

      {/* Crops List */}
      <div className="crops-list">
        {crops.length === 0 ? (
          <div className="empty-state">
            <h3>🌾 No Crops Found</h3>
            <p>Click "Add Crop" to start tracking your crops</p>
          </div>
        ) : (
          crops.map((crop) => (
            <div key={crop.id} className="crop-card">
              <div className="crop-header">
                <div className="crop-title">
                  <span className="crop-icon">{getCropIcon(crop.crop_type)}</span>
                  <h3>{crop.crop_type.charAt(0).toUpperCase() + crop.crop_type.slice(1)}</h3>
                </div>
                <div className="crop-status" style={{ backgroundColor: getStatusColor(crop.status) + '20', color: getStatusColor(crop.status) }}>
                  {getStatusIcon(crop.status)} {crop.status.toUpperCase()}
                </div>
              </div>
              <div className="crop-details">
                <div className="detail-item">
                  <span className="detail-label">📏 Area:</span>
                  <span className="detail-value">{crop.area_hectares} hectares</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">🌱 Planted:</span>
                  <span className="detail-value">{new Date(crop.planted_date).toLocaleDateString()}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">📅 Expected Harvest:</span>
                  <span className="detail-value">{new Date(crop.expected_harvest_date).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="crop-actions">
                {crop.status === 'growing' && (
                  <button className="btn-action btn-ready" onClick={() => updateCropStatus(crop.id, 'ready')}>✅ Mark Ready</button>
                )}
                {crop.status === 'ready' && (
                  <button className="btn-action btn-harvest" onClick={() => updateCropStatus(crop.id, 'harvested')}>🚜 Mark Harvested</button>
                )}
                <button className="btn-action btn-delete" onClick={() => deleteCrop(crop.id)}>🗑️ Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default CropsManager;
