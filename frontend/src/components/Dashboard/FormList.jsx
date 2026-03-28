import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import { readRecords } from '../../utils/records';
import './FormList.css';

export default function FormList() {
  const navigate = useNavigate();
  const records = readRecords();

  if (!records.length) {
    return (
      <div className="form-list-wrapper glass-panel">
        <div className="form-list-header">
          <h3>Recent Uploads</h3>
          <span className="text-muted">Your uploaded forms will appear here.</span>
        </div>
        <div style={{ padding: '28px', color: 'var(--text-secondary)' }}>
          No uploaded records yet. Start from the upload page to create a verification record.
        </div>
      </div>
    );
  }

  return (
    <div className="form-list-wrapper glass-panel">
      <div className="form-list-header">
        <h3>Recent Uploads</h3>
        <span className="text-muted">Manage and verify your extracted forms</span>
      </div>

      <div className="table-responsive">
        <table className="form-table">
          <thead>
            <tr>
              <th>Document ID</th>
              <th>Form Type</th>
              <th>Created</th>
              <th>Status</th>
              <th className="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {records.map((row) => (
              <tr
                key={row.id}
                className="table-row"
                onClick={() => navigate(`/verify?id=${encodeURIComponent(row.id)}`)}
              >
                <td>
                  <span className="doc-id">{row.id}</span>
                </td>
                <td>
                  <div className="file-info">
                    <div className="file-icon-bg">
                      <FileText size={16} className="file-icon" />
                    </div>
                    <span className="filename">{row.form_type}</span>
                  </div>
                </td>
                <td className="text-muted">
                  {row.created_at ? new Date(row.created_at).toLocaleString('en-IN') : '-'}
                </td>
                <td>
                  <StatusBadge status={row.status} />
                </td>
                <td className="text-right">
                  <button className="action-btn" title="Review Document">
                    Review <ChevronRight size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
