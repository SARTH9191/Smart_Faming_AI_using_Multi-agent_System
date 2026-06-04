import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProfileView({ farmer, apiUrl }) {
  const [farmerProfile, setFarmerProfile] = useState(null);
  const [weather, setWeather] = useState(null);
  const [market, setMarket] = useState(null);
  const [satellite, setSatellite] = useState(null);
  const [cropsData, setCropsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState({});
  const [showCropForm, setShowCropForm] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingCrop, setEditingCrop] = useState(null);
  const [cropForm, setCropForm] = useState({
    crop_type: '',
    area_hectares: '',
    planted_date: '',
    latitude: '',
    longitude: ''
  });
  const [profileForm, setProfileForm] = useState({
    name: '',
    total_land_area_acres: '',
    phone: '',
    email: ''
  });

  const farmId = farmer?.farmerId || farmer?.farmer_id || 'FARM001';

  useEffect(() => {
    fetchAllData();
  }, [farmId]);

  const fetchAllData = async () => {
    setLoading(true);
    const newErrors = {};

    const results = await Promise.allSettled([
      axios.get(`${apiUrl}/profile?farm_id=${farmId}`),
      axios.get(`${apiUrl}/get_weather?location=Pune`),
      axios.get(`${apiUrl}/get_market_forecast?crop=wheat`),
      axios.get(`${apiUrl}/drone_satellite_analysis?farm_id=${farmId}`),
      axios.get(`${apiUrl}/crops?farm_id=${farmId}`)
    ]);

    if (results[0].status === 'fulfilled') setFarmerProfile(results[0].value.data);
    else newErrors.profile = true;

    if (results[1].status === 'fulfilled') setWeather(results[1].value.data);
    else newErrors.weather = true;

    if (results[2].status === 'fulfilled') setMarket(results[2].value.data);
    else newErrors.market = true;

    if (results[3].status === 'fulfilled') setSatellite(results[3].value.data);
    else newErrors.satellite = true;

    if (results[4].status === 'fulfilled') setCropsData(results[4].value.data.crops || []);
    else newErrors.crops = true;

    setErrors(newErrors);
    setLoading(false);
  };

  const handleCropFormChange = (e) => {
    const { name, value } = e.target;
    setCropForm(prev => ({ ...prev, [name]: value }));
  };

  const openAddCropForm = () => {
    setCropForm({
      crop_type: '',
      area_hectares: '',
      planted_date: '',
      latitude: '',
      longitude: ''
    });
    setEditingCrop(null);
    setShowCropForm(true);
  };

  const openEditCropForm = (crop) => {
    setCropForm({
      crop_type: crop.crop_type || '',
      area_hectares: crop.area_hectares?.toString() || '',
      planted_date: crop.planted_date ? crop.planted_date.split('T')[0] : '',
      latitude: crop.latitude?.toString() || '',
      longitude: crop.longitude?.toString() || ''
    });
    setEditingCrop(crop.id);
    setShowCropForm(true);
  };

  const handleSaveCrop = async () => {
    setSaving(true);
    try {
      const lat = cropForm.latitude || (18.5 + Math.random() * 0.5).toFixed(4);
      const lon = cropForm.longitude || (73.5 + Math.random() * 0.5).toFixed(4);
      
      const cropData = {
        crop_type: cropForm.crop_type,
        area_hectares: cropForm.area_hectares ? parseFloat(cropForm.area_hectares) : 1,
        planted_date: cropForm.planted_date || new Date().toISOString().split('T')[0],
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        status: 'growing'
      };

      if (editingCrop) {
        await axios.put(`${apiUrl}/crops/${editingCrop}`, cropData);
      } else {
        await axios.post(`${apiUrl}/crops?farm_id=${farmId}`, cropData);
      }
      
      setShowCropForm(false);
      fetchAllData();
    } catch (err) {
      console.error('Error saving crop:', err);
      alert('Failed to save crop');
    }
    setSaving(false);
  };

  const handleDeleteCrop = async (cropId) => {
    if (!window.confirm('Are you sure you want to delete this crop?')) return;
    try {
      await axios.delete(`${apiUrl}/crops/${cropId}`);
      fetchAllData();
    } catch (err) {
      console.error('Error deleting crop:', err);
      alert('Failed to delete crop');
    }
  };

  const openProfileForm = () => {
    setProfileForm({
      name: farmerProfile?.name || farmer?.name || '',
      total_land_area_acres: farmerProfile?.total_land_area_acres?.toString() || '',
      phone: farmerProfile?.phone || '',
      email: farmerProfile?.email || '',
      location: farmerProfile?.location || '',
      soil_type: farmerProfile?.soil_type || '',
      irrigation_source: farmerProfile?.irrigation_source || '',
      is_organic: farmerProfile?.is_organic || false,
      latitude: farmerProfile?.latitude?.toString() || '',
      longitude: farmerProfile?.longitude?.toString() || ''
    });

    // Auto-fetch location if missing
    if (!farmerProfile?.latitude || !farmerProfile?.longitude) {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition((position) => {
          setProfileForm(prev => ({
            ...prev,
            latitude: position.coords.latitude.toString(),
            longitude: position.coords.longitude.toString()
          }));
        }, (err) => console.log("Geolocation error:", err));
      }
    }
    setShowProfileForm(true);
  };

  const handleProfileFormChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await axios.put(`${apiUrl}/profile/farm_details?farm_id=${farmId}`, {
        total_land_area_acres: profileForm.total_land_area_acres ? parseFloat(profileForm.total_land_area_acres) : null
      });
      
      await axios.put(`${apiUrl}/profile/update_basic?farm_id=${farmId}`, {
        name: profileForm.name,
        phone: profileForm.phone,
        email: profileForm.email,
        location: profileForm.location,
        soil_type: profileForm.soil_type,
        irrigation_source: profileForm.irrigation_source,
        is_organic: profileForm.is_organic,
        latitude: profileForm.latitude ? parseFloat(profileForm.latitude) : null,
        longitude: profileForm.longitude ? parseFloat(profileForm.longitude) : null
      });
      
      setShowProfileForm(false);
      await fetchAllData();
    } catch (err) {
      console.error('Error saving profile:', err);
      alert('Failed to save profile');
    }
    setSaving(false);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '1rem' }}>
        <div className="spinner"></div>
        <p style={{ color: '#6b7280', fontSize: '0.95rem' }}>Loading your farm profile...</p>
      </div>
    );
  }

  const activeCropsCount = cropsData.filter(c => c.status === 'growing').length;
  const totalCropHa = cropsData.reduce((sum, c) => sum + (c.area_hectares || 0), 0);
  const lat = farmerProfile?.latitude || 18.5204;
  const lon = farmerProfile?.longitude || 73.8567;
  const farmSize = farmerProfile?.total_land_area_acres || farmerProfile?.farm_size || 12.5;
  const farmSizeAcres = farmSize.toFixed(1);

  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.02}%2C${lat - 0.015}%2C${lon + 0.02}%2C${lat + 0.015}&layer=mapnik&marker=${lat}%2C${lon}`;
  const mapLink = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=14/${lat}/${lon}`;

  return (
    <div style={{ animation: 'fadeIn 0.4s ease-out' }}>

      {/* Hero Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%)',
        color: 'white',
        padding: '2rem 2.5rem',
        borderRadius: '1.5rem',
        marginBottom: '2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '2rem',
        flexWrap: 'wrap',
        boxShadow: '0 10px 30px -5px rgba(16, 185, 129, 0.45)'
      }}>
        <div style={{
          width: '90px', height: '90px',
          background: 'rgba(255,255,255,0.2)',
          borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2.75rem',
          border: '3px solid rgba(255,255,255,0.5)',
          flexShrink: 0
        }}>👤</div>

        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '1.9rem', margin: '0 0 0.25rem 0', fontWeight: '800' }}>
            {farmerProfile?.name || farmer?.name || 'Farmer'}
          </h2>
          <p style={{ opacity: 0.85, margin: '0 0 0.75rem 0', fontSize: '0.95rem' }}>
            ✉️ {farmerProfile?.email || farmer?.email} &nbsp;|&nbsp; 🆔 {farmId}
            {farmerProfile?.phone && <> &nbsp;|&nbsp; 📞 {farmerProfile.phone}</>}
          </p>
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            {[
              { icon: '📍', text: farmerProfile?.location || 'Pune, Maharashtra' },
              { icon: '📐', text: farmSizeAcres + ' acres' },
              { icon: '🌐', text: `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E` },
              { icon: '🌱', text: farmerProfile?.soil_type || 'Loamy' },
              { icon: '💧', text: farmerProfile?.irrigation_source || 'Borewell' },
              { icon: '🟢', text: farmerProfile?.is_organic ? 'Organic Certified' : 'Conventional' },
            ].map((badge, i) => (
              <span key={i} style={{
                background: 'rgba(255,255,255,0.2)',
                backdropFilter: 'blur(4px)',
                padding: '0.35rem 0.9rem',
                borderRadius: '2rem',
                fontSize: '0.82rem',
                fontWeight: '600',
                border: '1px solid rgba(255,255,255,0.3)'
              }}>
                {badge.icon} {badge.text}
              </span>
            ))}
          </div>
        </div>

        <button onClick={fetchAllData} style={{
          background: 'rgba(255,255,255,0.2)',
          border: '1px solid rgba(255,255,255,0.4)',
          color: 'white',
          padding: '0.5rem 1rem',
          borderRadius: '0.75rem',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '0.85rem',
          flexShrink: 0
        }}>
          🔄 Refresh
        </button>
        <button onClick={openProfileForm} style={{
          background: 'rgba(255,255,255,0.2)',
          border: '1px solid rgba(255,255,255,0.4)',
          color: 'white',
          padding: '0.5rem 1rem',
          borderRadius: '0.75rem',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '0.85rem',
          flexShrink: 0
        }}>
          ✏️ Edit Profile
        </button>
      </div>

      {/* Farm Location Map */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="card-title">🗺️ Farm Location</h3>
          <a href={mapLink} target="_blank" rel="noreferrer" style={{
            fontSize: '0.82rem', color: '#059669', fontWeight: '600', textDecoration: 'none',
            padding: '0.3rem 0.75rem', background: '#f0fdf4', borderRadius: '0.5rem',
            border: '1px solid #bbf7d0'
          }}>
            Open Full Map ↗
          </a>
        </div>
        <div className="card-content" style={{ padding: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 0, borderBottom: '1px solid #f3f4f6' }}>
            {[
              { label: 'Latitude', value: `${lat.toFixed(4)}°N`, icon: '🌐' },
              { label: 'Longitude', value: `${lon.toFixed(4)}°E`, icon: '🌐' },
              { label: 'Farm Size', value: `${farmSizeAcres} acres`, icon: '📐' },
            ].map((item, i) => (
              <div key={i} style={{
                padding: '1rem 1.25rem',
                borderRight: i < 2 ? '1px solid #f3f4f6' : 'none',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.1rem' }}>{item.icon}</div>
                <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#111827', marginTop: '0.25rem' }}>{item.value}</div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</div>
              </div>
            ))}
          </div>
          <div style={{ position: 'relative', height: '250px', borderRadius: '0 0 1rem 1rem', overflow: 'hidden' }}>
            <iframe
              title="Farm Location Map"
              src={mapUrl}
              style={{ width: '100%', height: '100%', border: 'none' }}
              loading="lazy"
            />
          </div>
        </div>
      </div>

      {/* My Crops Section */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="card-title">🌾 My Crops</h3>
          <button onClick={openAddCropForm} style={{
            background: '#059669', color: 'white', border: 'none',
            padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer',
            fontWeight: '600', fontSize: '0.85rem'
          }}>
            + Add Crop
          </button>
        </div>
        <div className="card-content">
          {cropsData.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af' }}>
              <p>No crops added yet. Click "Add Crop" to add your first crop.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #f3f4f6' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Crop</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Area (ha)</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Sowing Date</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Location</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Status</th>
                    <th style={{ textAlign: 'center', padding: '0.75rem', color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cropsData.map((crop, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '0.75rem', fontWeight: '600' }}>
                        {getCropIcon(crop.crop_type)} {crop.crop_type}
                      </td>
                      <td style={{ padding: '0.75rem' }}>{crop.area_hectares} ha</td>
                      <td style={{ padding: '0.75rem' }}>{crop.planted_date ? crop.planted_date.split('T')[0] : '-'}</td>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem', color: '#6b7280' }}>
                        {crop.latitude?.toFixed(4)}°N, {crop.longitude?.toFixed(4)}°E
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <StatusBadge status={crop.status} />
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                        <button onClick={() => openEditCropForm(crop)} style={{ marginRight: '0.5rem', padding: '0.3rem 0.6rem', border: '1px solid #d1d5db', borderRadius: '0.3rem', background: 'white', cursor: 'pointer', fontSize: '0.8rem' }}>Edit</button>
                        <button onClick={() => handleDeleteCrop(crop.id)} style={{ padding: '0.3rem 0.6rem', border: '1px solid #ef4444', borderRadius: '0.3rem', background: '#fef2f2', color: '#ef4444', cursor: 'pointer', fontSize: '0.8rem' }}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {cropsData.length > 0 && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#f0fdf4', borderRadius: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: '600' }}>Total Crops: {cropsData.length}</span>
              <span style={{ fontWeight: '600' }}>Total Area: {totalCropHa.toFixed(2)} ha</span>
            </div>
          )}
        </div>
      </div>

      {/* 3-Column Data Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>

        {/* Crop Assets */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🚜 Crop Assets</h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
              <StatBox value={activeCropsCount} label="Active Crops" color="#059669" bg="#f0fdf4" />
              <StatBox value={`${totalCropHa.toFixed(1)} ha`} label="Planted Area" color="#059669" bg="#f0fdf4" />
            </div>
          </div>
        </div>

        {/* Weather */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🌤️ Live Weather</h3>
            <span style={{ fontSize: '0.72rem', color: '#3b82f6', background: '#eff6ff', padding: '0.2rem 0.5rem', borderRadius: '1rem', fontWeight: '600' }}>
              OpenWeather
            </span>
          </div>
          <div className="card-content">
            {weather ? (
              <>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                  <div>
                    <div style={{ fontSize: '3rem', fontWeight: '800', color: '#1d4ed8', lineHeight: 1 }}>
                      {weather.current?.temperature ?? '—'}°C
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#6b7280', marginTop: '0.25rem' }}>
                      Feels like {weather.current?.feels_like ?? '—'}°C
                    </div>
                  </div>
                  <div style={{ fontSize: '3.5rem' }}>{getWeatherIcon(weather.current?.conditions)}</div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                  <InfoChip icon="💧" label="Humidity" value={`${weather.current?.humidity ?? '—'}%`} />
                  <InfoChip icon="📍" label="Location" value={weather.location || 'Pune'} />
                  <InfoChip icon="☁️" label="Conditions" value={weather.current?.conditions ?? '—'} />
                  <InfoChip icon="📊" label="Source" value="OpenWeather" />
                </div>
              </>
            ) : (
              <ErrorMessage msg="Weather data unavailable" />
            )}
          </div>
        </div>

        {/* Market */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📈 Market Prices</h3>
            <span style={{ fontSize: '0.72rem', color: '#d97706', background: '#fffbeb', padding: '0.2rem 0.5rem', borderRadius: '1rem', fontWeight: '600' }}>
              data.gov.in
            </span>
          </div>
          <div className="card-content">
            {market ? (
              <>
                <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.82rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {market.crop || 'Wheat'} · Today's Avg Price
                  </div>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#059669', margin: '0.25rem 0' }}>
                    ₹{market.current_price ? Math.round(market.current_price).toLocaleString() : '—'}
                    <span style={{ fontSize: '0.9rem', fontWeight: '400', color: '#6b7280' }}>/qtl</span>
                  </div>
                </div>
                {market.sample_mandis?.slice(0, 3).map((m, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between',
                    padding: '0.45rem 0',
                    borderTop: '1px solid #f3f4f6',
                    fontSize: '0.82rem'
                  }}>
                    <span style={{ color: '#374151' }}>{m.mandi}</span>
                    <span style={{ fontWeight: '700', color: '#059669' }}>₹{Math.round(m.price).toLocaleString()}</span>
                  </div>
                ))}
              </>
            ) : (
              <ErrorMessage msg="Market data unavailable" />
            )}
          </div>
        </div>
      </div>

      {/* Satellite + Contact */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>

        {/* Satellite */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🛰️ Satellite & Field Health</h3>
          </div>
          <div className="card-content">
            {satellite ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <StatBox value={satellite.drone_analysis?.ndvi_average ?? '—'} label="NDVI Index" color="#7c3aed" bg="#f5f3ff" />
                <StatBox value={satellite.drone_analysis?.crop_health ?? '—'} label="Crop Health" color="#7c3aed" bg="#f5f3ff" />
                <StatBox value={`${satellite.satellite_analysis?.temperature_trend?.current ?? '—'}°C`} label="Sat. Temp" color="#7c3aed" bg="#f5f3ff" />
                <StatBox value={`${satellite.satellite_analysis?.precipitation?.last_7_days_mm ?? '—'}mm`} label="7-Day Rain" color="#7c3aed" bg="#f5f3ff" />
              </div>
            ) : (
              <ErrorMessage msg="Satellite data unavailable" />
            )}
          </div>
        </div>

        {/* Contact Card */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📋 Account Details</h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {[
                { icon: '👤', label: 'Name', value: farmerProfile?.name || '—' },
                { icon: '📧', label: 'Email', value: farmerProfile?.email || '—' },
                { icon: '📞', label: 'Phone', value: farmerProfile?.phone || '—' },
                { icon: '🌍', label: 'Language', value: farmerProfile?.language?.toUpperCase() || 'EN' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>{item.icon}</span>
                  <div>
                    <div style={{ fontSize: '0.72rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{item.label}</div>
                    <div style={{ fontWeight: '600', fontSize: '0.88rem', color: '#111827' }}>{item.value}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Crop Form Modal */}
      {showCropForm && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowCropForm(false)}>
          <div style={{
            background: 'white', borderRadius: '1rem', padding: '2rem', width: '90%', maxWidth: '500px',
            boxShadow: '0 20px 50px rgba(0,0,0,0.3)'
          }} onClick={e => e.stopPropagation()}>
            <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.5rem', color: '#059669' }}>
              {editingCrop ? '✏️ Edit Crop' : '🌾 Add New Crop'}
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Crop Name *
                </label>
                <input
                  type="text"
                  name="crop_type"
                  value={cropForm.crop_type}
                  onChange={handleCropFormChange}
                  placeholder="e.g., Wheat, Rice, Cotton"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Sowed Area (hectares) *
                </label>
                <input
                  type="number"
                  name="area_hectares"
                  value={cropForm.area_hectares}
                  onChange={handleCropFormChange}
                  placeholder="e.g., 2"
                  step="0.1"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Date of Sowing *
                </label>
                <input
                  type="date"
                  name="planted_date"
                  value={cropForm.planted_date}
                  onChange={handleCropFormChange}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                    Latitude
                  </label>
                  <input
                    type="number"
                    name="latitude"
                    value={cropForm.latitude}
                    onChange={handleCropFormChange}
                    placeholder="e.g., 18.5204"
                    step="0.0001"
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                    Longitude
                  </label>
                  <input
                    type="number"
                    name="longitude"
                    value={cropForm.longitude}
                    onChange={handleCropFormChange}
                    placeholder="e.g., 73.8567"
                    step="0.0001"
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                  />
                </div>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: 0 }}>
                * Leave lat/lon empty to auto-generate random coordinates
              </p>
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button
                onClick={handleSaveCrop}
                disabled={saving || !cropForm.crop_type || !cropForm.area_hectares}
                style={{
                  flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: 'none',
                  background: saving || !cropForm.crop_type || !cropForm.area_hectares ? '#9ca3af' : '#059669', 
                  color: 'white', fontSize: '1rem', fontWeight: '600',
                  cursor: saving ? 'not-allowed' : 'pointer'
                }}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => setShowCropForm(false)}
                style={{
                  flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db',
                  background: 'white', color: '#374151', fontSize: '1rem', fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Profile Edit Modal */}
      {showProfileForm && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowProfileForm(false)}>
          <div style={{
            background: 'white', borderRadius: '1rem', padding: '2rem', width: '90%', maxWidth: '450px',
            boxShadow: '0 20px 50px rgba(0,0,0,0.3)'
          }} onClick={e => e.stopPropagation()}>
            <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.5rem', color: '#059669' }}>
              ✏️ Edit Profile
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Your Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={profileForm.name}
                  onChange={handleProfileFormChange}
                  placeholder="Enter your name"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Total Land Area (acres)
                </label>
                <input
                  type="number"
                  name="total_land_area_acres"
                  value={profileForm.total_land_area_acres}
                  onChange={handleProfileFormChange}
                  placeholder="e.g., 5"
                  step="0.1"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Phone Number
                </label>
                <input
                  type="text"
                  name="phone"
                  value={profileForm.phone}
                  onChange={handleProfileFormChange}
                  placeholder="e.g., 9876543210"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.3rem', color: '#374151' }}>
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={profileForm.email}
                  onChange={handleProfileFormChange}
                  placeholder="e.g., farmer@email.com"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db', fontSize: '1rem' }}
                />
              </div>

              {/* Grounding Fields Section */}
              <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', border: '1px solid #f3f4f6', marginTop: '0.5rem' }}>
                <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem', color: '#059669' }}>🌍 Farm Grounding</h4>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: '600', marginBottom: '0.2rem' }}>Soil Type</label>
                    <select name="soil_type" value={profileForm.soil_type} onChange={handleProfileFormChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid #d1d5db' }}>
                      <option value="">Select...</option>
                      <option value="Loamy">Loamy</option>
                      <option value="Clay">Clay</option>
                      <option value="Sandy">Sandy</option>
                      <option value="Black">Black</option>
                      <option value="Red">Red</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: '600', marginBottom: '0.2rem' }}>Irrigation</label>
                    <select name="irrigation_source" value={profileForm.irrigation_source} onChange={handleProfileFormChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid #d1d5db' }}>
                      <option value="">Select...</option>
                      <option value="Borewell">Borewell</option>
                      <option value="Canal">Canal</option>
                      <option value="Rainfed">Rainfed</option>
                      <option value="Drip">Drip</option>
                    </select>
                  </div>
                </div>

                <div style={{ marginTop: '0.75rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                    <input type="checkbox" name="is_organic" checked={profileForm.is_organic} onChange={(e) => setProfileForm(prev => ({ ...prev, is_organic: e.target.checked }))} />
                    Certified Organic Farm
                  </label>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.75rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: '600', marginBottom: '0.2rem' }}>Lat</label>
                    <input type="text" name="latitude" value={profileForm.latitude} onChange={handleProfileFormChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid #d1d5db' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: '600', marginBottom: '0.2rem' }}>Lon</label>
                    <input type="text" name="longitude" value={profileForm.longitude} onChange={handleProfileFormChange} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid #d1d5db' }} />
                  </div>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button
                onClick={handleSaveProfile}
                disabled={saving}
                style={{
                  flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: 'none',
                  background: saving ? '#9ca3af' : '#059669', 
                  color: 'white', fontSize: '1rem', fontWeight: '600',
                  cursor: saving ? 'not-allowed' : 'pointer'
                }}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => setShowProfileForm(false)}
                style={{
                  flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db',
                  background: 'white', color: '#374151', fontSize: '1rem', fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

function StatBox({ value, label, color, bg }) {
  return (
    <div style={{ textAlign: 'center', padding: '0.85rem 0.5rem', background: bg, borderRadius: '0.75rem' }}>
      <div style={{ fontSize: '1.3rem', fontWeight: '800', color }}>{value}</div>
      <div style={{ fontSize: '0.7rem', color, opacity: 0.75, textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '0.15rem' }}>{label}</div>
    </div>
  );
}

function InfoChip({ icon, label, value }) {
  return (
    <div style={{ background: '#f9fafb', borderRadius: '0.6rem', padding: '0.5rem 0.6rem' }}>
      <div style={{ fontSize: '0.68rem', color: '#9ca3af', textTransform: 'uppercase' }}>{icon} {label}</div>
      <div style={{ fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginTop: '0.1rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{value}</div>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    growing: { bg: '#dcfce7', color: '#166534', label: 'Growing' },
    ready:   { bg: '#fef9c3', color: '#854d0e', label: 'Ready' },
    harvested: { bg: '#f3f4f6', color: '#374151', label: 'Harvested' },
  };
  const s = map[status] || { bg: '#f3f4f6', color: '#6b7280', label: status };
  return (
    <span style={{ background: s.bg, color: s.color, fontSize: '0.72rem', fontWeight: '700', padding: '0.2rem 0.55rem', borderRadius: '1rem', textTransform: 'capitalize' }}>
      {s.label}
    </span>
  );
}

function ErrorMessage({ msg }) {
  return (
    <div style={{ textAlign: 'center', padding: '1.5rem 0', color: '#9ca3af', fontSize: '0.85rem' }}>
      ⚠️ {msg}
    </div>
  );
}

function getCropIcon(cropType) {
  const icons = { wheat: '🌾', rice: '🍚', corn: '🌽', maize: '🌽', tomato: '🍅', tomatoes: '🍅', potato: '🥔', potatoes: '🥔', onion: '🧅', onions: '🧅', carrot: '🥕', sugarcane: '🎋', cotton: '☁️', soybean: '🫘', soybeans: '🫘', mango: '🥭', banana: '🍌', chilli: '🌶️', sorghum: '🌿', bajra: '🌿' };
  return icons[cropType?.toLowerCase()] || '🌿';
}

function getWeatherIcon(condition) {
  if (!condition) return '🌤️';
  const c = condition.toLowerCase();
  if (c.includes('rain') || c.includes('drizzle')) return '🌧️';
  if (c.includes('thunder')) return '⛈️';
  if (c.includes('cloud')) return '☁️';
  if (c.includes('fog') || c.includes('mist') || c.includes('haze')) return '🌫️';
  if (c.includes('snow')) return '❄️';
  if (c.includes('clear') || c.includes('sunny')) return '☀️';
  return '🌤️';
}

export default ProfileView;
