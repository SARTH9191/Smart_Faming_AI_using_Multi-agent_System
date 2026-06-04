import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import './AdminPanel.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const LEVEL_CONFIG = {
  L0_SUBMITTED:        { label: 'Submitted',      color: '#64748b', icon: '📝' },
  L1_IMAGE_UPLOADED:   { label: 'Image Uploaded', color: '#f59e0b', icon: '🖼️' },
  L2_GEO_VERIFIED:     { label: 'Geo Verified',   color: '#10b981', icon: '📍' },
  L3_ADMIN_REVIEW:     { label: 'Admin Review',   color: '#3b82f6', icon: '🔍' },
  L4_VIDEO_PENDING:    { label: 'Call Scheduled', color: '#a855f7', icon: '📹' },
  L4_VIDEO_VERIFIED:   { label: 'Call Done',      color: '#059669', icon: '✅' },
  L5_APPROVED:         { label: 'Approved ✓',     color: '#10b981', icon: '🌟' },
  L5_REJECTED:         { label: 'Rejected',        color: '#f43f5e', icon: '❌' },
  verification_failed: { label: 'Geo Failed',      color: '#f43f5e', icon: '🚫' },
};

const STATUS_FILTERS = ['all', 'pending', 'geo_failed', 'video_pending', 'approved', 'rejected'];

const PROGRESS_STEPS = [
  { key: 'submitted',  label: 'Submitted',   levels: ['L0_SUBMITTED'] },
  { key: 'image',      label: 'Image',       levels: ['L1_IMAGE_UPLOADED'] },
  { key: 'geo',        label: 'Geo',         levels: ['L2_GEO_VERIFIED'] },
  { key: 'review',     label: 'Review',      levels: ['L3_ADMIN_REVIEW', 'L4_VIDEO_PENDING', 'L4_VIDEO_VERIFIED'] },
  { key: 'approved',   label: 'Approved',    levels: ['L5_APPROVED', 'L5_REJECTED', 'verification_failed'] },
];

function getProgressState(level, status) {
  const order = ['L0_SUBMITTED','L1_IMAGE_UPLOADED','L2_GEO_VERIFIED','L3_ADMIN_REVIEW',
                  'L4_VIDEO_PENDING','L4_VIDEO_VERIFIED','L5_APPROVED','L5_REJECTED','verification_failed'];
  const currentIdx = order.indexOf(level);
  const rejected = status === 'rejected' || level === 'L5_REJECTED';
  const failed = level === 'verification_failed';

  return PROGRESS_STEPS.map((step, i) => {
    const stepMaxLevel = step.levels[step.levels.length - 1];
    const stepIdx = order.indexOf(step.levels[0]);
    if (rejected && step.key === 'approved') return 'failed';
    if (failed && step.key === 'geo') return 'failed';
    if (currentIdx >= stepIdx) return 'done';
    if (i === PROGRESS_STEPS.findIndex(s => order.indexOf(s.levels[0]) > currentIdx) - 1 + 1) return 'active';
    return 'pending';
  });
}

// ── Status Badge ──────────────────────────────────────────────────
function StatusBadge({ level, status }) {
  const cfg = LEVEL_CONFIG[level] || { label: level || status, color: '#64748b', icon: '❓' };
  return (
    <span className="admin-status-badge"
      style={{ background: cfg.color + '18', color: cfg.color, borderColor: cfg.color + '45' }}>
      {cfg.icon} {cfg.label}
    </span>
  );
}

