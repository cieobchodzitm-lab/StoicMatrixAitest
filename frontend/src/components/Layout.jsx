import { NavLink } from 'react-router-dom'
import '../App.css'

const navItems = [
  { path: '/', label: 'Dashboard', icon: '⚖️' },
  { path: '/passport', label: 'Passport', icon: '🏛️' },
  { path: '/leaderboard', label: 'Leaderboard', icon: '📜' },
]

function Layout({ children }) {
  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h2>L7 CNOTA</h2>
          <span>Virtue Governance Dashboard</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ path, label, icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="main-content">
        <header className="top-header">
          <h1>Rzeczpospolita Stoicka</h1>
          <span className="header-badge">⚡ Live</span>
        </header>
        <main className="page-content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
