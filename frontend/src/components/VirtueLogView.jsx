import { useState, useEffect } from 'react'
import axios from 'axios'

const MOCK_VIRTUE_LOG_ENTRIES = [
  {
    id: 'log_001',
    user_id: 'demo_user_001',
    action: 'governance_vote',
    virtues: { sophia: 81, andreia: 76, dikaiosyne: 88, sophrosyne: 80 },
    total_score: 325,
    created_at: '2026-03-14T10:00:00Z',
  },
  {
    id: 'log_002',
    user_id: 'demo_user_001',
    action: 'proposal_review',
    virtues: { sophia: 79, andreia: 74, dikaiosyne: 84, sophrosyne: 82 },
    total_score: 319,
    created_at: '2026-03-14T08:30:00Z',
  },
]

const MOCK_VIRTUE_LOG_RESPONSE = {
  entries: MOCK_VIRTUE_LOG_ENTRIES,
  total: MOCK_VIRTUE_LOG_ENTRIES.length,
  limit: 10,
  offset: 0,
}

function VirtueLogView() {
  const [payload, setPayload] = useState(MOCK_VIRTUE_LOG_RESPONSE)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios
      .get('/api/virtue_log/list?limit=10&offset=0')
      .then((res) => {
        const entries = Array.isArray(res.data?.entries) ? res.data.entries : []
        setPayload({
          entries,
          total: Number.isFinite(res.data?.total) ? res.data.total : entries.length,
          limit: Number.isFinite(res.data?.limit) ? res.data.limit : 10,
          offset: Number.isFinite(res.data?.offset) ? res.data.offset : 0,
        })
      })
      .catch(() => setPayload(MOCK_VIRTUE_LOG_RESPONSE))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="loading">Loading virtue log...</div>
  }

  if (!payload.entries.length) {
    return (
      <div className="virtue-log">
        <div className="virtue-log-card">
          <h2>Virtue Log</h2>
          <p className="virtue-log-empty">No virtue log entries are available yet.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="virtue-log">
      <div className="virtue-log-card">
        <div className="virtue-log-header">
          <h2>Virtue Log</h2>
          <span className="virtue-log-total">{payload.total} total entries</span>
        </div>

        <div className="virtue-log-table-wrapper">
          <table className="virtue-log-table">
            <thead>
              <tr>
                <th>Entry</th>
                <th>User</th>
                <th>Action</th>
                <th>Sophia</th>
                <th>Andreia</th>
                <th>Dikaiosyne</th>
                <th>Sophrosyne</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {payload.entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.id}</td>
                  <td>{entry.user_id}</td>
                  <td>{entry.action}</td>
                  <td>{entry.virtues?.sophia ?? 0}</td>
                  <td>{entry.virtues?.andreia ?? 0}</td>
                  <td>{entry.virtues?.dikaiosyne ?? 0}</td>
                  <td>{entry.virtues?.sophrosyne ?? 0}</td>
                  <td className="virtue-log-total-cell">{entry.total_score ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .virtue-log { display: flex; flex-direction: column; gap: 1.5rem; }
        .loading { color: var(--text-secondary); text-align: center; padding: 3rem; font-family: 'Cinzel', serif; }
        .virtue-log-card {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          padding: 1.5rem;
        }
        .virtue-log-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .virtue-log-header h2 { color: var(--gold); font-size: 1.1rem; }
        .virtue-log-total { color: var(--text-muted); font-size: 0.85rem; }
        .virtue-log-empty { color: var(--text-secondary); margin: 0; }
        .virtue-log-table-wrapper {
          overflow-x: auto;
          border: 1px solid var(--border);
          border-radius: 6px;
        }
        .virtue-log-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.85rem;
        }
        .virtue-log-table th {
          text-align: left;
          background: var(--bg-secondary);
          color: var(--gold);
          font-family: 'Cinzel', serif;
          font-size: 0.75rem;
          letter-spacing: 0.04em;
          padding: 0.75rem;
          border-bottom: 1px solid var(--border-gold);
        }
        .virtue-log-table td {
          color: var(--text-primary);
          padding: 0.7rem 0.75rem;
          border-bottom: 1px solid var(--border);
        }
        .virtue-log-table tr:last-child td { border-bottom: none; }
        .virtue-log-table tr:hover td { background: rgba(201, 168, 76, 0.05); }
        .virtue-log-total-cell { color: var(--gold); font-weight: 700; }
      `}</style>
    </div>
  )
}

export default VirtueLogView
