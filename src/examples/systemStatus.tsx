import { useState, useCallback } from 'react'

type ServiceStatus = 'operational' | 'degraded' | 'down' | 'unknown'

type Service = {
  name: string
  description: string
  port: number | null
  status: ServiceStatus
  detail: string
}

type CrisisReport = {
  moltbook: { anomalyScore: number; logs: number; anomalies: boolean }
  contract: { failedTxPct: number; transactions: number; exploitPatterns: boolean }
  hsa: { emergencyCode: string; recommendation: string }
  timestamp: string
}

const STATUS_ICON: Record<ServiceStatus, string> = {
  operational: '🟢',
  degraded: '🟡',
  down: '🔴',
  unknown: '⚪',
}

const STATUS_LABEL: Record<ServiceStatus, string> = {
  operational: 'OPERATIONAL',
  degraded: 'DEGRADED',
  down: 'DOWN',
  unknown: 'UNKNOWN',
}

const INITIAL_SERVICES: Service[] = [
  {
    name: 'Memory5 API',
    description: 'Spring Boot – primary memory & inference gateway',
    port: 8080,
    status: 'operational',
    detail: 'Health endpoint responding at /health',
  },
  {
    name: 'PostgreSQL',
    description: 'Database stoic_matrix',
    port: 5432,
    status: 'operational',
    detail: 'Accepting connections on port 5432',
  },
  {
    name: 'Ollama (qwen:latest)',
    description: 'Local LLM inference engine',
    port: 11434,
    status: 'operational',
    detail: 'Model qwen:latest loaded and ready',
  },
  {
    name: 'Chroma',
    description: 'Vector store for embeddings',
    port: 8000,
    status: 'operational',
    detail: 'Returning valid responses on port 8000',
  },
  {
    name: 'Crisis Agents',
    description: 'AutoGen daemon – watchdog every 5 min',
    port: null,
    status: 'operational',
    detail: 'Running in daemon mode, watchdog active',
  },
  {
    name: 'Solana RPC Client',
    description: 'Rust release binary (~42.3 MB)',
    port: null,
    status: 'operational',
    detail: 'Built in release mode, binary ready',
  },
]

const LAST_CRISIS_REPORT: CrisisReport = {
  moltbook: { anomalyScore: 0.02, logs: 547, anomalies: false },
  contract: { failedTxPct: 0.01, transactions: 203, exploitPatterns: false },
  hsa: { emergencyCode: 'NONE', recommendation: 'Continue monitoring' },
  timestamp: new Date().toISOString(),
}

const DIAGNOSTIC_COMMANDS = `# Health check
curl http://localhost:8080/health

# Running containers
docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

# Crisis agent logs
cd ~/.stoic-matrix/l7-bridge
docker-compose logs -f crisis-agents`

export const SystemStatusExample = () => {
  const [services] = useState<Service[]>(INITIAL_SERVICES)
  const [report] = useState<CrisisReport>(LAST_CRISIS_REPORT)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<string>(new Date().toLocaleTimeString())

  const refresh = useCallback(async () => {
    setIsRefreshing(true)
    // Simulate a brief async check cycle
    await new Promise<void>(resolve => setTimeout(resolve, 800))
    setLastRefresh(new Date().toLocaleTimeString())
    setIsRefreshing(false)
  }, [])

  const allOperational = services.every(s => s.status === 'operational')

  return (
    <section className="card stack">
      <div className="status-header">
        <div className="stack">
          <h2>StoicMatrix System Status</h2>
          <p>Live overview of all StoicMatrix AI infrastructure services.</p>
        </div>
        <div className="status-actions">
          <span className="status">Last refresh: {lastRefresh}</span>
          <button onClick={refresh} disabled={isRefreshing}>
            {isRefreshing ? 'Checking…' : '↻ Refresh'}
          </button>
        </div>
      </div>

      <div className={`status-banner ${allOperational ? 'status-banner--ok' : 'status-banner--warn'}`}>
        {allOperational
          ? '🟢 All systems operational'
          : '🟡 One or more services require attention'}
      </div>

      <div className="service-grid">
        {services.map(svc => (
          <div key={svc.name} className="service-card">
            <div className="service-card-header">
              <span className="service-name">{svc.name}</span>
              <span className={`service-badge service-badge--${svc.status}`}>
                {STATUS_ICON[svc.status]} {STATUS_LABEL[svc.status]}
              </span>
            </div>
            <p className="service-desc">{svc.description}</p>
            {svc.port !== null && (
              <code className="service-port">:{svc.port}</code>
            )}
            <p className="service-detail">{svc.detail}</p>
          </div>
        ))}
      </div>

      <div className="callout">
        <strong>Last Crisis Protocol Test</strong>
        <p className="status">Run at {new Date(report.timestamp).toLocaleString()}</p>
        <div className="crisis-grid">
          <div className="crisis-item">
            <span className="crisis-label">Moltbook</span>
            <span className={`crisis-value ${report.moltbook.anomalies ? 'crisis-value--alert' : 'crisis-value--ok'}`}>
              {report.moltbook.anomalies ? '🔴 Anomalies detected' : '🟢 No anomalies'}
            </span>
            <span className="crisis-meta">
              {report.moltbook.logs} logs · anomaly score {report.moltbook.anomalyScore.toFixed(2)}
            </span>
          </div>
          <div className="crisis-item">
            <span className="crisis-label">Contract</span>
            <span className={`crisis-value ${report.contract.exploitPatterns ? 'crisis-value--alert' : 'crisis-value--ok'}`}>
              {report.contract.exploitPatterns ? '🔴 Exploit patterns found' : '🟢 No exploit patterns'}
            </span>
            <span className="crisis-meta">
              {report.contract.transactions} transactions · {report.contract.failedTxPct.toFixed(2)}% failed TX
            </span>
          </div>
          <div className="crisis-item">
            <span className="crisis-label">HSA_Supervisor</span>
            <span className={`crisis-value ${report.hsa.emergencyCode !== 'NONE' ? 'crisis-value--alert' : 'crisis-value--ok'}`}>
              {report.hsa.emergencyCode !== 'NONE' ? `🔴 ${report.hsa.emergencyCode}` : '🟢 NONE'}
            </span>
            <span className="crisis-meta">{report.hsa.recommendation}</span>
          </div>
        </div>
      </div>

      <div className="callout">
        <strong>Diagnostic Commands</strong>
        <pre>{DIAGNOSTIC_COMMANDS}</pre>
      </div>
    </section>
  )
}
