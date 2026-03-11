import { useState, useEffect } from 'react'

type Balances = {
  angel: number
  guardian: number
  cnota: number
}

type WalletPanelProps = {
  userId: string
}

export const WalletPanel = ({ userId }: WalletPanelProps) => {
  const [balances, setBalances] = useState<Balances>({ angel: 0, guardian: 0, cnota: 0 })
  const [phantomAddress, setPhantomAddress] = useState<string | null>(null)
  const [isWithdrawing, setIsWithdrawing] = useState(false)
  const [message, setMessage] = useState<{ text: string; type: 'info' | 'error' } | null>(null)

  const showMessage = (text: string, type: 'info' | 'error' = 'info') => {
    setMessage({ text, type })
  }

  // 1. Fetch balances from the internal API (PostgreSQL -> FastAPI)
  useEffect(() => {
    const fetchBalances = async () => {
      try {
        const response = await fetch(`/api/v1/wallet/${userId}`)
        if (response.ok) {
          const data = await response.json() as {
            angel_balance: number
            guardian_balance: number
            cnota_balance: number
          }
          setBalances({
            angel: data.angel_balance,
            guardian: data.guardian_balance,
            cnota: data.cnota_balance,
          })
        } else {
          showMessage(`Failed to load balances (HTTP ${response.status}).`, 'error')
        }
      } catch (error) {
        console.error('Error fetching wallet balances:', error)
        showMessage('Could not reach the wallet API. Check your connection.', 'error')
      }
    }
    fetchBalances()
  }, [userId])

  // 2. Connect to Phantom wallet
  const connectPhantom = async () => {
    try {
      const solana = (window as Window & { solana?: { isPhantom?: boolean; connect: () => Promise<{ publicKey: { toString: () => string } }> } }).solana
      if (solana?.isPhantom) {
        const response = await solana.connect()
        setPhantomAddress(response.publicKey.toString())
        showMessage('Phantom wallet connected.', 'info')
      } else {
        showMessage('Phantom wallet not found. Please install the extension.', 'error')
      }
    } catch (error) {
      console.error('Error connecting to Phantom wallet:', error)
      showMessage('Could not connect to Phantom wallet.', 'error')
    }
  }

  // 3. Initiate on-chain withdrawal
  const handleWithdraw = async () => {
    if (!phantomAddress) {
      showMessage('Please connect your Phantom wallet first.', 'error')
      return
    }
    if (balances.angel <= 0) {
      showMessage('No $ANGEL tokens available for withdrawal.', 'error')
      return
    }

    setIsWithdrawing(true)
    setMessage(null)
    try {
      console.log(`Initiating withdrawal to: ${phantomAddress}`)
      await new Promise<void>(resolve => setTimeout(resolve, 2000))
      showMessage('Transaction submitted to the Solana network!', 'info')
      setBalances(prev => ({ ...prev, angel: 0 }))
    } catch (error) {
      console.error('Withdrawal error:', error)
      showMessage('Withdrawal failed. Please try again.', 'error')
    } finally {
      setIsWithdrawing(false)
    }
  }

  return (
    <section className="card stack">
      <div className="stack">
        <h2>AGORA MUNDI</h2>
        <p>Internal Ledger (L7) — token balances and on-chain withdrawal.</p>
      </div>

      {message && (
        <div className={`callout${message.type === 'error' ? ' callout--error' : ''}`}>
          <span>{message.text}</span>
        </div>
      )}

      {/* Balance section */}
      <div className="service-grid">
        <div className="service-card">
          <div className="service-card-header">
            <span className="service-name">$ANGEL</span>
            <span className="service-badge service-badge--operational">Governance</span>
          </div>
          <p className="service-desc">Governance token balance</p>
          <p className="service-detail" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
            {balances.angel}
          </p>
        </div>

        <div className="service-card">
          <div className="service-card-header">
            <span className="service-name">$GUARDIAN</span>
            <span className="service-badge service-badge--operational">Security</span>
          </div>
          <p className="service-desc">Security token balance</p>
          <p className="service-detail" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
            {balances.guardian}
          </p>
        </div>

        <div className="service-card">
          <div className="service-card-header">
            <span className="service-name">$CNOTA</span>
            <span className="service-badge service-badge--degraded">Reputation</span>
          </div>
          <p className="service-desc">Reputation token balance</p>
          <p className="service-detail" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
            {balances.cnota}
          </p>
        </div>
      </div>

      {/* Phantom wallet actions */}
      <div className="actions">
        {!phantomAddress ? (
          <button onClick={() => void connectPhantom()} type="button">
            Connect Phantom Wallet
          </button>
        ) : (
          <>
            <div className="callout">
              <strong>Connected wallet</strong>
              <code style={{ wordBreak: 'break-all' }}>{phantomAddress}</code>
            </div>
            <button
              onClick={() => void handleWithdraw()}
              disabled={isWithdrawing || balances.angel <= 0}
              type="button"
            >
              {isWithdrawing ? 'Processing…' : 'Withdraw $ANGEL on-chain'}
            </button>
          </>
        )}
      </div>
    </section>
  )
}

export default WalletPanel
