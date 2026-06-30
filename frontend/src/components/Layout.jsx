import React, { useState, useEffect, useRef } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, Clock, Database, Sun, Moon, Filter, ChevronDown } from 'lucide-react';

const Layout = () => {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [eraFilter, setEraFilter] = useState('All'); // 'All', 'Crisis', 'Stable'
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const filterOptions = [
    { value: 'All', label: 'All Years' },
    { value: 'Crisis', label: 'Crisis Years Only' },
    { value: 'Stable', label: 'Stable Years Only' }
  ];

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Cinematic Macro</h2>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end>
            <LayoutDashboard size={20} />
            <span style={{ marginLeft: '10px' }}>Executive Snapshot</span>
          </NavLink>
          <NavLink to="/macro" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            <TrendingUp size={20} />
            <span style={{ marginLeft: '10px' }}>Macro & Crisis</span>
          </NavLink>
          <NavLink to="/structural" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            <Clock size={20} />
            <span style={{ marginLeft: '10px' }}>Structural & Runtime</span>
          </NavLink>
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-right" style={{ display: 'flex', alignItems: 'center' }}>

            <div className="custom-dropdown-container" ref={dropdownRef}>
              <button
                className="custom-dropdown-button"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                aria-label="Filter Era"
              >
                <Filter size={16} color={eraFilter !== 'All' ? 'var(--color-teal)' : 'var(--text-secondary)'} />
                {filterOptions.find(opt => opt.value === eraFilter)?.label || 'All Years'}
                <ChevronDown size={16} color="var(--text-secondary)" style={{ marginLeft: '4px', transform: dropdownOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s' }} />
              </button>

              {dropdownOpen && (
                <div className="custom-dropdown-menu">
                  {filterOptions.map(option => (
                    <div
                      key={option.value}
                      className={`custom-dropdown-item ${eraFilter === option.value ? 'active' : ''}`}
                      onClick={() => {
                        setEraFilter(option.value);
                        setDropdownOpen(false);
                      }}
                    >
                      {option.label}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle Theme">
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
        </header>
        <div className="page-wrapper">
          <Outlet context={{ eraFilter }} />
        </div>
      </main>
    </div>
  );
};

export default Layout;
