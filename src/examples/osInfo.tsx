import puter from '@heyputer/puter.js'
import { useState } from 'react'

const getErrorMessage = (error: unknown) => error instanceof Error ? error.message : String(error)
const formatJSON = (data: Record<string, unknown>) => JSON.stringify(data, null, 2)

export const OSExample = () => {
  const [status, setStatus] = useState<string>('Idle')
  const [userInfo, setUserInfo] = useState<Record<string, unknown> | null>(null)
  const [versionInfo, setVersionInfo] = useState<Record<string, unknown> | null>(null)

  const fetchUser = async () => {
    setStatus('Fetching user...')
    try {
      const user = await puter.os.user()
      setUserInfo(user)
      setStatus('User info loaded')
    } catch (error) {
      setStatus(`User lookup failed: ${getErrorMessage(error)}`)
    }
  }

  const fetchVersion = async () => {
    setStatus('Fetching version...')
    try {
      const version = await puter.os.version()
      setVersionInfo(version)
      setStatus('Version loaded')
    } catch (error) {
      setStatus(`Version lookup failed: ${getErrorMessage(error)}`)
    }
  }

  return (
    <section className="card stack">
      <div className="stack">
        <h2>Puter OS</h2>
        <p>Fetches the current user and OS version metadata from Puter.</p>
      </div>

      <div className="actions">
        <button onClick={fetchUser}>Get current user</button>
        <button onClick={fetchVersion}>Get OS version</button>
      </div>

      <p className="status">Status: {status}</p>

      {userInfo ? (
        <div className="callout">
          <strong>User info</strong>
          <pre>{formatJSON(userInfo)}</pre>
        </div>
      ) : null}

      {versionInfo ? (
        <div className="callout">
          <strong>Version info</strong>
          <pre>{formatJSON(versionInfo)}</pre>
        </div>
      ) : null}
    </section>
  )
}
