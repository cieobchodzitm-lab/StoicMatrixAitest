import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js'
import { Radar, Bar } from 'react-chartjs-2'
import axios from 'axios'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
)

const MOCK_PROFILE = {
  user_id: 'demo_user_001',
  display_name: 'Marcus Aurelius',
  rank: 3,
  total_score: 342,
  sophia: 87,
  andreia: 74,
  dikaiosyne: 91,
  sophrosyne: 90,
}

const VIRTUES = [
  { key: 'sophia', label: 'Sophia', description: 'Wisdom' },
  { key: 'andreia', label: 'Andreia', description: 'Courage' },
  { key: 'dikaiosyne', label: 'Dikaiosyne', description: 'Justice' },
  { key: 'sophrosyne', label: 'Sophrosyne', description: 'Temperance' },
]

function Dashboard() {
  const [profile, setProfile] = useState(MOCK_PROFILE)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios
      .get('/api/cnota/profile/demo_user_001')
      .then((res) => setProfile(res.data))
      .catch(() => setProfile(MOCK_PROFILE))
      .finally(() => setLoading(false))
  }, [])

  const radarData = {
    labels: VIRTUES.map((v) => `${v.label}\n(${v.description})`),
    datasets: [
      {
        label: 'Virtue Scores',
        data: VIRTUES.map((v) => profile[v.key]),
        backgroundColor: 'rgba(201, 168, 76, 0.2)',
        borderColor: 'rgba(201, 168, 76, 0.8)',
        pointBackgroundColor: 'rgba(201, 168, 76, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(201, 168, 76, 1)',
        borderWidth: 2,
      },
    ],
  }

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
          color: '#5a4e38',
          backdropColor: 'transparent',
          font: { size: 10 },
        },
        grid: { color: '#2a2a2a' },
        angleLines: { color: '#2a2a2a' },
        pointLabels: {
          color: '#c9a84c',
          font: { family: 'Cinzel', size: 11 },
        },
      },
    },
    plugins: {
      legend: { display: false },
    },
    responsive: true,
    maintainAspectRatio: false,
  }

  const barData = {
    labels: VIRTUES.map((v) => v.label),
    datasets: [
      {
        label: 'Score',
        data: VIRTUES.map((v) => profile[v.key]),
        backgroundColor: [
          'rgba(201, 168, 76, 0.7)',
          'rgba(76, 175, 122, 0.7)',
          'rgba(122, 142, 201, 0.7)',
          'rgba(201, 122, 76, 0.7)',
        ],
        borderColor: [
          'rgba(201, 168, 76, 1)',
          'rgba(76, 175, 122, 1)',
          'rgba(122, 142, 201, 1)',
          'rgba(201, 122, 76, 1)',
        ],
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  }

  const barOptions = {
    scales: {
      x: {
        ticks: { color: '#a89060', font: { family: 'Cinzel', size: 11 } },
        grid: { color: '#2a2a2a' },
      },
      y: {
        min: 0,
        max: 100,
        ticks: { color: '#5a4e38', stepSize: 20 },
        grid: { color: '#2a2a2a' },
      },
    },
    plugins: {
      legend: { display: false },
    },
    responsive: true,
    maintainAspectRatio: false,
  }

  if (loading) {
    return <div className="loading">Loading virtue data…</div>
  }

  return (
    <div className="dashboard">
      <div className="profile-card">
        <div className="profile-avatar">⚖️</div>
        <div className="profile-info">
          <h2>{profile.display_name}</h2>
          <p className="profile-id">{profile.user_id}</p>
          <div className="profile-stats">
            <div className="stat">
              <span className="stat-value">{profile.total_score}</span>
              <span className="stat-label">Total Score</span>
            </div>
            <div className="stat">
              <span className="stat-value">#{profile.rank}</span>
              <span className="stat-label">Rank</span>
            </div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Virtue Radar</h3>
          <div className="chart-wrapper">
            <Radar data={radarData} options={radarOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Individual Scores</h3>
          <div className="chart-wrapper">
            <Bar data={barData} options={barOptions} />
          </div>
        </div>
      </div>

      <div className="virtue-bars">
        <h3>Virtue Progress</h3>
        {VIRTUES.map((v) => (
          <div key={v.key} className="virtue-bar-row">
            <div className="virtue-bar-label">
              <span className="virtue-name">{v.label}</span>
              <span className="virtue-desc">{v.description}</span>
            </div>
            <div className="virtue-bar-track">
              <div
                className="virtue-bar-fill"
                style={{ width: `${profile[v.key]}%` }}
              />
            </div>
            <span className="virtue-score">{profile[v.key]}</span>
          </div>
        ))}
      </div>

      <style>{`
        .dashboard { display: flex; flex-direction: column; gap: 1.5rem; }
        .loading { color: var(--text-secondary); text-align: center; padding: 3rem; font-family: 'Cinzel', serif; }
        .profile-card {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }
        .profile-avatar { font-size: 3rem; }
        .profile-info h2 { font-size: 1.25rem; color: var(--gold); margin-bottom: 0.25rem; }
        .profile-id { font-size: 0.8rem; color: var(--text-muted); font-family: monospace; margin-bottom: 0.75rem; }
        .profile-stats { display: flex; gap: 2rem; }
        .stat { display: flex; flex-direction: column; align-items: center; }
        .stat-value { font-family: 'Cinzel', serif; font-size: 1.5rem; color: var(--gold); font-weight: 700; }
        .stat-label { font-size: 0.75rem; color: var(--text-muted); }
        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .chart-card {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          padding: 1.5rem;
        }
        .chart-card h3 { font-size: 0.9rem; color: var(--gold); margin-bottom: 1rem; }
        .chart-wrapper { height: 280px; }
        .virtue-bars {
          background: var(--bg-card);
          border: 1px solid var(--border-gold);
          border-radius: 8px;
          padding: 1.5rem;
        }
        .virtue-bars h3 { font-size: 0.9rem; color: var(--gold); margin-bottom: 1rem; }
        .virtue-bar-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
        .virtue-bar-label { width: 140px; flex-shrink: 0; }
        .virtue-name { font-family: 'Cinzel', serif; font-size: 0.85rem; color: var(--text-primary); display: block; }
        .virtue-desc { font-size: 0.7rem; color: var(--text-muted); }
        .virtue-bar-track {
          flex: 1;
          height: 8px;
          background: var(--bg-secondary);
          border-radius: 4px;
          overflow: hidden;
          border: 1px solid var(--border);
        }
        .virtue-bar-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--gold-dark), var(--gold));
          border-radius: 4px;
          transition: width 0.5s ease;
        }
        .virtue-score { width: 30px; text-align: right; font-size: 0.85rem; color: var(--gold); font-weight: 500; }
        @media (max-width: 768px) { .charts-grid { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  )
}

export default Dashboard