// ── Progress Tracker ──────────────────────────────────────────────
function ProgressTracker({ level, status }) {
  const states = getProgressState(level, status);
  return (
    <div className="progress-tracker">
      {PROGRESS_STEPS.map((step, i) => {
        const state = states[i] || 'pending';
        return (
          <div className={`progress-step ${state}`} key={step.key}>
            <div className="progress-dot">
              {state === 'done' ? '✓' : state === 'failed' ? '✕' : i + 1}
            </div>
            <span className="progress-label">{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}

// ── Loading Skeleton ──────────────────────────────────────────────
function QueueSkeleton() {
  return (
    <div className="queue-skeleton">
      {[1, 2, 3].map(i => (
        <div key={i} className="skeleton skeleton-card" />
      ))}
    </div>
  );
}

// ── GPS Distance Chip ─────────────────────────────────────────────
function DistanceChip({ action }) {
  if (!action.proof_latitude) {
    return <span className="distance-chip unknown">📍 No GPS data</span>;
  }
  const pass = action.geo_match_passed;
  const dist = action.distance_meters != null ? `${action.distance_meters.toFixed(0)}m` : '?';
  const radius = action.allowed_radius_meters != null ? `${action.allowed_radius_meters.toFixed(0)}m` : '?';
  return (
    <span className={`distance-chip ${pass ? 'pass' : 'fail'}`}>
      {pass ? '✅' : '❌'} {dist} / {radius} radius
    </span>
  );
}

// ── Admin Login ───────────────────────────────────────────────────
function AdminLogin({ onLogin }) {
  const [creds, setCreds] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API_BASE}/admin/login`, creds);
      if (res.data.status === 'success') {
        localStorage.setItem('admin_token', res.data.admin_token);
        localStorage.setItem('admin_user', JSON.stringify({ username: res.data.username, role: res.data.role }));
        onLogin(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-wrap">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <span className="admin-logo">🛡️</span>
          <h2>Admin Dashboard</h2>
          <p>Smart Farming Verification Portal</p>
        </div>
        <form onSubmit={handleLogin} className="admin-login-form">
          <div className="admin-form-group">
            <label>Username</label>
            <input type="text" value={creds.username} onChange={e => setCreds({ ...creds, username: e.target.value })} placeholder="admin" required />
          </div>
          <div className="admin-form-group">
            <label>Password</label>
            <input type="password" value={creds.password} onChange={e => setCreds({ ...creds, password: e.target.value })} placeholder="••••••••" required />
          </div>
          {error && <div className="admin-error">⚠️ {error}</div>}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="button" onClick={() => window.location.reload()} className="admin-login-btn" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', flex: 1 }}>
              ← Back
            </button>
            <button type="submit" className="admin-login-btn" disabled={loading} style={{ flex: 2 }}>
              {loading ? '⏳ Signing in...' : '🔐 Sign In'}
            </button>
          </div>
        </form>
        <div className="admin-register-hint">
          First time? Register via <code>POST /admin/register</code> with your <code>ADMIN_SUPER_SECRET</code>
        </div>
      </div>
    </div>
  );
}

// ── Schedule Call Modal ───────────────────────────────────────────
function ScheduleModal({ action, token, onClose, onDone }) {
  const [phone, setPhone] = useState(action.verification_phone || '');
  const [scheduledAt, setScheduledAt] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    if (!phone || phone.trim().length < 7) { setError('Enter a valid phone number'); return; }
    if (!scheduledAt) { setError('Select a date and time'); return; }
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/admin/schedule_call/${action.id}`, {
        phone: phone.trim(),
        scheduled_at: new Date(scheduledAt).toISOString(),
        notes,
      }, { headers: { 'X-Admin-Token': token } });
      onDone();
    } catch (err) {
      setError(err.response?.data?.detail || 'Schedule failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>📹 Schedule WhatsApp Verification Call</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body">
          <p className="modal-sub">
            Farm: <strong>{action.farm_id}</strong> · Action #{action.id} · {action.action_type}
          </p>
          <div className="admin-form-group">
            <label>WhatsApp Phone Number *</label>
            <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+919876543210" required />
          </div>
          <div className="admin-form-group">
            <label>Call Date &amp; Time *</label>
            <input type="datetime-local" value={scheduledAt} onChange={e => setScheduledAt(e.target.value)} required />
          </div>
          <div className="admin-form-group">
            <label>Notes (optional)</label>
            <textarea value={notes} onChange={e => setNotes(e.target.value)} rows="2" placeholder="e.g. Verify composting on north field" />
          </div>
          {error && <div className="admin-error">⚠️ {error}</div>}
          <div className="modal-actions">
            <button type="button" className="admin-btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="admin-btn-primary" disabled={loading}>
              {loading ? '⏳ Scheduling...' : '📅 Schedule Call'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Farm Profile Modal ────────────────────────────────────────────
function FarmProfileModal({ farmId, token, onClose, onDone }) {
  const [form, setForm] = useState({ farm_name: '', latitude: '', longitude: '', area_hectares: '', verification_radius_meters: 600 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(`${API_BASE}/admin/farm_profile/${farmId}`, { headers: { 'X-Admin-Token': token } })
      .then(r => setForm({ ...r.data, latitude: r.data.latitude ?? '', longitude: r.data.longitude ?? '' }))
      .catch(() => { });
  }, [farmId, token]);

  const handleSave = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const payload = {};
    if (form.farm_name) payload.farm_name = form.farm_name;
    if (form.latitude !== '') payload.latitude = parseFloat(form.latitude);
    if (form.longitude !== '') payload.longitude = parseFloat(form.longitude);
    if (form.area_hectares !== '') payload.area_hectares = parseFloat(form.area_hectares);
    payload.verification_radius_meters = parseFloat(form.verification_radius_meters) || 600;
    try {
      await axios.put(`${API_BASE}/admin/farm_profile/${farmId}`, payload, { headers: { 'X-Admin-Token': token } });
      onDone();
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>🗺️ Edit Farm Profile — {farmId}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSave} className="modal-body">
          <div className="admin-form-group">
            <label>Farm Name</label>
            <input value={form.farm_name || ''} onChange={e => setForm({ ...form, farm_name: e.target.value })} placeholder="Optional" />
          </div>
          <div className="form-row-2">
            <div className="admin-form-group">
              <label>Latitude</label>
              <input type="number" step="any" value={form.latitude} onChange={e => setForm({ ...form, latitude: e.target.value })} placeholder="e.g. 18.5204" />
            </div>
            <div className="admin-form-group">
              <label>Longitude</label>
              <input type="number" step="any" value={form.longitude} onChange={e => setForm({ ...form, longitude: e.target.value })} placeholder="e.g. 73.8567" />
            </div>
          </div>
          <div className="form-row-2">
            <div className="admin-form-group">
              <label>Area (hectares)</label>
              <input type="number" step="any" value={form.area_hectares} onChange={e => setForm({ ...form, area_hectares: e.target.value })} placeholder="e.g. 5.0" />
            </div>
            <div className="admin-form-group">
              <label>Radius (metres)</label>
              <input type="number" value={form.verification_radius_meters} onChange={e => setForm({ ...form, verification_radius_meters: e.target.value })} min="10" />
            </div>
          </div>
          {error && <div className="admin-error">⚠️ {error}</div>}
          <div className="modal-actions">
            <button type="button" className="admin-btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="admin-btn-primary" disabled={loading}>
              {loading ? '⏳ Saving...' : '💾 Save Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Queue Action Card ─────────────────────────────────────────────
function QueueCard({ action, expanded, onToggle, onApprove, onReject, onSchedule, onMarkCall, reviewNotes, onNoteChange }) {
  const cfg = LEVEL_CONFIG[action.verification_level] || { label: action.token_request_status, color: '#64748b', icon: '❓' };
  const isPending = ['pending', 'awaiting_admin_review', 'awaiting_video_verification'].includes(action.token_request_status);
  const isCallScheduled = action.video_verification_status === 'scheduled';
  const isApproved = action.token_request_status === 'approved';
  const isRejected = action.token_request_status === 'rejected';

  const typeIcons = {
    irrigation: '🚿', fertilization: '🌱', composting: '♻️', harvesting: '🚜',
    planting: '🌾', eco_action: '🌍', rotation: '🔄', rainwater: '💧', solar: '☀️', organic: '🍃'
  };

  return (
    <div className={`queue-card ${expanded ? 'expanded' : ''}`}>
      {/* Card Header Row */}
      <div className="queue-card-top" onClick={onToggle}>
        <div className="queue-card-left">
          <div className="queue-type-icon">{typeIcons[action.action_type] || '📝'}</div>
          <div className="queue-meta">
            <div className="queue-meta-top">
              <span className="queue-farm-id">{action.farm_id}</span>
              <span className="queue-action-type">{(action.action_type || 'unspecified').replace(/_/g, ' ')}</span>
              <StatusBadge level={action.verification_level} status={action.token_request_status} />
            </div>
            <div className="queue-meta-sub">
              {action.action_details ? `${action.action_details.slice(0, 60)}${action.action_details.length > 60 ? '…' : ''}` : 'No details provided'}
            </div>
          </div>
        </div>
        <div className="queue-card-right">
          <span className="queue-tokens">+{action.requested_green_tokens} 🌟</span>
          <span className="queue-date">{new Date(action.timestamp).toLocaleDateString()}</span>
          <span className={`queue-chevron ${expanded ? 'open' : ''}`}>▼</span>
        </div>
      </div>

      {/* Expanded Detail */}
      {expanded && (
        <div className="queue-detail">
          {/* Progress Tracker */}
          <div style={{ padding: '16px 20px 0' }}>
            <ProgressTracker level={action.verification_level} status={action.token_request_status} />
          </div>

          {/* 2-Column Layout */}
          <div className="queue-detail-body">
            {/* LEFT — Details & Notes */}
            <div className="detail-left">
              <div className="detail-section">
                <div className="detail-section-title">📋 Activity Details</div>
                <div className="detail-row">
                  <span className="detail-key">Details</span>
                  <span className="detail-val">{action.action_details || '—'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Reason</span>
                  <span className="detail-val">{action.verification_reason || '—'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Reviewer</span>
                  <span className="detail-val">{action.admin_reviewer || '—'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Notes</span>
                  <span className="detail-val">{action.admin_review_notes || '—'}</span>
                </div>
              </div>

              {/* EXIF */}
              {action.image_metadata && (
                <div className="detail-section">
                  <div className="detail-section-title">📷 Photo Metadata</div>
                  <div className="exif-row">
                    <div className="exif-item">
                      <span className="exif-item-label">GPS</span>
                      <span className="exif-item-val">{action.image_metadata.has_gps ? '✅ Found' : '❌ Missing'}</span>
                    </div>
                    <div className="exif-item">
                      <span className="exif-item-label">Captured</span>
                      <span className="exif-item-val">{action.image_metadata.exif_datetime || 'N/A'}</span>
                    </div>
                    <div className="exif-item">
                      <span className="exif-item-label">Device</span>
                      <span className="exif-item-val">{action.image_metadata.exif_device || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Call Info */}
              {action.video_call_scheduled_at && (
                <div className="detail-section">
                  <div className="detail-section-title">📹 Call Details</div>
                  <div className="call-badge">
                    <span>📅</span>
                    <div>
                      <strong>{new Date(action.video_call_scheduled_at).toLocaleString()}</strong>
                      {action.verification_phone && <div style={{ fontSize: '12px', opacity: 0.7 }}>📱 {action.verification_phone}</div>}
                    </div>
                  </div>
                </div>
              )}

              {/* Admin Notes */}
              <div className="detail-section">
                <div className="detail-section-title">✍️ Admin Notes</div>
                <div className="detail-notes">
                  <textarea
                    value={reviewNotes || ''}
                    onChange={e => onNoteChange(e.target.value)}
                    placeholder="Add notes before approving or rejecting…"
                    rows="3"
                  />
                </div>
              </div>
            </div>

            {/* RIGHT — GPS + Status + Actions */}
            <div className="detail-right">
              <div className="detail-section">
                <div className="detail-section-title">📍 GPS Verification</div>
                <div className="gps-info-grid">
                  <div className="gps-block">
                    <div className="gps-block-label">📷 Photo GPS</div>
                    <div className={`gps-coords ${!action.proof_latitude ? 'not-set' : ''}`}>
                      {action.proof_latitude
                        ? `${action.proof_latitude.toFixed(5)}, ${action.proof_longitude.toFixed(5)}`
                        : 'Not captured'}
                    </div>
                  </div>
                  <div className="gps-block">
                    <div className="gps-block-label">🏡 Farm GPS</div>
                    <div className={`gps-coords ${!action.farm_latitude ? 'not-set' : ''}`}>
                      {action.farm_latitude
                        ? `${action.farm_latitude.toFixed(5)}, ${action.farm_longitude.toFixed(5)}`
                        : 'Not configured'}
                    </div>
                  </div>
                </div>
                <DistanceChip action={action} />
              </div>

              <div className="detail-section">
                <div className="detail-section-title">🔖 Status Info</div>
                <div className="detail-row">
                  <span className="detail-key">Level</span>
                  <StatusBadge level={action.verification_level} status={action.token_request_status} />
                </div>
                <div className="detail-row">
                  <span className="detail-key">Tokens Req.</span>
                  <span className="detail-val" style={{ color: '#fbbf24', fontWeight: 700 }}>+{action.requested_green_tokens} 🌟</span>
                </div>
                {isApproved && (
                  <div className="detail-row">
                    <span className="detail-key">Minted</span>
                    <span className="detail-val" style={{ color: '#10b981', fontWeight: 700 }}>+{action.green_tokens_earned} 🌟</span>
                  </div>
                )}
                {action.blockchain_tx_hash && (
                  <div className="detail-row">
                    <span className="detail-key">Tx Hash</span>
                    <span className="detail-val" style={{ fontFamily: 'monospace', fontSize: '11px', color: '#a5b4fc' }}>
                      {action.blockchain_tx_hash.slice(0, 20)}…
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sticky Action Bar */}
          <div className="queue-action-bar">
            {isPending && (
              <div className="action-bar-primary">
                <button className="qbtn qbtn-approve" onClick={onApprove}>✅ Approve &amp; Mint</button>
                <button className="qbtn qbtn-reject" onClick={onReject}>✕ Reject</button>
              </div>
            )}
            {isCallScheduled && (
              <div className="action-bar-primary">
                <button className="qbtn qbtn-done" onClick={() => onMarkCall('completed')}>✅ Mark Done</button>
                <button className="qbtn qbtn-rejected" onClick={() => onMarkCall('failed')}>❌ Mark Failed</button>
              </div>
            )}
            {isApproved && (
              <div className="action-bar-result approved">
                🌟 Approved — {action.green_tokens_earned} tokens minted
              </div>
            )}
            {isRejected && (
              <div className="action-bar-result rejected">
                ❌ Rejected
              </div>
            )}

            <div className="action-bar-secondary">
              {isPending && action.verification_level !== 'L4_VIDEO_PENDING' && (
                <button className="qbtn qbtn-schedule" onClick={onSchedule}>📅 Schedule Call</button>
              )}
              {isCallScheduled && (
                <button className="qbtn qbtn-schedule" onClick={onSchedule}>🔄 Re-schedule</button>
              )}
              {action.verification_phone && (
                <>
                  <a href={`tel:${action.verification_phone}`} className="qbtn qbtn-call">📞 Voice Call</a>
                  <a
                    href={`https://wa.me/${(action.verification_phone || '').replace(/\D/g, '')}?text=Hi! Agri-AI Admin verification for your ${action.action_type || 'action'} action.`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="qbtn qbtn-whatsapp"
                  >
                    💬 WhatsApp
                  </a>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main Admin Panel ──────────────────────────────────────────────
function AdminPanel({ onLogout }) {
  const token = localStorage.getItem('admin_token');
  const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');

  const [activeTab, setActiveTab] = useState('queue');
  const [queueFilter, setQueueFilter] = useState('all');
  const [queue, setQueue] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');
  const [scheduleAction, setScheduleAction] = useState(null);
  const [farmProfileId, setFarmProfileId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [reviewNotes, setReviewNotes] = useState({});
  const [search, setSearch] = useState('');

  const headers = { 'X-Admin-Token': token };
  const showToast = msg => { setToast(msg); setTimeout(() => setToast(''), 3500); };

  const fetchQueue   = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/admin/queue?status=${queueFilter}&limit=200`, { headers });
      setQueue(res.data.actions || []);
    } catch (e) { showToast('❌ Failed to load queue'); }
    finally { setLoading(false); }
  };

  const fetchFarmers = async () => {
    try {
      const res = await axios.get(`${API_BASE}/admin/farmers`, { headers });
      setFarmers(res.data.farmers || []);
    } catch (e) { showToast('❌ Failed to load farmers'); }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/admin/stats`, { headers });
      setStats(res.data);
    } catch (e) { }
  };

  useEffect(() => { fetchQueue(); fetchStats(); }, [queueFilter]);
  useEffect(() => { if (activeTab === 'farmers') fetchFarmers(); }, [activeTab]);

  const approve = async id => {
    const notes = reviewNotes[id] || '';
    try {
      await axios.post(`${API_BASE}/admin/approve/${id}`, { reviewer: adminUser.username, notes }, { headers });
      showToast('✅ Approved & tokens minted!');
      fetchQueue(); fetchStats();
    } catch (e) { showToast('❌ ' + (e.response?.data?.detail || 'Approve failed')); }
  };

  const reject = async id => {
    const notes = reviewNotes[id] || '';
    if (!window.confirm('Reject this token request?')) return;
    try {
      await axios.post(`${API_BASE}/admin/reject/${id}`, { reviewer: adminUser.username, notes }, { headers });
      showToast('🚫 Rejected');
      fetchQueue(); fetchStats();
    } catch (e) { showToast('❌ ' + (e.response?.data?.detail || 'Reject failed')); }
  };

  const markCall = async (id, callStatus) => {
    const notes = reviewNotes[id] || '';
    try {
      await axios.post(`${API_BASE}/admin/complete_call/${id}`, { call_status: callStatus, notes }, { headers });
      showToast(callStatus === 'completed' ? '✅ Call marked completed' : '⚠️ Call marked failed');
      fetchQueue(); fetchStats();
    } catch (e) { showToast('❌ ' + (e.response?.data?.detail || 'Update failed')); }
  };

  const filterCounts = useMemo(() => {
    const counts = {};
    STATUS_FILTERS.forEach(f => {
      counts[f] = queue.filter(a => {
        if (f === 'all') return true;
        if (f === 'pending') return ['pending','awaiting_admin_review','awaiting_video_verification'].includes(a.token_request_status);
        if (f === 'geo_failed') return a.verification_status === 'geo_failed';
        if (f === 'video_pending') return a.video_verification_status === 'scheduled';
        return a.token_request_status === f;
      }).length;
    });
    return counts;
  }, [queue]);

  const filteredQueue = useMemo(() =>
    queue.filter(a => {
      if (search) {
        const q = search.toLowerCase();
        if (!(a.farm_id?.toLowerCase().includes(q) || a.action_type?.toLowerCase().includes(q) || a.action_details?.toLowerCase().includes(q))) return false;
      }
      return true;
    }),
    [queue, search]
  );

  const STAT_CARDS = stats ? [
    { label: 'Farmers',     value: stats.total_farmers,       icon: '👨‍🌾', color: '#10b981', bg: 'rgba(16,185,129,0.12)' },
    { label: 'Actions',     value: stats.total_actions,       icon: '📋', color: '#6366f1',  bg: 'rgba(99,102,241,0.12)' },
    { label: 'Pending',     value: stats.pending,             icon: '⏳', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
    { label: 'Approved',    value: stats.approved,            icon: '✅', color: '#10b981',  bg: 'rgba(16,185,129,0.12)' },
    { label: 'Rejected',    value: stats.rejected,            icon: '❌', color: '#f43f5e',  bg: 'rgba(244,63,94,0.12)' },
    { label: 'Geo Failed',  value: stats.geo_failed,          icon: '📍', color: '#f43f5e',  bg: 'rgba(244,63,94,0.12)' },
    { label: 'Tokens',      value: stats.total_tokens_minted, icon: '🌟', color: '#fbbf24',  bg: 'rgba(251,191,36,0.12)' },
  ] : [];

  const filterLabels = {
    all: '📦 All', pending: '⏳ Pending', geo_failed: '📍 Geo Failed',
    video_pending: '📹 Video', approved: '✅ Approved', rejected: '❌ Rejected'
  };

  return (
    <div className="admin-panel">
      {toast && <div className="admin-toast">{toast}</div>}

      {scheduleAction && (
        <ScheduleModal action={scheduleAction} token={token}
          onClose={() => setScheduleAction(null)}
          onDone={() => { setScheduleAction(null); fetchQueue(); showToast('📅 Call scheduled'); }} />
      )}
      {farmProfileId && (
        <FarmProfileModal farmId={farmProfileId} token={token}
          onClose={() => setFarmProfileId(null)}
          onDone={() => { setFarmProfileId(null); fetchFarmers(); showToast('✅ Farm profile updated'); }} />
      )}

      {/* Top Bar */}
      <div className="admin-topbar">
        <div className="admin-topbar-brand">
          <div className="admin-brand-logo">🛡️</div>
          <div className="admin-brand-text">
            <h1>Admin Dashboard</h1>
            <p>Verification &amp; Token Management</p>
          </div>
        </div>
        <div className="admin-topbar-right">
          <div className="admin-user-pill">
            <div className="admin-user-avatar">{(adminUser.username || 'A')[0].toUpperCase()}</div>
            <span>{adminUser.username}</span>
            <span style={{ opacity: 0.5, fontSize: 11 }}>· {adminUser.role}</span>
          </div>
          <button className="admin-logout-btn" onClick={onLogout}>🚪 Logout</button>
        </div>
      </div>

      {/* Body */}
      <div className="admin-body">
        {/* Stats */}
        {stats && (
          <div className="admin-stats-row">
            {STAT_CARDS.map(s => (
              <div className="admin-stat-card" key={s.label} style={{ '--stat-color': s.color, '--stat-bg': s.bg }}>
                <div className="stat-header">
                  <div className="stat-icon-badge">{s.icon}</div>
                </div>
                <p className="stat-value">{s.value ?? 0}</p>
                <p className="stat-label">{s.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Tab Nav */}
        <div className="admin-section-nav">
          <div className="admin-tabs">
            <button className={activeTab === 'queue' ? 'admin-tab active' : 'admin-tab'} onClick={() => setActiveTab('queue')}>
              🔍 Verification Queue
            </button>
            <button className={activeTab === 'farmers' ? 'admin-tab active' : 'admin-tab'} onClick={() => setActiveTab('farmers')}>
              👨‍🌾 Farmers
            </button>
          </div>
        </div>

        {/* Queue Tab */}
        {activeTab === 'queue' && (
          <div className="admin-tab-content">
            {/* Toolbar */}
            <div className="admin-toolbar">
              <div className="admin-search-wrap">
                <span className="admin-search-icon">🔎</span>
                <input
                  className="admin-search"
                  placeholder="Search farm ID, activity…"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <div className="queue-filters">
                {STATUS_FILTERS.map(f => (
                  <button key={f} className={queueFilter === f ? 'filter-btn active' : 'filter-btn'} onClick={() => setQueueFilter(f)}>
                    {filterLabels[f]}
                    <span className="filter-count">{filterCounts[f] ?? 0}</span>
                  </button>
                ))}
              </div>
              <button className="admin-btn-refresh" onClick={() => { fetchQueue(); fetchStats(); }}>🔄 Refresh</button>
            </div>

            {/* Queue List */}
            {loading ? (
              <div className="admin-loading"><QueueSkeleton /></div>
            ) : filteredQueue.length === 0 ? (
              <div className="admin-empty">
                <h3>📭 No records found</h3>
                <p>{search ? 'Try a different search term.' : 'No records match this filter.'}</p>
              </div>
            ) : (
              <div className="queue-list">
                {filteredQueue.map(action => (
                  <QueueCard
                    key={action.id}
                    action={action}
                    expanded={expandedId === action.id}
                    onToggle={() => setExpandedId(expandedId === action.id ? null : action.id)}
                    onApprove={() => approve(action.id)}
                    onReject={() => reject(action.id)}
                    onSchedule={() => setScheduleAction(action)}
                    onMarkCall={status => markCall(action.id, status)}
                    reviewNotes={reviewNotes[action.id] || ''}
                    onNoteChange={val => setReviewNotes(prev => ({ ...prev, [action.id]: val }))}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Farmers Tab */}
        {activeTab === 'farmers' && (
          <div className="admin-tab-content">
            <div className="farmers-header">
              <h3>👨‍🌾 Registered Farmers <span style={{ color: '#64748b', fontWeight: 400, fontSize: 14 }}>({farmers.length})</span></h3>
              <button className="admin-btn-refresh" onClick={fetchFarmers}>🔄 Refresh</button>
            </div>
            {farmers.length === 0 ? (
              <div className="admin-empty"><h3>No farmers found</h3></div>
            ) : (
              <div className="farmers-table-wrap">
                <table className="farmers-table">
                  <thead>
                    <tr>
                      <th>Farm ID</th>
                      <th>Name</th>
                      <th>Phone</th>
                      <th>Latitude</th>
                      <th>Longitude</th>
                      <th>Area (ha)</th>
                      <th>Radius (m)</th>
                      <th>GPS Profile</th>
                    </tr>
                  </thead>
                  <tbody>
                    {farmers.map(f => (
                      <tr key={f.farmer_id}>
                        <td><code>{f.farmer_id}</code></td>
                        <td>{f.name || '—'}</td>
                        <td>{f.phone || '—'}</td>
                        <td>{f.farm_latitude?.toFixed(4) ?? '—'}</td>
                        <td>{f.farm_longitude?.toFixed(4) ?? '—'}</td>
                        <td>{f.farm_size?.toFixed(1) ?? '—'}</td>
                        <td>{f.verification_radius_meters?.toFixed(0) ?? '—'}</td>
                        <td>
                          <button className="qbtn qbtn-schedule" onClick={() => setFarmProfileId(f.farmer_id)}>
                            🗺️ {f.has_profile ? 'Edit' : 'Set'} GPS
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Root Export ───────────────────────────────────────────────────
export default function AdminPanelRoot({ onLogout }) {
  const [adminSession, setAdminSession] = useState(() => {
    const stored = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    return stored && user ? JSON.parse(user) : null;
  });

  const handleLogin = data => setAdminSession({ username: data.username, role: data.role });

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    setAdminSession(null);
    if (onLogout) onLogout();
  };

  if (!adminSession) return <AdminLogin onLogin={handleLogin} />;
  return <AdminPanel onLogout={handleLogout} />;
}
