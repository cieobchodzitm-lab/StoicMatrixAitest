import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './components/Dashboard.jsx'
import PassportView from './components/PassportView.jsx'
import LeaderboardView from './components/LeaderboardView.jsx'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/passport" element={<PassportView />} />
          <Route path="/leaderboard" element={<LeaderboardView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
