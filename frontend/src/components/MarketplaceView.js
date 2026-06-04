import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useLanguage } from '../context/LanguageContext';

const MarketplaceView = () => {
  const { t } = useLanguage();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [stateFilter, setStateFilter] = useState('');
  const [cropFilter, setCropFilter] = useState('');
  const [priceSort, setPriceSort] = useState(''); // 'high-low' or 'low-high'

  const API_URL = 'http://localhost:8000/api/marketplace';

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async (selectedState = '') => {
    try {
      setLoading(true);
      setError(null);
      
      const url = selectedState ? `${API_URL}?state=${selectedState}` : API_URL;
      const response = await axios.get(url);
      
      if (response.data && response.data.records) {
        setData(response.data.records);
      } else {
        setError('Invalid data format received from API');
      }
    } catch (err) {
      console.error('Error fetching market data:', err);
      setError('Failed to fetch market data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Extract unique states and crops for dropdowns
  const uniqueStates = useMemo(() => {
    const states = new Set(data.map(item => item.state).filter(Boolean));
    return Array.from(states).sort();
  }, [data]);

  const uniqueCrops = useMemo(() => {
    const crops = new Set(data.map(item => item.commodity).filter(Boolean));
    return Array.from(crops).sort();
  }, [data]);

  // Filter and sort the data
  const filteredAndSortedData = useMemo(() => {
    let result = [...data];

    if (stateFilter) {
      result = result.filter(item => item.state === stateFilter);
    }

    if (cropFilter) {
      result = result.filter(item => item.commodity === cropFilter);
    }

    if (priceSort === 'high-low') {
      result.sort((a, b) => parseFloat(b.modal_price || 0) - parseFloat(a.modal_price || 0));
    } else if (priceSort === 'low-high') {
      result.sort((a, b) => parseFloat(a.modal_price || 0) - parseFloat(b.modal_price || 0));
    }

    return result;
  }, [data, stateFilter, cropFilter, priceSort]);

  return (
    <div className="marketplace-container" style={{ padding: '2rem', height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', color: '#1e3a8a', margin: '0 0 0.5rem 0' }}>🏷️ Live Marketplace</h2>
          <p style={{ color: '#64748b', margin: 0 }}>Real-time Mandi Prices across India (Source: data.gov.in)</p>
        </div>
        <button 
          onClick={fetchMarketData}
          style={{
            padding: '0.6rem 1.2rem',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'background 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.background = '#059669'}
          onMouseLeave={(e) => e.target.style.background = '#10b981'}
        >
          🔄 Refresh Data
        </button>
      </div>

      {/* Filters Section */}
      <div style={{ 
        background: 'white', 
        padding: '1.5rem', 
        borderRadius: '1rem', 
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        marginBottom: '2rem',
        display: 'flex',
        gap: '1.5rem',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: '1 1 200px' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#475569', marginBottom: '0.5rem' }}>
            📍 State
          </label>
          <select 
            value={stateFilter} 
            onChange={(e) => {
              const newState = e.target.value;
              setStateFilter(newState);
              fetchMarketData(newState);
            }}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #cbd5e1', outline: 'none' }}
          >
            <option value="">All States</option>
            {uniqueStates.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        <div style={{ flex: '1 1 200px' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#475569', marginBottom: '0.5rem' }}>
            🌾 Commodity (Crop)
          </label>
          <select 
            value={cropFilter} 
            onChange={(e) => setCropFilter(e.target.value)}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #cbd5e1', outline: 'none' }}
          >
            <option value="">All Commodities</option>
            {uniqueCrops.map(crop => (
              <option key={crop} value={crop}>{crop}</option>
            ))}
          </select>
        </div>

        <div style={{ flex: '1 1 200px' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#475569', marginBottom: '0.5rem' }}>
            💰 Pricing Sort
          </label>
          <select 
            value={priceSort} 
            onChange={(e) => setPriceSort(e.target.value)}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #cbd5e1', outline: 'none' }}
          >
            <option value="">Default order</option>
            <option value="low-high">Price: Low to High</option>
            <option value="high-low">Price: High to Low</option>
          </select>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 0' }}>
          <div className="spinner" style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #3b82f6', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite' }} />
          <p style={{ marginTop: '1rem', color: '#64748b' }}>Fetching live market data...</p>
          <style>{`
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          `}</style>
        </div>
      ) : error ? (
        <div style={{ background: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
          {error}
        </div>
      ) : filteredAndSortedData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '1rem', color: '#64748b' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
          <h3>No records found</h3>
          <p>Try adjusting your filters to see more results.</p>
        </div>
      ) : (
        <>
          <p style={{ color: '#64748b', marginBottom: '1rem' }}>Showing {filteredAndSortedData.length} records</p>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
            gap: '1.5rem' 
          }}>
            {filteredAndSortedData.map((item, index) => (
              <div 
                key={`${item.state}-${item.market}-${item.commodity}-${index}`}
                style={{
                  background: 'white',
                  borderRadius: '1rem',
                  padding: '1.5rem',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  borderTop: '4px solid #3b82f6',
                  transition: 'transform 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem' }}>{item.commodity}</h3>
                    <span style={{ fontSize: '0.8rem', color: '#3b82f6', background: '#eff6ff', padding: '0.2rem 0.5rem', borderRadius: '1rem', display: 'inline-block', marginTop: '0.3rem' }}>
                      Variety: {item.variety || 'N/A'}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#16a34a' }}>
                      ₹{item.modal_price || item.max_price || 'N/A'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>per quintal</div>
                  </div>
                </div>

                <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem', fontSize: '0.875rem' }}>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '0.75rem' }}>Market</div>
                    <div style={{ fontWeight: '500', color: '#334155' }}>🏪 {item.market}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '0.75rem' }}>State</div>
                    <div style={{ fontWeight: '500', color: '#334155' }}>📍 {item.state}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '0.75rem' }}>Arrival Date</div>
                    <div style={{ fontWeight: '500', color: '#334155' }}>📅 {item.arrival_date}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '0.75rem' }}>Price Range</div>
                    <div style={{ fontWeight: '500', color: '#334155' }}>₹{item.min_price || '0'} - ₹{item.max_price || '0'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default MarketplaceView;
