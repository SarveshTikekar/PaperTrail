import React from 'react';
import FormList from '../components/Dashboard/FormList';
import { Upload, CheckCircle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  return (
    <div className="animate-fade-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="flex-between" style={{ marginBottom: '32px' }}>
        <div>
          <h1>Dashboard</h1>
          <p className="text-muted" style={{ marginTop: '8px' }}>
            Welcome back. You have 1 document <span className="text-gradient">pending verification</span>.
          </p>
        </div>
        
        <Link to="/upload" className="btn-primary" style={{ textDecoration: 'none' }}>
          <Upload size={18} /> New Upload
        </Link>
      </div>

      {/* Quick Stats Row */}
      <div className="stats-row">
        <div className="glass-panel" style={{ flex: 1, padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '12px', color: 'var(--text-primary)' }}>
            <Upload size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.8rem', margin: '0' }}>142</h3>
            <span className="text-muted" style={{ fontSize: '0.9rem' }}>Total Processed</span>
          </div>
        </div>

        <div className="glass-panel" style={{ flex: 1, padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', background: 'var(--conf-medium-bg)', borderRadius: '12px', color: 'var(--conf-medium)' }}>
            <Clock size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.8rem', margin: '0' }}>1</h3>
            <span className="text-muted" style={{ fontSize: '0.9rem' }}>Needs Review</span>
          </div>
        </div>

        <div className="glass-panel" style={{ flex: 1, padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', background: 'var(--conf-high-bg)', borderRadius: '12px', color: 'var(--conf-high)' }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.8rem', margin: '0' }}>141</h3>
            <span className="text-muted" style={{ fontSize: '0.9rem' }}>Successfully Verified</span>
          </div>
        </div>
      </div>

      <FormList />
    </div>
  );
}
