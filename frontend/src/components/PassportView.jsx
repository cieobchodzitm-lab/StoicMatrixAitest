import { useState, useEffect } from 'react'
import axios from 'axios'

const MOCK_PASSPORT = {
  token_id: 'L7-NFT-0001',
  user_id: 'demo_user_001',
  display_name: 'Marcus Aurelius',
  virtues: {
    sophia: 87,
    andreia: 74,
    dikaiosyne: 91,
    sophrosyne: 90,
  },
  total_score: 342,
  rank: 3,
  created_at: '2024-01-15T10:30:00Z',
  image_url: null,
}

function PassportView() {
  const [passport, setPassport] = useState(MOCK_PASSPORT)
  const [loading, setLoading] = useState(true)
  const [minting, setMinting] = useState(false)
  const [txStatus, setTxStatus] = useState(null)

  useEffect(() => {
    axios
      .get('/api/passport/demo_user_001')
      .then((res) => setPassport(res.data))
      .catch(() => setPassport(MOCK_PASSPORT))
      .finally(() => setLoading(false))
  }, [])

  const handleMint = async () => {
    setMinting(true)
    setTxStatus(null)
    try {
      const res = await axios.post('/api/passport/mint', {
        user_id: passport.user_id,
      })
      setTxStatus({ success: true, tx_id: res.data.tx_id, status: res.data.status })
    } catch {
      setTxStatus({ success: false, message: 'Mint request queued (mock mode)' })
    } finally {
      setMinting(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading passport data…</div>
  }

  return (
    <div className="passport-view">
      <div className="nft-card">
        <div className="nft-card-header">
          <div className="nft-badge">L7 VIRTUE PASSPORT</div>
          <div className="nft-token-id">{passport.token_id}</div>
        </div>

        <div className="nft-avatar">🏛️</div>

        <div className="nft-name">{passport.display_name}</div>
        <div className="nft-user-id">{passport.user_id}</div>

        <div className="nft-virtues">
          {Object.entries(passport.virtues).map(([key, value]) => (
            <div key={key} className="nft-virtue">
              <span className="nft-virtue-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
              <span className="nft-virtue-value">{value}</span>
            </div>
          ))}
        </div>

        <div className="nft-total">
          <span className="nft-total-label">Total Score</span>
          <span className="nft-total-value">{passport.total_score}</span>
        </div>

        <div className="nft-rank">Rank #{passport.rank}</div>
      </div>

      <div className="passport-actions">
        <div className="passport-meta">
          <h3>Passport Metadata</h3>
          <div className="meta-grid">
            <div className="meta-row">
              <span className="meta-key">Token ID</span>
              <span className="meta-value">{passport.token_id}</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Standard</span>
              <span className="meta-value">ERC-1155</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Chain</span>
              <span className="meta-value">Solana L7 Bridge</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Created</span>
              <span className="meta-value">
                {new Date(passport.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Traits</span>
              <span className="meta-value">{Object.keys(passport.virtues).length} virtues</span>
            </div>
          </div>
        </div>

        <button
          className="mint-btn"
          onClick={handleMint}
          disabled={minting}
        >
          {minting ? '⏳ Processing…' : '⚡ Mint Passport NFT'}
        </button>

        {txStatus && (
          <div className={`tx-status ${txStatus.success ? 'success' : 'info'}`}>
            {txStatus.success ? (
              <>
                <span>✅ Status: {txStatus.status}</span>
                {txStatus.tx_id && (
                  <span className="tx-id">TX: {txStatus.tx_id}</span>
                )}
              </>
            ) : (
              <span>ℹ️ {txStatus.message}</span>
            )}
          </div>
        )}
      </div>

      <style>{`
        .passport-view {
          display: grid;
          grid-template-columns: 340px 1fr;
          gap: 2rem;
          align-items: start;
        }
        .loading { color: var(--text-secondary); text-align: center; padding: 3rem; font-family: 'Cinzel', serif; }
        .nft-card {
          background: linear-gradient(135deg, #1a1a1a 0%, #2a1f0a 50%, #1a1a1a 100%);
          border: 2px solid var(--gold-dark);
          border-radius: 16px;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 0 30px rgba(201, 168, 76, 0.15);
          position: relative;
          overflow: hidden;
        }
        .nft-card::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 3px;
          background: linear-gradient(90deg, transparent, var(--gold), transparent);
        }
        .nft-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        .nft-badge {
          font-family: 'Cinzel', serif;
          font-size: 0.65rem;
          color: var(--gold);
          letter-spacing: 0.1em;
          border: 1px solid var(--gold-dark);
          padding: 0.2rem 0.5rem;
          border-radius: 3px;
        }
        .nft-token-id { font-size: 0.7rem; color: var(--text-muted); font-family: monospace; }
        .nft-avatar { font-size: 4rem; margin: 1rem 0; }
        .nft-name { font-family: 'Cinzel', serif; font-size: 1.25rem; color: var(--gold); margin-bottom: 0.25rem; }
        .nft-user-id { font-size: 0.75rem; color: var(--text-muted); font-family: monospace; margin-bottom: 1.5rem; }
        .nft-virtues {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        .nft-virtue {
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 0.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .nft-virtue-label { font-size: 0.65rem; color: var(--text-muted); font-family: 'Cinzel', serif; }
        .nft-virtue-value { font-size: 1.1rem; color: var(--gold); font-weight: 700; font-family: 'Cinzel', serif; }
        .nft-total {
          background: var(--bg-primary);
          border: 1px solid var(--gold-dark);
          border-radius: 6px;
          padding: 0.75rem;
          margin: 0.5rem 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .nft-total-label { font-size: 0.8rem; color: var(--text-secondary); font-family: 'Cinzel', serif; }
        .nft-total-value { font-size: 1.5rem; color: var(--gold); font-weight: 700; font-family: 'Cinzel', serif; }
        .nft-rank { font-size: 0.8rem; color: var(--text-muted); font-family: 'Cinzel', serif; margin-top: 0.5rem; }
        .passport-actions { display: flex; flex-direction: column; gap: 1.5rem; }
        .passport-meta {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          padding: 1.5rem;
        }
        .passport-meta h3 { font-size: 0.9rem; color: var(--gold); margin-bottom: 1rem; }
        .meta-grid { display: flex; flex-direction: column; gap: 0.5rem; }
        .meta-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
        .meta-row:last-child { border-bottom: none; }
        .meta-key { font-size: 0.8rem; color: var(--text-muted); }
        .meta-value { font-size: 0.8rem; color: var(--text-primary); font-family: monospace; }
        .mint-btn {
          background: linear-gradient(135deg, var(--gold-dark), var(--gold));
          color: var(--bg-primary);
          border: none;
          padding: 1rem 2rem;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 700;
          letter-spacing: 0.05em;
          transition: all 0.2s ease;
          width: 100%;
        }
        .mint-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, var(--gold), var(--gold-light));
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(201, 168, 76, 0.3);
        }
        .mint-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .tx-status {
          padding: 1rem;
          border-radius: 8px;
          font-size: 0.85rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .tx-status.success { background: rgba(76, 175, 122, 0.1); border: 1px solid var(--success); color: var(--success); }
        .tx-status.info { background: rgba(201, 168, 76, 0.1); border: 1px solid var(--gold-dark); color: var(--gold); }
        .tx-id { font-family: monospace; font-size: 0.75rem; }
        @media (max-width: 768px) { .passport-view { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  )
}

export default PassportView
