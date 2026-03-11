import { useState, useEffect } from 'react'
import axios from 'axios'

const MOCK_LEADERBOARD_SAMPLE = Array.from({ length: 20 }, (_, i) => ({
  rank: i + 1,
  user_id: `user_${String(i + 1).padStart(3, '0')}`,
  display_name: [
    'Marcus Aurelius', 'Epictetus', 'Seneca', 'Cato the Elder', 'Zeno of Citium',
    'Cleanthes', 'Chrysippus', 'Musonius Rufus', 'Cicero', 'Scipio Africanus',
    'Laelius Sapiens', 'Panaetius', 'Posidonius', 'Antipater', 'Diogenes of Babylon',
    'Aristo', 'Boethus', 'Mnesarchus', 'Dardanus', 'Antipater of Tyre',
  ][i],
  total_score: Math.floor(400 - i * 12 + Math.random() * 8),
  virtues: {
    sophia: Math.floor(70 + Math.random() * 30 - i * 1.2),
    andreia: Math.floor(65 + Math.random() * 30 - i * 1.1),
    dikaiosyne: Math.floor(72 + Math.random() * 28 - i * 1.3),
    sophrosyne: Math.floor(68 + Math.random() * 30 - i * 1.0),
  },
}))

const VIRTUES = ['sophia', 'andreia', 'dikaiosyne', 'sophrosyne']
const PAGE_SIZES = [10, 25, 50]

function LeaderboardView() {
  const [entries, setEntries] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [limit, setLimit] = useState(10)
  const [offset, setOffset] = useState(0)
  const [sortBy, setSortBy] = useState('total_score')

  useEffect(() => {
    setLoading(true)
    axios
      .get(`/api/cnota/leaderboard?limit=${limit}&offset=${offset}`)
      .then((res) => {
        setEntries(res.data.entries || res.data)
        setTotal(res.data.total || MOCK_LEADERBOARD.length)
      })
      .catch(() => {
        const sorted = [...MOCK_LEADERBOARD_SAMPLE].sort((a, b) => {
          if (sortBy === 'total_score') return b.total_score - a.total_score
          return b.virtues[sortBy] - a.virtues[sortBy]
        })
        setEntries(sorted.slice(offset, offset + limit))
        setTotal(MOCK_LEADERBOARD_SAMPLE.length)
      })
      .finally(() => setLoading(false))
  }, [limit, offset, sortBy])

  const totalPages = Math.ceil(total / limit)
  const currentPage = Math.floor(offset / limit)

  return (
    <div className="leaderboard">
      <div className="leaderboard-header">
        <h2>Virtue Leaderboard</h2>
        <div className="leaderboard-controls">
          <label className="control-label">
            Sort by:
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setOffset(0) }}
              className="control-select"
            >
              <option value="total_score">Total Score</option>
              {VIRTUES.map((v) => (
                <option key={v} value={v}>
                  {v.charAt(0).toUpperCase() + v.slice(1)}
                </option>
              ))}
            </select>
          </label>
          <label className="control-label">
            Per page:
            <select
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0) }}
              className="control-select"
            >
              {PAGE_SIZES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading leaderboard…</div>
      ) : (
        <div className="leaderboard-table-wrapper">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Citizen</th>
                <th>Total</th>
                <th>Sophia</th>
                <th>Andreia</th>
                <th>Dikaiosyne</th>
                <th>Sophrosyne</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.user_id} className={entry.rank <= 3 ? 'top-three' : ''}>
                  <td className="rank-cell">
                    {entry.rank <= 3 ? (
                      <span className={`rank-medal rank-${entry.rank}`}>
                        {['🥇', '🥈', '🥉'][entry.rank - 1]}
                      </span>
                    ) : (
                      <span className="rank-num">#{entry.rank}</span>
                    )}
                  </td>
                  <td className="user-cell">
                    <div className="user-name">{entry.display_name}</div>
                    <div className="user-id">{entry.user_id}</div>
                  </td>
                  <td className="score-cell total">{entry.total_score}</td>
                  {VIRTUES.map((v) => (
                    <td key={v} className="score-cell">
                      <span className={`virtue-score-badge ${sortBy === v ? 'active' : ''}`}>
                        {entry.virtues[v]}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button
          className="page-btn"
          onClick={() => setOffset(Math.max(0, offset - limit))}
          disabled={offset === 0}
        >
          ‹ Prev
        </button>
        <span className="page-info">
          Page {currentPage + 1} of {totalPages}
        </span>
        <button
          className="page-btn"
          onClick={() => setOffset(offset + limit)}
          disabled={offset + limit >= total}
        >
          Next ›
        </button>
      </div>

      <style>{`
        .leaderboard { display: flex; flex-direction: column; gap: 1.5rem; }
        .loading { color: var(--text-secondary); text-align: center; padding: 3rem; font-family: 'Cinzel', serif; }
        .leaderboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
        }
        .leaderboard-header h2 { font-size: 1.1rem; color: var(--gold); }
        .leaderboard-controls { display: flex; gap: 1rem; }
        .control-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: var(--text-muted);
          font-family: 'Cinzel', serif;
        }
        .control-select {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          color: var(--text-primary);
          padding: 0.3rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        .leaderboard-table-wrapper {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          overflow: hidden;
        }
        .leaderboard-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.85rem;
        }
        .leaderboard-table th {
          background: var(--bg-secondary);
          color: var(--gold);
          font-family: 'Cinzel', serif;
          font-size: 0.75rem;
          padding: 0.75rem 1rem;
          text-align: left;
          border-bottom: 1px solid var(--border-gold);
          letter-spacing: 0.05em;
        }
        .leaderboard-table td {
          padding: 0.75rem 1rem;
          border-bottom: 1px solid var(--border);
          color: var(--text-primary);
        }
        .leaderboard-table tr:last-child td { border-bottom: none; }
        .leaderboard-table tr:hover td { background: rgba(201, 168, 76, 0.05); }
        .top-three td { background: rgba(201, 168, 76, 0.03); }
        .rank-cell { width: 60px; }
        .rank-medal { font-size: 1.2rem; }
        .rank-num { color: var(--text-muted); font-family: monospace; }
        .user-name { font-weight: 500; color: var(--text-primary); }
        .user-id { font-size: 0.7rem; color: var(--text-muted); font-family: monospace; }
        .score-cell { text-align: center; }
        .score-cell.total { font-weight: 700; color: var(--gold); font-size: 0.95rem; }
        .virtue-score-badge {
          display: inline-block;
          padding: 0.15rem 0.4rem;
          border-radius: 3px;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        .virtue-score-badge.active {
          background: rgba(201, 168, 76, 0.15);
          color: var(--gold);
          border: 1px solid var(--gold-dark);
        }
        .pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 1rem;
        }
        .page-btn {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          color: var(--gold);
          padding: 0.5rem 1rem;
          border-radius: 6px;
          font-size: 0.85rem;
          transition: all 0.2s ease;
        }
        .page-btn:hover:not(:disabled) {
          background: var(--bg-secondary);
          border-color: var(--gold);
        }
        .page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .page-info { color: var(--text-muted); font-size: 0.85rem; }
      `}</style>
    </div>
  )
}

export default LeaderboardView
