import { useState } from 'react'
import { SalePanel } from './components/SalePanel'
import './style.css'

function App() {
  const [status, setStatus] = useState('Aberto')

  return (
    <div className="app">
      <header className="app__header">
        <h1>PDV Desktop</h1>
        <span>Caixa: {status}</span>
      </header>
      <main>
        <SalePanel onStatusChange={setStatus} />
      </main>
    </div>
  )
}

export default App
