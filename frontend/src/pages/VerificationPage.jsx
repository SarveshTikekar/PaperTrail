import React from 'react';
import DualPaneLayout from '../components/Verification/DualPaneLayout';
import { useLanguage } from '../context/LanguageContext';
import { FileCheck } from 'lucide-react';

export default function VerificationPage() {
  const { t } = useLanguage();
  
  const mockExtractedData = [
    { id: 'field_name', label: 'Full Name', value: 'JOHNATHAN SMITH', originalOCR: 'JOHMATHAN SMITH', confidence: 'medium' },
    { id: 'field_dob', label: 'Date of Birth', value: '1985-11-23', originalOCR: '1985-11-23', confidence: 'high' },
    { id: 'field_address', label: 'Home Address', value: '123 Fake Street, CA 90210', originalOCR: '123 Fake Street, CA 9O210', confidence: 'low' },
    { id: 'field_id_number', label: 'ID Number', value: 'AB-123-456', originalOCR: 'AB-123-456', confidence: 'high' }
  ];

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
      
      <DualPaneLayout initialData={mockExtractedData} />
    </div>
  );
}
