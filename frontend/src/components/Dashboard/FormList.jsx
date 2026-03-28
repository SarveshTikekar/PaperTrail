import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import './FormList.css';

const mockData = [
  { id: 'REC-1042', filename: 'bank_statement_march.png', date: '2023-10-24 14:32', status: 'pending' },
  { id: 'REC-1041', filename: 'driving_license_front.jpg', date: '2023-10-24 09:15', status: 'verified' },
  { id: 'REC-1040', filename: 'invoice_apple_store.pdf', date: '2023-10-23 18:45', status: 'verified' },
  { id: 'REC-1039', filename: 'w9_form_contractor.png', date: '2023-10-23 11:20', status: 'processing' },
];

export default function FormList() {
  const navigate = useNavigate();

  return (
    <div className="form-list-wrapper glass-panel">
      <div className="form-list-header">
        <h3>Recent Uploads</h3>
        <span className="text-muted">Manage and verify your documents</span>
      </div>
      
      <div className="table-responsive">
        <table className="form-table">
          <thead>
            <tr>
              <th>Document ID</th>
              <th>File Info</th>
              <th>Upload Date</th>
              <th>Status</th>
              <th className="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {mockData.map((row) => (
              <tr 
                key={row.id} 
                className="table-row"
                onClick={() => {
                  if (row.status !== 'processing') navigate('/verify');
                }}
              >
                <td>
                  <span className="doc-id">{row.id}</span>
                </td>
                <td>
                  <div className="file-info">
                    <div className="file-icon-bg">
                      <FileText size={16} className="file-icon" />
                    </div>
                    <span className="filename">{row.filename}</span>
                  </div>
                </td>
                <td className="text-muted">{row.date}</td>
                <td>
                  <StatusBadge status={row.status} />
                </td>
                <td className="text-right">
                  <button 
                    className="action-btn"
                    disabled={row.status === 'processing'}
                    title={row.status === 'processing' ? 'Processing...' : 'Review Document'}
                  >
                    {row.status === 'verified' ? 'View' : 'Review'} <ChevronRight size={16} />
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
