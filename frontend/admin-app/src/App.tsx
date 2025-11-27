import Dashboard from './components/Dashboard'
import InventoryWidget from './components/InventoryWidget'

function App() {
  return (
    <div className="app">
      <header>
        <h1>Retaguarda / Admin</h1>
      </header>
      <div className="layout">
        <Dashboard />
        <InventoryWidget />
      </div>
    </div>
  )
}

export default App
