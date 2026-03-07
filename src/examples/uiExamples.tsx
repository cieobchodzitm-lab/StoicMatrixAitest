import puter from '@heyputer/puter.js'
import { useState } from 'react'

const getErrorMessage = (error: unknown) => error instanceof Error ? error.message : String(error)

export const UIExample = () => {
  const [lastResult, setLastResult] = useState<string>('No UI actions yet')

  const openFile = async () => {
    try {
      const result = await puter.ui.showOpenFilePicker({ multiple: false })
      const file = Array.isArray(result) ? result[0] : result
      setLastResult(file ? `Selected file: ${file.name || file.path || 'unknown'}` : 'No file selected')
    } catch (error) {
      setLastResult(`File picker failed: ${getErrorMessage(error)}`)
    }
  }

  return (
    <section className="card stack">
      <div className="stack">
        <h2>Puter UI</h2>
        <p>Single-file picker example using <code>puter.ui.showOpenFilePicker</code>.</p>
      </div>

      <div className="actions">
        <button onClick={openFile}>Open file picker</button>
      </div>

      <div className="callout">
        <strong>Last UI result</strong>
        <p>{lastResult}</p>
      </div>
    </section>
  )
}
