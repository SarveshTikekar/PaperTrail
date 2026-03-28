import React from 'react';
import FormList from '../components/Dashboard/FormList';
import { Upload, CheckCircle, Clock, ArrowUpRight, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import '../components/Dashboard/Dashboard.css';

export default function DashboardPage() {
  const now = new Date();
  const greeting = now.getHours() < 12 ? 'Good morning' : now.getHours() < 17 ? 'Good afternoon' : 'Good evening';
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' });

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1060px', margin: '0 auto' }}>
      {/* Header */}
      <div className="flex-between" style={{ marginBottom: '28px' }}>
        <div>
          <h1 style={{ marginBottom: '4px' }}>Dashboard</h1>
          <p className="text-muted text-sm">
            {greeting}. {dateStr} &middot; <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>1 pending</span> verification
          </p>
        </div>
        
        <Link to="/upload" className="btn-primary" style={{ textDecoration: 'none' }}>
          <Upload size={15} /> New Upload
        </Link>
      </div>

      {/* Stats */}
      <div className="stats-row stagger-children">
        <div className="stat-card glass-panel">
          <div className="stat-icon-wrap" style={{ background: 'var(--accent-subtle)', color: 'var(--accent-primary)' }}>
            <Upload size={18} />
          </div>
          <div className="stat-body">
            <span className="stat-value">142</span>
            <span className="stat-label">Total Processed</span>
          </div>
          <div className="stat-trend up">
            <TrendingUp size={12} /> 12%
          </div>
        </div>

        <div className="stat-card glass-panel" style={{ borderColor: 'var(--conf-medium)', borderWidth: '1px' }}>
          <div className="stat-icon-wrap" style={{ background: 'var(--conf-medium-bg)', color: 'var(--conf-medium)' }}>
            <Clock size={18} />
          </div>
          <div className="stat-body">
            <span className="stat-value" style={{ color: 'var(--conf-medium)' }}>1</span>
            <span className="stat-label">Needs Review</span>
          </div>
          <Link to="/verify" className="stat-action" style={{ color: 'var(--conf-medium)' }}>
            Review <ArrowUpRight size={13} />
          </Link>
        </div>

        <div className="stat-card glass-panel">
          <div className="stat-icon-wrap" style={{ background: 'var(--conf-high-bg)', color: 'var(--conf-high)' }}>
            <CheckCircle size={18} />
          </div>
          <div className="stat-body">
            <span className="stat-value">141</span>
            <span className="stat-label">Verified</span>
          </div>
          <div className="stat-trend up" style={{ color: 'var(--conf-high)' }}>
            99.3%
          </div>
        </div>
      </div>

      <FormList />
    </div>
  );
}
