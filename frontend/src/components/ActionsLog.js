import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import exifr from 'exifr';
import './ActionsLog.css';

const ACTION_TYPES = [
  { value: 'irrigation', label: '🚿 Irrigation', tokens: 10 },
  { value: 'fertilization', label: '🌱 Fertilization', tokens: 15 },
  { value: 'eco_action', label: '🌍 Eco Action', tokens: 20 },
  { value: 'rotation', label: '🔄 Crop Rotation', tokens: 20 },
  { value: 'composting', label: '♻️ Composting', tokens: 14 },
  { value: 'rainwater', label: '💧 Rainwater Harvesting', tokens: 30 },
  { value: 'solar', label: '☀️ Solar Power', tokens: 25 },
  { value: 'organic', label: '🍃 Organic Methods', tokens: 18 },
  { value: 'planting', label: '🌾 Planting', tokens: 5 },
  { value: 'harvesting', label: '🚜 Harvesting', tokens: 5 },
];

const LEVEL_CONFIG = {
  L0_SUBMITTED: { label: 'Submitted', color: '#6b7280', icon: '📝' },
  L1_IMAGE_UPLOADED: { label: 'Image Uploaded', color: '#f59e0b', icon: '🖼️' },
  L2_GEO_VERIFIED: { label: 'Geo Verified', color: '#10b981', icon: '📍' },
  L3_ADMIN_REVIEW: { label: 'Admin Review', color: '#3b82f6', icon: '🔍' },
  L4_VIDEO_PENDING: { label: 'Video Pending', color: '#8b5cf6', icon: '📹' },
  L4_VIDEO_VERIFIED: { label: 'Video Verified', color: '#059669', icon: '✅' },
  L5_APPROVED: { label: 'Approved ✓', color: '#16a34a', icon: '🌟' },
  L5_REJECTED: { label: 'Rejected', color: '#dc2626', icon: '❌' },
  verification_failed: { label: 'Geo Failed', color: '#ef4444', icon: '📍' },
};

function getActionIcon(type) {
  const icons = {
    irrigation: '🚿', fertilization: '🌱', pesticide: '🦠', harvesting: '🚜',
    planting: '🌾', eco_action: '🌍', rotation: '🔄', composting: '♻️', rainwater: '💧', solar: '☀️', organic: '🍃'
  };
  return icons[type] || '📝';
}
function getActionColor(type) {
  const colors = {
    irrigation: '#3b82f6', fertilization: '#10b981', pesticide: '#f59e0b',
    harvesting: '#8b5cf6', planting: '#10b981', eco_action: '#059669', rotation: '#6366f1',
    composting: '#059669', rainwater: '#3b82f6', solar: '#f59e0b', organic: '#10b981'
  };
  return colors[type] || '#6b7280';
}

function GpsBadge({ exifResult, geoResult }) {
  if (!exifResult) return null;

  // Before submit: show GPS found / missing based purely on EXIF
  if (!geoResult) {
    if (exifResult.has_gps) {
      return (
        <div className="gps-badge gps-matched">
          🟢 GPS Found — {exifResult.gps_latitude?.toFixed(6)}, {exifResult.gps_longitude?.toFixed(6)}
          <span style={{ fontWeight: 400, marginLeft: '0.4rem', opacity: 0.8 }}>· Submit to verify vs your farm</span>
        </div>
      );
    }
    return <div className="gps-badge gps-missing">🟡 No GPS — {exifResult.error || 'No EXIF GPS found'}</div>;
  }

  // After submit: show server-verified result
  if (geoResult.geo_passed) {
    return (
      <div className="gps-badge gps-matched">
        🟢 GPS Matched — {geoResult.distance_meters?.toFixed(0)}m from farm center
        <span style={{ fontWeight: 400, marginLeft: '0.4rem', opacity: 0.8 }}>(radius {geoResult.allowed_radius_m?.toFixed(0)}m)</span>
      </div>
    );
  }
  if (exifResult.has_gps) {
    return (
      <div className="gps-badge gps-outofradius">
        🔴 Outside Radius — {geoResult.distance_meters?.toFixed(0) ?? '?'}m from farm
        {geoResult.allowed_radius_m ? ` (max ${geoResult.allowed_radius_m.toFixed(0)}m)` : ''}
      </div>
    );
  }
  return <div className="gps-badge gps-missing">🟡 No GPS — {exifResult.error || 'No EXIF GPS found'}</div>;
}


function VerificationBadge({ level }) {
  const cfg = LEVEL_CONFIG[level] || { label: level, color: '#6b7280', icon: '❓' };
  return (
    <span className="verification-badge" style={{ background: cfg.color + '20', color: cfg.color, borderColor: cfg.color }}>
      {cfg.icon} {cfg.label}
    </span>
  );
}

