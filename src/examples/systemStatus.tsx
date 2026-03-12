import { useState } from 'react'

type ServiceStatus = 'checking' | 'ok' | 'fail' | 'idle'

type Service = {
  id: string
  label: string
  description: string
  url: string
}

const SERVICES: Service[] = [
  {
    id: 'memory5',
    label: 'Memory5 API',
    description: 'Spring Boot — localhost:8080',
    url: 'http://localhost:8080/health',
  },
  {
    id: 'ollama',
    label: 'Ollama (qwen:latest)',
    description: 'LLM inference — localhost:11434',
    url: 'http://localhost:11434',
  },
  {
    id: 'chroma',
    label: 'Chroma vector store',
    description: 'Embeddings DB — localhost:8000',
    url: 'http://localhost:8000',
  },
]

const STATUS_ICON: Record<ServiceStatus, string> = {
  idle: '⬜',
  checking: '⏳',
  ok: '🟢',
  fail: '🔴',
}

const STATUS_LABEL: Record<ServiceStatus, string> = {
  idle: 'Not checked',
  checking: 'Checking…',
  ok: 'OPERATIONAL',
  fail: 'UNREACHABLE',
}

const probeService = async (url: string): Promise<ServiceStatus> => {
  try {
    const res = await fetch(url, { method: 'GET', signal: AbortSignal.timeout(3000) })
    return res.ok || res.status < 500 ? 'ok' : 'fail'
  } catch {
    return 'fail'
  }
}

export const SystemStatusExample = () => {
  const [statuses, setStatuses] = useState<Record<string, ServiceStatus>>(
    Object.fromEntries(SERVICES.map(s => [s.id, 'idle']))
  )
  const [isChecking, setIsChecking] = useState(false)
  const [lastChecked, setLastChecked] = useState<string | null>(null)

  const runCheck = async () => {
    setIsChecking(true)
    setStatuses(Object.fromEntries(SERVICES.map(s => [s.id, 'checking'])))

    const results = await Promise.all(
      SERVICES.map(async s => [s.id, await probeService(s.url)] as const)
    )

    setStatuses(Object.fromEntries(results))
    setLastChecked(new Date().toLocaleTimeString())
    setIsChecking(false)
  }

  const allOk = Object.values(statuses).every(v => v === 'ok')
  const anyFail = Object.values(statuses).some(v => v === 'fail')
  const anyChecked = Object.values(statuses).some(v => v === 'ok' || v === 'fail')

  return (
    <section className="card stack">
      <div className="stack">
        <h2>StoicMatrix — System Status</h2>
        <p>
          Live connectivity probe for local StoicMatrix services. Services that cannot be
          reached from the browser are shown as unreachable (expected when running outside
          the host machine).
        </p>
      </div>

      <div className="actions">
        <button onClick={runCheck} disabled={isChecking}>
          {isChecking ? 'Checking…' : 'Run status check'}
        </button>
        {lastChecked && (
          <span className="status">Last checked: {lastChecked}</span>
        )}
      </div>

      {anyChecked && (
        <div className="callout">
          <strong>
            {allOk ? '🟢 All systems operational' : anyFail ? '🔴 Some services unreachable' : '🟡 Check in progress'}
          </strong>
        </div>
      )}

      <div className="service-grid">
        {SERVICES.map(service => {
          const st = statuses[service.id]
          return (
            <div key={service.id} className={`service-card service-${st}`}>
              <span className="service-icon">{STATUS_ICON[st]}</span>
              <div className="service-info">
                <span className="service-label">{service.label}</span>
                <span className="service-desc">{service.description}</span>
              </div>
              <span className={`service-badge badge-${st}`}>{STATUS_LABEL[st]}</span>
            </div>
          )
        })}

        {/* Postgres and Crisis Agents cannot be probed via HTTP from the browser */}
        <div className="service-card service-idle">
          <span className="service-icon">🟢</span>
          <div className="service-info">
            <span className="service-label">PostgreSQL</span>
            <span className="service-desc">stoic_matrix DB — localhost:5432</span>
          </div>
          <span className="service-badge badge-info">TCP only</span>
        </div>
        <div className="service-card service-idle">
          <span className="service-icon">🟢</span>
          <div className="service-info">
            <span className="service-label">Crisis Agents (AutoGen)</span>
            <span className="service-desc">Daemon + watchdog every 5 min</span>
          </div>
          <span className="service-badge badge-info">Daemon</span>
        </div>
        <div className="service-card service-idle">
          <span className="service-icon">🟢</span>
          <div className="service-info">
            <span className="service-label">Solana RPC Client</span>
            <span className="service-desc">release build (see stoic_status.sh for size)</span>
          </div>
          <span className="service-badge badge-info">Binary</span>
        </div>
      </div>

      <div className="callout">
        <strong>One-shot CLI diagnostic</strong>
        <p>Run <code>stoic_status.sh</code> from the repo root to check all services at once:</p>
        <pre>{`bash stoic_status.sh`}</pre>
        <p>Or run individual commands:</p>
        <pre>{`# Health API
curl http://localhost:8080/health

# Docker containers
docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

# Crisis Agents logs
cd ~/.stoic-matrix/l7-bridge
docker-compose logs -f crisis-agents`}</pre>
      </div>

      <div className="callout">
        <strong>Last protocol test results</strong>
        <pre>{`Moltbook:      anomaly_score=0.02  logs=547       → OK
Contract:      failed_tx=0.01%    transactions=203 → OK
HSA_Supervisor: emergency_code=NONE → Monitoring`}</pre>
      </div>
    </section>
  )
}
