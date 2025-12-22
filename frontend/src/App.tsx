import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import AboutProject from './pages/AboutProject';
import DataSources from './pages/DataSources';
import Visualization from './pages/Visualization';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1 className="project-name">Платформа мониторинга цен</h1>
          <nav className="navbar">
            <NavLink
              to="/about"
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              О проекте
            </NavLink>
            <NavLink
              to="/data-sources"
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              Источники данных
            </NavLink>
            <NavLink
              to="/visualization"
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              Визуализация
            </NavLink>
          </nav>
        </header>

        <main className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/about" replace />} />
            <Route path="/about" element={<AboutProject />} />
            <Route path="/data-sources" element={<DataSources />} />
            <Route path="/visualization" element={<Visualization />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App
