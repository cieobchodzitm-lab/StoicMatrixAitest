import puter from '@heyputer/puter.js'
import { useEffect, useState } from 'react'


const getTestCounter = async () => {
  const counter = await puter.kv.get<number>("testCounter");
  return counter || 0;
}

const incrementCounter = async () => {
  return await puter.kv.incr("testCounter", 1);
}

const decrementCounter = async () => {
  return await puter.kv.decr("testCounter", 1);
}

export const KVExample = () => {

  const [localCount, setLocalCount] = useState<number | undefined>();
  useEffect(() => {
    getTestCounter().then(setLocalCount)
  }, [])

  const incrementCount = async () => {
    setLocalCount(count => (count || 0) + 1);
    await incrementCounter();
  }

  const decrementCount = async () => {
    setLocalCount(count => (count || 0) - 1);
    await decrementCounter();
  }

  return (
    <section className="card stack">
      <div className="stack">
        <h2>Puter KV Store</h2>
        <a href="https://docs.puter.com/KV/" target="_blank" rel="noreferrer">KV documentation</a>
      </div>
      <div className="counter-row">
        <button disabled={localCount === undefined} onClick={decrementCount}>
          -
        </button>
        <span className="counter-value">
          {localCount !== undefined ? localCount : 'loading...'}
        </span>
        <button disabled={localCount === undefined} onClick={incrementCount}>
          +
        </button>
      </div>
      <p className="status">
        This counter is stored in Puter KV as <code>testCounter</code>.
      </p>
    </section>
  )
}
