import React from 'react';
import DualPaneLayout from '../components/Verification/DualPaneLayout';
import { useLanguage } from '../context/LanguageContext';

export default function VerificationPage() {
  const { t } = useLanguage();
  
  // Mock data for demonstration purposes
  const mockExtractedData = [
    { id: 'field_name', label: 'Full Name', value: 'JOHNATHAN SMITH', originalOCR: 'JOHMATHAN SMITH', confidence: 'medium' },
    { id: 'field_dob', label: 'Date of Birth', value: '1985-11-23', originalOCR: '1985-11-23', confidence: 'high' },
    { id: 'field_address', label: 'Home Address', value: '123 Fake Street, CA 90210', originalOCR: '123 Fake Street, CA 9O210', confidence: 'low' },
    { id: 'field_id_number', label: 'ID Number', value: 'AB-123-456', originalOCR: 'AB-123-456', confidence: 'high' }
  ];

  return (
    <div className="animate-fade-in" style={{ height: '100%' }}>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
         <div>
             <h1 style={{ fontSize: '1.75rem', margin: '0 0 8px 0' }}>Record: <span style={{ fontFamily: 'monospace' }}>REC-1042</span></h1>
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
      
      <DualPaneLayout initialData={mockExtractedData} />
    </div>
  );
}
