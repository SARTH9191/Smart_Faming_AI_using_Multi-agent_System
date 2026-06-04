import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios to prevent caching
axios.defaults.headers.common['Cache-Control'] = 'no-cache, no-store, must-revalidate';
axios.defaults.headers.common['Pragma'] = 'no-cache';
axios.defaults.headers.common['Expires'] = '0';

function BlockchainView({ apiUrl, farmId }) {
  const [blocks, setBlocks] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [chainValid, setChainValid] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [view, setView] = useState('list'); // 'list' or 'chain'
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [balanceChanged, setBalanceChanged] = useState(false);

  useEffect(() => {
    fetchAllData();
    
    // Poll for updates every 10 seconds (smooth background updates)
    const interval = setInterval(() => {
      fetchAllDataSilent();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [farmId]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      
      // Fetch all blocks
      const blocksResponse = await axios.get(`${apiUrl}/blockchain_blocks?_t=${timestamp}`);
      setBlocks(blocksResponse.data.blocks || []);
      setChainValid(blocksResponse.data.chain_valid);
      
      // Fetch summary
      const summaryResponse = await axios.get(`${apiUrl}/green_token_summary?farm_id=${farmId}&_t=${timestamp}`);
      setSummary(summaryResponse.data);
      
      setLastUpdated(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching blockchain data:', error);
      setLoading(false);
    }
  };

  const fetchAllDataSilent = async () => {
    try {
      setIsUpdating(true);
      
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      
      // Fetch all blocks
      const blocksResponse = await axios.get(`${apiUrl}/blockchain_blocks?_t=${timestamp}`);
      const newBlocks = blocksResponse.data.blocks || [];
      
      // Fetch summary
      const summaryResponse = await axios.get(`${apiUrl}/green_token_summary?farm_id=${farmId}&_t=${timestamp}`);
      const newSummary = summaryResponse.data;
      
      // Check if balance changed
      if (summary && newSummary.current_balance !== summary.current_balance) {
        setBalanceChanged(true);
        setTimeout(() => setBalanceChanged(false), 2000); // Remove animation after 2s
      }
      
      setBlocks(newBlocks);
      setSummary(newSummary);
      setChainValid(blocksResponse.data.chain_valid);
      setLastUpdated(new Date());
      setIsUpdating(false);
    } catch (error) {
      console.error('Error fetching blockchain data silently:', error);
      setIsUpdating(false);
    }
  };

  const verifyBlockchain = async () => {
    try {
      const response = await axios.get(`${apiUrl}/verify_blockchain`);
      alert(response.data.message);
      setChainValid(response.data.is_valid);
    } catch (error) {
      console.error('Error verifying blockchain:', error);
      alert('Error verifying blockchain');
    }
  };

  const getActionColor = (action) => {
    if (action.toLowerCase().includes('irrigation') || action.toLowerCase().includes('water')) return '#3b82f6'; // blue
    if (action.toLowerCase().includes('fertilizer') || action.toLowerCase().includes('organic')) return '#10b981'; // green
    if (action.toLowerCase().includes('market') || action.toLowerCase().includes('sell')) return '#f59e0b'; // yellow
    if (action.toLowerCase().includes('disease') || action.toLowerCase().includes('pest')) return '#ef4444'; // red
    if (action.toLowerCase().includes('genesis')) return '#8b5cf6'; // purple
    return '#6b7280'; // gray
  };

  const filteredBlocks = blocks.filter(block => {
    const matchesSearch = block.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         block.block_number.toString().includes(searchTerm);
    const matchesFilter = filterType === 'all' || block.action.toLowerCase().includes(filterType.toLowerCase());
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
          🌟 Green Token Rewards & History
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isUpdating && (
            <div style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>🔄</span>
              Updating...
            </div>
          )}
          {lastUpdated && !isUpdating && (
            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
              Last updated: {lastUpdated.toLocaleTimeString()}
            </div>
          )}
          <button 
            onClick={fetchAllData}
            disabled={isUpdating}
            style={{
              padding: '0.5rem 1rem',
              background: isUpdating ? '#9ca3af' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: isUpdating ? 'not-allowed' : 'pointer',
              fontSize: '0.9rem',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              transition: 'all 0.3s ease',
              opacity: isUpdating ? 0.6 : 1
            }}
            onMouseEnter={(e) => {
              if (!isUpdating) {
                e.target.style.background = '#059669';
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isUpdating) {
                e.target.style.background = '#10b981';
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
              }
            }}
          >
            🔄 Refresh Stats
          </button>
        </div>
      </div>

      {/* Add CSS animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        @keyframes slideIn {
          from { transform: translateX(-10px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .balance-updated {
          animation: pulse 0.6s ease-in-out;
          box-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
        }
        .new-block {
          animation: slideIn 0.5s ease-out;
        }
      `}</style>

      {/* Summary Cards */}
      <div className="dashboard-grid" style={{ marginBottom: '2rem' }}>
        <div 
          className={`card ${balanceChanged ? 'balance-updated' : ''}`}
          style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            color: 'white',
            transition: 'all 0.3s ease'
          }}
        >
          <div className="card-header">
            <h3 className="card-title" style={{ color: 'white' }}>🌟 Green Token Balance</h3>
          </div>
          <div className="card-content">
            <div style={{ 
              fontSize: '3rem', 
              fontWeight: '700', 
              marginBottom: '0.5rem',
              transition: 'all 0.3s ease'
            }}>
              {summary?.current_balance || 0}
              {balanceChanged && <span style={{ fontSize: '1.5rem', marginLeft: '0.5rem', color: '#fbbf24' }}>✨</span>}
            </div>
            <p style={{ opacity: 0.9 }}>Level: {summary?.sustainability_level || 'Loading...'}</p>
            {balanceChanged && (
              <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', opacity: 0.9 }}>
                🎉 Balance Updated!
              </p>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📦 Total Blocks</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{blocks.length}</div>
            <p style={{ color: '#6b7280', marginTop: '0.5rem' }}>
              Total Transactions: {summary?.total_transactions || 0}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📈 Token Stats</h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#16a34a' }}>Earned: +{summary?.total_earned || 0}</span>
              <span style={{ color: '#dc2626' }}>Spent: -{summary?.total_spent || 0}</span>
            </div>
            <div style={{ fontWeight: '600', fontSize: '1.5rem', color: '#10b981' }}>
              Net: {summary?.net_tokens || 0}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">✅ Chain Status</h3>
          </div>
          <div className="card-content">
            <div className={`status-badge ${chainValid ? 'status-good' : 'status-critical'}`} style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
              {chainValid ? '✓ Valid & Secure' : '✗ Invalid'}
            </div>
            <button 
              className="btn btn-primary"
              onClick={verifyBlockchain}
              style={{ width: '100%' }}
            >
              🔍 Verify Chain Integrity
            </button>
          </div>
        </div>
      </div>

      {/* Top Earning Actions */}
      {summary?.top_earning_actions && summary.top_earning_actions.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div className="card-header">
            <h3 className="card-title">🏆 Top Earning Actions</h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {summary.top_earning_actions.map((item, index) => (
                <div key={index} style={{ 
                  padding: '1rem', 
                  background: '#f9fafb', 
                  borderRadius: '8px',
                  borderLeft: `4px solid ${getActionColor(item.action)}`
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#10b981', marginBottom: '0.25rem' }}>
                    +{item.tokens}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {item.action}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* View Toggle and Search */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            className={`btn ${view === 'list' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('list')}
          >
            📋 List View
          </button>
          <button 
            className={`btn ${view === 'chain' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('chain')}
          >
            🔗 Chain View
          </button>
        </div>

        <input
          type="text"
          placeholder="🔍 Search blocks by action or number..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: '0.5rem 1rem',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '1rem'
          }}
        />

        <select 
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{
            padding: '0.5rem 1rem',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '1rem'
          }}
        >
          <option value="all">All Actions</option>
          <option value="irrigation">💧 Irrigation</option>
          <option value="fertilizer">🌱 Fertilizer</option>
          <option value="solar">☀️ Solar</option>
          <option value="composting">♻️ Composting</option>
          <option value="rainwater">🌧️ Rainwater</option>
          <option value="rotation">🔄 Crop Rotation</option>
          <option value="tillage">🚜 Tillage</option>
          <option value="pest">🐛 Pest Management</option>
        </select>
      </div>

      {/* Chain View */}
      {view === 'chain' && (
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ 
            display: 'flex', 
            overflowX: 'auto', 
            padding: '2rem 1rem',
            background: '#f9fafb',
            borderRadius: '12px',
            gap: '1rem'
          }}>
            {filteredBlocks.map((block, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
                <div 
                  onClick={() => setSelectedBlock(block)}
                  style={{
                    background: selectedBlock?.block_number === block.block_number ? '#10b981' : 'white',
                    color: selectedBlock?.block_number === block.block_number ? 'white' : '#1f2937',
                    border: `3px solid ${getActionColor(block.action)}`,
                    borderRadius: '12px',
                    padding: '1rem',
                    width: '150px',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    boxShadow: selectedBlock?.block_number === block.block_number ? '0 10px 30px rgba(0,0,0,0.2)' : '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                  onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <div style={{ fontWeight: '700', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                    Block #{block.block_number}
                  </div>
                  <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>
                    {block.action.substring(0, 20)}{block.action.length > 20 ? '...' : ''}
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', marginTop: '0.5rem' }}>
                    {block.tokens_awarded > 0 ? `+${block.tokens_awarded}` : block.tokens_awarded} 🌟
                  </div>
                </div>
                {index < filteredBlocks.length - 1 && (
                  <div style={{ 
                    width: '40px', 
                    height: '3px', 
                    background: '#d1d5db',
                    position: 'relative'
                  }}>
                    <div style={{
                      position: 'absolute',
                      right: '-5px',
                      top: '-4px',
                      width: '0',
                      height: '0',
                      borderTop: '6px solid transparent',
                      borderBottom: '6px solid transparent',
                      borderLeft: '10px solid #d1d5db'
                    }}></div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Selected Block Details */}
          {selectedBlock && (
            <div className="card" style={{ marginTop: '2rem' }}>
              <div className="card-header" style={{ background: getActionColor(selectedBlock.action), color: 'white' }}>
                <h3 className="card-title" style={{ color: 'white' }}>
                  Block #{selectedBlock.block_number} Details
                </h3>
              </div>
              <div className="card-content">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
                  <div>
                    <strong>Timestamp:</strong>
                    <div style={{ color: '#6b7280', marginTop: '0.25rem' }}>
                      {new Date(selectedBlock.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <strong>Action:</strong>
                    <div style={{ color: '#6b7280', marginTop: '0.25rem' }}>{selectedBlock.action}</div>
                  </div>
                  <div>
                    <strong>Agent Responsible:</strong>
                    <div style={{ color: '#6b7280', marginTop: '0.25rem' }}>{selectedBlock.agent_responsible}</div>
                  </div>
                  <div>
                    <strong>Green Tokens:</strong>
                    <div style={{ color: '#10b981', fontWeight: '600', fontSize: '1.25rem', marginTop: '0.25rem' }}>
                      {selectedBlock.tokens_awarded > 0 ? '+' : ''}{selectedBlock.tokens_awarded}
                    </div>
                  </div>
                  <div>
                    <strong>Farm ID:</strong>
                    <div style={{ color: '#6b7280', marginTop: '0.25rem' }}>{selectedBlock.farm_id}</div>
                  </div>
                  <div>
                    <strong>Previous Hash:</strong>
                    <div style={{ 
                      fontFamily: 'monospace', 
                      fontSize: '0.75rem', 
                      color: '#6b7280',
                      wordBreak: 'break-all',
                      marginTop: '0.25rem'
                    }}>
                      {selectedBlock.previous_hash.substring(0, 20)}...
                    </div>
                  </div>
                  <div>
                    <strong>Current Hash:</strong>
                    <div style={{ 
                      fontFamily: 'monospace', 
                      fontSize: '0.75rem', 
                      color: '#6b7280',
                      wordBreak: 'break-all',
                      marginTop: '0.25rem'
                    }}>
                      {selectedBlock.current_hash.substring(0, 20)}...
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* List View */}
      {view === 'list' && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📜 Token Earning History ({filteredBlocks.length} Actions)</h3>
          </div>
          <div className="card-content">
            {filteredBlocks.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #e5e7eb', background: '#f9fafb' }}>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Block #</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Timestamp</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Action</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Agent</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Tokens</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600' }}>Hash</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredBlocks.map((block, index) => (
                      <tr 
                        key={index} 
                        style={{ 
                          borderBottom: '1px solid #f3f4f6',
                          cursor: 'pointer',
                          transition: 'background 0.2s'
                        }}
                        onClick={() => setSelectedBlock(block)}
                        onMouseOver={(e) => e.currentTarget.style.background = '#f9fafb'}
                        onMouseOut={(e) => e.currentTarget.style.background = 'white'}
                      >
                        <td style={{ padding: '1rem', fontWeight: '700' }}>
                          <div style={{
                            display: 'inline-block',
                            background: getActionColor(block.action),
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '4px'
                          }}>
                            #{block.block_number}
                          </div>
                        </td>
                        <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                          {new Date(block.timestamp).toLocaleString()}
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <div style={{ 
                            display: 'inline-block',
                            padding: '0.25rem 0.5rem',
                            background: '#f3f4f6',
                            borderRadius: '4px',
                            borderLeft: `3px solid ${getActionColor(block.action)}`
                          }}>
                            {block.action}
                          </div>
                        </td>
                        <td style={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>
                          {block.agent_responsible}
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span style={{ 
                            color: block.tokens_awarded > 0 ? '#16a34a' : '#6b7280', 
                            fontWeight: '700',
                            fontSize: '1rem'
                          }}>
                            {block.tokens_awarded > 0 ? '+' : ''}{block.tokens_awarded} 🌟
                          </span>
                        </td>
                        <td style={{ padding: '1rem', fontFamily: 'monospace', fontSize: '0.75rem', color: '#9ca3af' }}>
                          {block.current_hash.substring(0, 12)}...
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                <p>No blocks found matching your search criteria</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* How to Earn More Tokens */}
      <div className="card" style={{ marginTop: '2rem' }}>
        <div className="card-header">
          <h3 className="card-title">💡 Earn More Green Tokens</h3>
        </div>
        <div className="card-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {[
              { icon: '💧', name: 'Drip Irrigation', tokens: 20 },
              { icon: '🌱', name: 'Organic Fertilizer', tokens: 15 },
              { icon: '☀️', name: 'Solar Pump', tokens: 30 },
              { icon: '🌧️', name: 'Rainwater Harvesting', tokens: 25 },
              { icon: '♻️', name: 'Composting', tokens: 15 },
              { icon: '🔄', name: 'Crop Rotation', tokens: 12 },
              { icon: '🌾', name: 'Zero Tillage', tokens: 18 },
              { icon: '🍃', name: 'Mulching', tokens: 10 }
            ].map((item, index) => (
              <div key={index} style={{ 
                background: '#f0fdf4', 
                padding: '1rem', 
                borderRadius: '8px',
                textAlign: 'center',
                border: '2px solid #bbf7d0'
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{item.icon}</div>
                <strong>{item.name}</strong>
                <div style={{ color: '#16a34a', fontWeight: '700', fontSize: '1.25rem', marginTop: '0.5rem' }}>
                  +{item.tokens} tokens
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BlockchainView;
