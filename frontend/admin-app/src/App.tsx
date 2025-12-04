import ActivityFeed from './components/ActivityFeed'
import Header from './components/Header'
import InventoryHealth from './components/InventoryHealth'
import SalesPerformance from './components/SalesPerformance'
import Sidebar from './components/Sidebar'
import SummaryCards from './components/SummaryCards'
import TaskBoard from './components/TaskBoard'

function App() {
  return (
    <div className="shell">
      <Sidebar />
      <main className="main">
        <Header />
        <div className="grid">
          <SummaryCards />
          <SalesPerformance />
          <InventoryHealth />
          <TaskBoard />
          <ActivityFeed />
        </div>
      </main>
    </div>
  )
}

export default App
