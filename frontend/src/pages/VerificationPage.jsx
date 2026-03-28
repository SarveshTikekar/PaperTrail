import React, { useState } from 'react';
import DualPaneLayout from '../components/Verification/DualPaneLayout';
import { useLanguage } from '../context/LanguageContext';
import { FileCheck, AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react';

export default function VerificationPage() {
  const { t } = useLanguage();
  const [documentStatus, setDocumentStatus] = useState('pending');
  
  const mockExtractedData = [
    { id: 'field_name', label: 'Full Name', value: 'JOHNATHAN SMITH', originalOCR: 'JOHMATHAN SMITH', confidence: 'medium' },
    { id: 'field_dob', label: 'Date of Birth', value: '1985-11-23', originalOCR: '1985-11-23', confidence: 'high' },
    { id: 'field_address', label: 'Home Address', value: '123 Fake Street, CA 90210', originalOCR: '123 Fake Street, CA 9O210', confidence: 'low' },
    { id: 'field_id_number', label: 'ID Number', value: 'AB-123-456', originalOCR: 'AB-123-456', confidence: 'high' }
  ];

  const getStatusConfig = (status) => {
    switch (status) {
      case 'approved': return { icon: <CheckCircle size={14} />, text: 'Approved', color: 'var(--conf-high)', bg: 'var(--conf-high-bg)' };
      case 'rejected': return { icon: <XCircle size={14} />, text: 'Rejected', color: 'var(--conf-low)', bg: 'var(--conf-low-bg)' };
      case 'flagged': return { icon: <AlertTriangle size={14} />, text: 'Flagged', color: 'var(--conf-medium)', bg: 'var(--conf-medium-bg)' };
      default: return { icon: <Clock size={14} />, text: 'Pending Review', color: 'var(--text-secondary)', bg: 'var(--bg-tertiary)' };
    }
  };

  const statusCfg = getStatusConfig(documentStatus);

  return (
    <div className="animate-fade-in" style={{ height: '100%' }}>
      <div className="flex-between" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ 
            padding: '8px', 
            background: 'var(--accent-subtle)', 
            borderRadius: 'var(--radius-md)', 
            color: 'var(--accent-primary)',
            display: 'flex'
          }}>
            <FileCheck size={18} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.35rem', margin: 0 }}>
              Record <span className="mono" style={{ color: 'var(--text-secondary)' }}>REC-1042</span>
            </h1>
          </div>
          {/* Status badge */}
          <div style={{ 
            display: 'flex', alignItems: 'center', gap: '5px',
            padding: '4px 10px', borderRadius: '6px',
            background: statusCfg.bg, color: statusCfg.color,
            fontSize: '0.75rem', fontWeight: 600
          }}>
            {statusCfg.icon} {statusCfg.text}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="text-muted text-xs">{t('docType')}</span>
          <select 
            className="btn-secondary"
            style={{ 
              background: 'var(--bg-tertiary)', 
              cursor: 'pointer',
              fontSize: '0.82rem',
              fontFamily: 'var(--font-sans)',
              color: 'var(--text-primary)',
              fontWeight: 600
            }}
          >
            <option>Driving License</option>
            <option>Tax Form W-9</option>
            <option>Invoice</option>
            <option>Certificate Application</option>
          </select>
        </div>
      </div>
      
      {/* Document Quality Alert — kept from main, restyled */}
      <div style={{
        padding: '12px 14px',
        background: 'var(--conf-low-bg)',
        border: '1px solid rgba(239, 68, 68, 0.2)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '16px',
        display: 'flex',
        gap: '10px',
        alignItems: 'flex-start'
      }}>
        <AlertTriangle color="var(--conf-low)" size={18} style={{ flexShrink: 0, marginTop: '1px' }} />
        <div>
          <h4 style={{ color: 'var(--conf-low)', margin: '0 0 2px 0', fontSize: '0.85rem' }}>Document Quality Issues Detected</h4>
          <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            This document appears to have scanning issues. Review carefully and use the reject or re-scan options if needed.
          </p>
        </div>
      </div>
      
      <DualPaneLayout initialData={mockExtractedData} />
    </div>
  );
}
