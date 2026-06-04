import React, { useState, useEffect } from 'react';
import axios from 'axios';

function BlockchainView({ apiUrl, farmId }) {
  const [blockchainData, setBlockchainData] = useState(null);
  const [greenTokens, setGreenTokens] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBlockchainData();
    fetchGreenTokens();
  }, [farmId]);

  const fetchBlockchainData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiUrl}/blockchain_log?limit=20`);
      setBlockchainData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching blockchain data:', error);
      setLoading(false);
    }
  };

  const fetchGreenTokens = async () => {
    try {
      const response = await axios.get(`${apiUrl}/green_tokens/${farmId}`);
      setGreenTokens(response.data.balance);
    } catch (error) {
      console.error('Error fetching green tokens:', error);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.75rem' }}>⛓️ Blockchain & Green Tokens</h2>

      {/* Green Token Wallet */}
      <div className="token-wallet" style={{ marginBottom: '2rem' }}>
        <h3>🌟 Your Green Token Wallet</h3>
        <div className="token-balance">{greenTokens}</div>
        <p>Total Green Tokens Earned</p>
        <p style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '1rem' }}>
          Earn tokens by adopting sustainable farming practices like:
          <br />
          💧 Drip Irrigation (+20) | 🌱 Organic Fertilizer (+15) | ♻️ Composting (+15)
          <br />
          ☀️ Solar Pump (+30) | 🌧️ Rainwater Harvesting (+25)
        </p>
      </div>

      {/* Blockchain Stats */}
      <div className="dashboard-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📦 Total Blocks</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{blockchainData?.total_blocks || 0}</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">✅ Chain Status</h3>
          </div>
          <div className="card-content">
            <div className={`status-badge ${blockchainData?.chain_valid ? 'status-good' : 'status-critical'}`}>
              {blockchainData?.chain_valid ? '✓ Valid' : '✗ Invalid'}
            </div>
            <p style={{ marginTop: '1rem', color: '#6b7280' }}>
              All transactions are cryptographically secured
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🎁 Tokens Issued</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{blockchainData?.total_blocks * 10 || 0}</div>
            <p style={{ marginTop: '1rem', color: '#6b7280' }}>
              Across all farms
            </p>
          </div>
        </div>
      </div>

      {/* Transaction History */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">📜 Recent Transactions</h3>
        </div>
        <div className="card-content">
          {blockchainData?.recent_transactions && blockchainData.recent_transactions.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Block #</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Farm ID</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Action</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Tokens</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Hash</th>
                  </tr>
                </thead>
                <tbody>
                  {blockchainData.recent_transactions.slice(0, 10).map((tx, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '0.75rem', fontWeight: '600' }}>{tx.index}</td>
                      <td style={{ padding: '0.75rem' }}>{tx.data?.farm_id || 'N/A'}</td>
                      <td style={{ padding: '0.75rem' }}>{tx.data?.action_type || tx.data?.message || 'N/A'}</td>
                      <td style={{ padding: '0.75rem', color: '#16a34a', fontWeight: '600' }}>
                        {tx.data?.green_tokens_earned > 0 ? `+${tx.data.green_tokens_earned}` : '-'}
                      </td>
                      <td style={{ padding: '0.75rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {tx.hash?.substring(0, 16)}...
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: '#9ca3af' }}>No transactions yet</p>
          )}
        </div>
      </div>

      {/* How to Earn Tokens */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title">💡 How to Earn More Tokens</h3>
        </div>
        <div className="card-content">
          <div className="dashboard-grid">
            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💧</div>
              <strong>Drip Irrigation</strong>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem' }}>+20 tokens</p>
            </div>
            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌱</div>
              <strong>Organic Farming</strong>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem' }}>+15 tokens</p>
            </div>
            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>☀️</div>
              <strong>Solar Pump</strong>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem' }}>+30 tokens</p>
            </div>
            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌧️</div>
              <strong>Rainwater Harvesting</strong>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem' }}>+25 tokens</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BlockchainView;
