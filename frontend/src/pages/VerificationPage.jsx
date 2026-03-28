import React, { useState } from 'react';
import DualPaneLayout from '../components/Verification/DualPaneLayout';
import { useLanguage } from '../context/LanguageContext';
import { AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react';

export default function VerificationPage() {
  const { t } = useLanguage();
  const [documentStatus, setDocumentStatus] = useState('pending'); // pending, approved, rejected, flagged
  
  // Mock data for demonstration purposes
  const mockExtractedData = [
    { id: 'field_name', label: 'Full Name', value: 'JOHNATHAN SMITH', originalOCR: 'JOHMATHAN SMITH', confidence: 'medium' },
    { id: 'field_dob', label: 'Date of Birth', value: '1985-11-23', originalOCR: '1985-11-23', confidence: 'high' },
    { id: 'field_address', label: 'Home Address', value: '123 Fake Street, CA 90210', originalOCR: '123 Fake Street, CA 9O210', confidence: 'low' },
    { id: 'field_id_number', label: 'ID Number', value: 'AB-123-456', originalOCR: 'AB-123-456', confidence: 'high' }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle color="#28a745" size={20} />;
      case 'rejected': return <XCircle color="#dc3545" size={20} />;
      case 'flagged': return <AlertTriangle color="#ffc107" size={20} />;
      default: return <Clock color="#6c757d" size={20} />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved': return 'Approved';
      case 'rejected': return 'Rejected';
      case 'flagged': return 'Flagged for Review';
      default: return 'Pending Review';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return '#28a745';
      case 'rejected': return '#dc3545';
      case 'flagged': return '#ffc107';
      default: return '#6c757d';
    }
  };

  return (
    <div className="animate-fade-in" style={{ height: '100%' }}>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
         <div>
             <h1 style={{ fontSize: '1.75rem', margin: '0 0 8px 0' }}>Record: <span style={{ fontFamily: 'monospace' }}>REC-1042</span></h1>
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
               {getStatusIcon(documentStatus)}
               <span style={{ 
                 color: getStatusColor(documentStatus), 
                 fontWeight: '600', 
                 fontSize: '0.9rem' 
               }}>
                 {getStatusText(documentStatus)}
               </span>
             </div>
         </div>
         <div style={{ display: 'flex', alignItems: 'center', gap: '16px', background: 'var(--bg-secondary)', padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
             <span className="text-muted" style={{ fontSize: '0.85rem' }}>{t('docType')}:</span>
             <select style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontWeight: '600', cursor: 'pointer' }}>
                 <option>Driving License</option>
                 <option>Tax Form W-9</option>
                 <option>Invoice</option>
                 <option>Certificate Application</option>
             </select>
             <button className="btn-secondary" style={{ padding: '4px 12px', fontSize: '0.8rem' }}>{t('overrideType')}</button>
         </div>
      </div>
      
      {/* Document Issues Alert */}
      <div style={{
        padding: '16px',
        background: 'var(--conf-low-bg)',
        border: '1px solid var(--conf-low)',
        borderRadius: '8px',
        marginBottom: '20px',
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-start'
      }}>
        <AlertTriangle color="var(--conf-low)" size={24} style={{ flexShrink: 0 }} />
        <div>
          <h4 style={{ color: 'var(--conf-low)', margin: '0 0 4px 0', fontSize: '0.95rem' }}>Document Quality Issues Detected</h4>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            This document appears to have scanning issues. Please review carefully and use the reject or re-scan options if the quality is unacceptable.
          </p>
        </div>
      </div>
      
      <DualPaneLayout initialData={mockExtractedData} />
    </div>
  );
}