function ActionsLog({ farmId, farmer }) {
  const resolvedFarmId = farmId || (farmer?.farmer_id) || (farmer?.farmerId) || 'FARM001';
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const [actions, setActions] = useState([]);
  const [totalTokens, setTotalTokens] = useState(0);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [filterType, setFilterType] = useState('all');
  const [submitResult, setSubmitResult] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const [newAction, setNewAction] = useState({ action_type: '', action_details: '', green_tokens: 0 });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [exifResult, setExifResult] = useState(null);  // from server after upload-parse
  const [geoResult, setGeoResult] = useState(null);    // from server after submit
  const [analyzing, setAnalyzing] = useState(false);
  const [liveGps, setLiveGps] = useState(null); // { lat, lon } from browser

  const fileInputRef = useRef(null);

  useEffect(() => { fetchActions(); }, [resolvedFarmId]);

  const handleUseLiveLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setLiveGps({ lat: latitude, lon: longitude });
        // Update UI to show we have live GPS + Actual Browser Data for Time/Device
        setExifResult(prev => ({
          ...prev,
          gps_latitude: latitude,
          gps_longitude: longitude,
          has_gps: true,
          error: null,
          is_live: true,
          // Actual data fallbacks
          datetime: prev?.datetime || new Date().toLocaleString(),
          make: prev?.make || 'Web Upload',
          model: prev?.model || `(via ${window.navigator.userAgent.match(/(Chrome|Safari|Firefox|Edg)/)?.[0] || 'Browser'})`
        }));
      },
      (error) => {
        console.error("Error getting location:", error);
        alert(`Could not get location: ${error.message}. Please ensure location permissions are granted.`);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const fetchActions = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${apiUrl}/actions_log?farm_id=${resolvedFarmId}&limit=100`);
      setActions(res.data.actions || []);
      setTotalTokens(res.data.total_green_tokens || 0);
    } catch (err) {
      console.error('Error fetching actions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setUploadError('');
    setExifResult(null);
    setGeoResult(null);
    setSubmitResult(null);

    // Local preview
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);

    // ── Client-side EXIF extraction (shows lat/lon before submit) ──
    try {
      const gps = await exifr.gps(file);          // { latitude, longitude }
      const tags = await exifr.parse(file, {
        pick: ['DateTimeOriginal', 'DateTime', 'Make', 'Model'],
      });
      const rawDate = tags?.DateTimeOriginal || tags?.DateTime;
      const dateStr = rawDate instanceof Date
        ? rawDate.toLocaleString()
        : (rawDate ? String(rawDate) : null);

      const clientExif = {
        gps_latitude: gps?.latitude ?? null,
        gps_longitude: gps?.longitude ?? null,
        has_gps: !!(gps?.latitude && gps?.longitude),
        // Actual Data Fallback: use current time if meta is missing
        datetime: dateStr || new Date().toLocaleString(),
        // Actual Data Fallback: identify browser as the upload source
        make: tags?.Make ? String(tags.Make) : 'Web Upload',
        model: tags?.Model ? String(tags.Model) : `(via ${window.navigator.userAgent.match(/(Chrome|Safari|Firefox|Edg)/)?.[0] || 'Browser'})`,
        error: (!gps?.latitude) ? 'No GPS data found in this image' : null,
      };

      setExifResult(clientExif);
    } catch (err) {
      setExifResult({
        gps_latitude: null, gps_longitude: null, has_gps: false,
        datetime: null, make: null, model: null,
        error: 'Could not read EXIF data from this image',
      });
    }

    // Auto-select token value for the chosen action type
    const selectedType = ACTION_TYPES.find(t => t.value === newAction.action_type);
    if (selectedType) setNewAction(prev => ({ ...prev, green_tokens: selectedType.tokens }));
  };

  const handleActionTypeChange = (e) => {
    const val = e.target.value;
    const selectedType = ACTION_TYPES.find(t => t.value === val);
    setNewAction(prev => ({ ...prev, action_type: val, green_tokens: selectedType ? selectedType.tokens : 0 }));
  };

  const logAction = async (e) => {
    e.preventDefault();
    if (!newAction.action_type) { setUploadError('Please select an action type'); return; }
    setSubmitting(true);
    setUploadError('');
    setSubmitResult(null);
    setExifResult(null);
    setGeoResult(null);

    try {
      const formData = new FormData();
      formData.append('farm_id', resolvedFarmId);
      formData.append('action_type', newAction.action_type);
      formData.append('action_details', newAction.action_details);
      formData.append('green_tokens', String(newAction.green_tokens));
      if (imageFile) formData.append('image', imageFile);
      if (liveGps) {
        formData.append('provided_lat', String(liveGps.lat));
        formData.append('provided_lon', String(liveGps.lon));
      }

      const res = await axios.post(`${apiUrl}/actions_log/submit`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = res.data;
      setSubmitResult(data);
      if (data.exif) setExifResult(data.exif);
      setGeoResult(data);

      // Reset form
      setShowAddForm(false);
      setNewAction({ action_type: '', action_details: '', green_tokens: 0 });
      setImageFile(null);
      setImagePreview(null);
      setLiveGps(null); // Clear live state
      fetchActions();
    } catch (err) {
      console.error('Error submitting action:', err);
      setUploadError(err.response?.data?.detail || 'Error submitting action. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const deleteAction = async (actionId) => {
    if (!window.confirm('Delete this action?')) return;
    try {
      await axios.delete(`${apiUrl}/actions_log/${actionId}`);
      fetchActions();
    } catch (err) {
      alert('❌ Error deleting action.');
    }
  };

  const uniqueActionTypes = [...new Set(actions.map(a => a.action_type))];
  const filteredActions = filterType === 'all' ? actions : actions.filter(a => a.action_type === filterType);

  // Should submit be disabled? Only if image was selected but geo failed strictly
  const isSubmitDisabled = submitting || (
    imageFile && geoResult && !geoResult.geo_passed &&
    geoResult.verification_level === 'verification_failed'
  );

  return (
    <div className="actions-log">
      <div className="actions-header">
        <div className="header-title">
          <h2>📝 Actions Log</h2>
          <p>Track farming activities and earn green tokens after verification</p>
        </div>
        <div className="header-actions">
          <button className="btn-refresh" onClick={fetchActions} title="Refresh">🔄 Refresh</button>
          <button className="btn-add" onClick={() => { setShowAddForm(!showAddForm); setSubmitResult(null); setUploadError(''); }}>
            {showAddForm ? '❌ Cancel' : '➕ Log Action'}
          </button>
        </div>
      </div>

      {/* Token Summary */}
      <div className="tokens-summary">
        <div className="tokens-card">
          <div className="tokens-icon">🌟</div>
          <div className="tokens-info"><h3>{totalTokens}</h3><p>Total Green Tokens</p></div>
        </div>
        <div className="tokens-card">
          <div className="tokens-icon">📊</div>
          <div className="tokens-info"><h3>{actions.length}</h3><p>Total Actions</p></div>
        </div>
        <div className="tokens-card">
          <div className="tokens-icon">✅</div>
          <div className="tokens-info">
            <h3>{actions.filter(a => a.token_request_status === 'approved').length}</h3>
            <p>Approved</p>
          </div>
        </div>
        <div className="tokens-card">
          <div className="tokens-icon">⏳</div>
          <div className="tokens-info">
            <h3>{actions.filter(a => ['pending', 'awaiting_admin_review', 'awaiting_video_verification'].includes(a.token_request_status)).length}</h3>
            <p>Pending Review</p>
          </div>
        </div>
      </div>

      {/* Submit Result Banner */}
      {submitResult && (
        <div className={`submit-banner ${submitResult.geo_passed ? 'banner-success' : 'banner-warn'}`}>
          <strong>{submitResult.geo_passed ? '✅ Submitted for Admin Review' : '⚠️ Submitted with Verification Issue'}</strong>
          <p>{submitResult.verification_reason}</p>
          {submitResult.proof_latitude && (
            <p>📍 Photo GPS: {submitResult.proof_latitude.toFixed(6)}, {submitResult.proof_longitude.toFixed(6)}</p>
          )}
        </div>
      )}

      {/* Add Action Form */}
      {showAddForm && (
        <div className="add-action-form">
          <h3>➕ Log New Action</h3>
          <form onSubmit={logAction}>
            <div className="form-row">
              <div className="form-group">
                <label>Action Type *</label>
                <select value={newAction.action_type} onChange={handleActionTypeChange} required>
                  <option value="">Select action type</option>
                  {ACTION_TYPES.map(t => (
                    <option key={t.value} value={t.value}>{t.label} (+{t.tokens} tokens)</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Green Tokens Requested</label>
                <input
                  type="number" min="0" value={newAction.green_tokens}
                  onChange={e => setNewAction({ ...newAction, green_tokens: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Action Details *</label>
              <textarea
                value={newAction.action_details}
                onChange={e => setNewAction({ ...newAction, action_details: e.target.value })}
                placeholder="Describe what you did..."
                rows="3"
                required
              />
            </div>

            {/* Image Upload */}
            <div className="form-group">
              <label>Proof Image (with GPS EXIF) <span className="label-hint">— Required for token verification</span></label>
              <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
                {imagePreview ? (
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                ) : (
                  <div className="upload-placeholder">
                    <span>📸</span>
                    <p>Click to upload proof photo</p>
                    <small>JPEG with GPS EXIF recommended</small>
                  </div>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                style={{ display: 'none' }}
                onChange={handleImageSelect}
              />
              {imageFile && <p className="file-name">📎 {imageFile.name}</p>}
            </div>

            {/* EXIF Metadata Panel */}
            {exifResult && (
              <div className="exif-panel">
                <h4>📷 Extracted Photo Metadata</h4>
                <div className="exif-grid">
                  <div className="exif-item">
                    <span className="exif-label">Latitude</span>
                    <span className="exif-value">{exifResult.gps_latitude?.toFixed(6) ?? 'N/A'}</span>
                  </div>
                  <div className="exif-item">
                    <span className="exif-label">Longitude</span>
                    <span className="exif-value">{exifResult.gps_longitude?.toFixed(6) ?? 'N/A'}</span>
                  </div>
                  <div className="exif-item">
                    <span className="exif-label">Timestamp</span>
                    <span className="exif-value">{exifResult.datetime ?? 'N/A'}</span>
                  </div>
                  <div className="exif-item">
                    <span className="exif-label">Device</span>
                    <span className="exif-value">{([exifResult.make, exifResult.model].filter(Boolean).join(' ')) || 'N/A'}</span>
                  </div>
                </div>
                <GpsBadge exifResult={exifResult} geoResult={geoResult} />

                {!exifResult.has_gps && (
                  <button 
                    type="button" 
                    className="btn-live-gps"
                    onClick={handleUseLiveLocation}
                    style={{
                      marginTop: '1rem',
                      padding: '0.6rem 1rem',
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.6rem',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      fontWeight: '600',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      width: '100%',
                      justifyContent: 'center',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#2563eb'}
                    onMouseLeave={(e) => e.target.style.background = '#3b82f6'}
                  >
                    📍 Use My Actual Current Location
                  </button>
                )}
              </div>
            )}

            {uploadError && <div className="error-msg">❌ {uploadError}</div>}

            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? '⏳ Submitting...' : '✅ Submit Action'}
            </button>
          </form>
        </div>
      )}

      {/* Filter Buttons */}
      {uniqueActionTypes.length > 0 && (
        <div className="actions-filters">
          <button className={filterType === 'all' ? 'filter-btn active' : 'filter-btn'} onClick={() => setFilterType('all')}>
            📦 All ({actions.length})
          </button>
          {uniqueActionTypes.map(type => (
            <button key={type} className={filterType === type ? 'filter-btn active' : 'filter-btn'} onClick={() => setFilterType(type)}>
              {getActionIcon(type)} {type.charAt(0).toUpperCase() + type.slice(1)} ({actions.filter(a => a.action_type === type).length})
            </button>
          ))}
        </div>
      )}

      {/* Actions List */}
      <div className="actions-list">
        {loading ? (
          <div className="empty-state"><p>⏳ Loading actions...</p></div>
        ) : filteredActions.length === 0 ? (
          <div className="empty-state">
            <h3>📝 No Actions Found</h3>
            <p>Click "Log Action" to start tracking your farming activities</p>
          </div>
        ) : (
          filteredActions.map(action => (
            <div key={action.id} className="action-card" style={{ borderLeft: `4px solid ${getActionColor(action.action_type)}` }}>
              <div className="action-header">
                <div className="action-title">
                  <span className="action-icon" style={{ background: getActionColor(action.action_type) + '20', color: getActionColor(action.action_type) }}>
                    {getActionIcon(action.action_type)}
                  </span>
                  <div>
                    <h3>{action.action_type.charAt(0).toUpperCase() + action.action_type.slice(1).replace('_', ' ')}</h3>
                    <p className="action-time">{new Date(action.timestamp).toLocaleString()}</p>
                  </div>
                </div>
                <div className="action-right">
                  <span className="tokens-badge">+{action.green_tokens_earned} 🌟</span>
                  <VerificationBadge level={action.verification_level} />
                </div>
              </div>

              <div className="action-details">
                <p>{action.action_details}</p>
                {action.verification_reason && (
                  <p className="action-reason">💬 {action.verification_reason}</p>
                )}
              </div>

              {/* GPS info on card */}
              {action.proof_latitude && (
                <div className="action-geo">
                  📍 Photo GPS: {action.proof_latitude?.toFixed(5)}, {action.proof_longitude?.toFixed(5)}
                  {action.distance_meters != null && ` — ${action.distance_meters?.toFixed(0)}m from farm`}
                </div>
              )}

              <div className="action-footer">
                <span className="action-id">ID: {action.id}</span>
                <button className="btn-delete-action" onClick={() => deleteAction(action.id)}>🗑️ Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ActionsLog;
