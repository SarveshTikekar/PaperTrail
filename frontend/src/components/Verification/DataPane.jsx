import React from 'react';
import { AlertTriangle, CheckCircle, HelpCircle, Save, Info } from 'lucide-react';

export default function DataPane({ data, onFieldFocus }) {
  
  // Mocking a duplicate detection flag for Phase 7
  const isDuplicateDetected = true;
  
  const getConfidenceIcon = (conf) => {
    if (conf === 'high') return <CheckCircle size={18} color="var(--conf-high)" />;
    if (conf === 'medium') return <AlertTriangle size={18} color="var(--conf-medium)" />;
    return <HelpCircle size={18} color="var(--conf-low)" />;
  };

  const getConfidenceClass = (conf) => {
    return `conf-${conf}`;
  };

  return (
    <div className="data-pane-inner animate-fade-in">
      {isDuplicateDetected && (
        <div style={{
          padding: '16px',
          background: 'var(--conf-low-bg)',
          border: '1px solid var(--conf-low)',
          borderRadius: '8px',
          marginBottom: '24px',
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-start'
        }}>
          <AlertTriangle color="var(--conf-low)" size={24} style={{ flexShrink: 0 }} />
          <div>
            <h4 style={{ color: 'var(--conf-low)', margin: '0 0 4px 0', fontSize: '0.95rem' }}>Potential Duplicate Detected</h4>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              A record with a matching Name and Date of Birth already exists. Please review carefully before confirming.
            </p>
          </div>
        </div>
      )}

      <div className="confidence-legend flex-between" style={{ marginBottom: '24px', padding: '12px', background: 'rgba(0,0,0,0.03)', borderRadius: '8px' }}>
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', fontWeight: 600 }}>
          <span style={{ color: 'var(--conf-high)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: 8, height: 8, background: 'var(--conf-high)', borderRadius: '50%' }}></span> High
          </span>
          <span style={{ color: 'var(--conf-medium)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: 8, height: 8, background: 'var(--conf-medium)', borderRadius: '50%' }}></span> Medium
          </span>
          <span style={{ color: 'var(--conf-low)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: 8, height: 8, background: 'var(--conf-low)', borderRadius: '50%' }}></span> Low
          </span>
        </div>
      </div>

      <form onSubmit={(e) => e.preventDefault()}>
        {data.map((field) => (
          <div className="field-group" key={field.id}>
            <label className="field-label">{field.label}</label>
            <div className="editable-input-container">
              <input 
                type="text" 
                defaultValue={field.value} 
                className={`editable-input ${getConfidenceClass(field.confidence)}`}
                onFocus={() => onFieldFocus(field.id)}
                onBlur={() => onFieldFocus(null)}
              />
              <div className="conf-icon-wrapper" title={`Confidence: ${field.confidence}`}>
                {getConfidenceIcon(field.confidence)}
              </div>
            </div>
            
            {/* Before vs After comparison UI placeholder (Phase 5) */}
            <div style={{ fontSize: '0.75rem', marginTop: '6px', color: 'var(--text-secondary)' }}>
              OCR Parsed: <span style={{ fontFamily: 'monospace' }}>{field.originalOCR}</span>
            </div>
          </div>
        ))}

        <div style={{ marginTop: '40px', borderTop: '1px solid var(--border-subtle)', paddingTop: '24px' }}>
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <button 
                    className="btn-secondary" 
                    style={{ flex: 1, backgroundColor: '#dc3545', color: 'white', border: 'none' }}
                    onClick={() => alert('Document rejected. This will be flagged for manual review.')}
                >
                    <AlertTriangle size={18} style={{ marginRight: '8px' }} /> Reject Document
                </button>
                <button 
                    className="btn-secondary" 
                    style={{ flex: 1, backgroundColor: '#ffc107', color: '#212529', border: 'none' }}
                    onClick={() => alert('Re-scan requested. Document will be sent back for re-processing.')}
                >
                    <Info size={18} style={{ marginRight: '8px' }} /> Request Re-scan
                </button>
            </div>
            
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <select 
                    style={{ 
                        flex: 1, 
                        padding: '8px 12px', 
                        border: '1px solid var(--border-subtle)', 
                        borderRadius: '4px',
                        backgroundColor: 'var(--bg-primary)',
                        color: 'var(--text-primary)'
                    }}
                    defaultValue=""
                >
                    <option value="" disabled>Report Issue</option>
                    <option value="wrong_scan">Wrong Document Scanned</option>
                    <option value="poor_quality">Poor Image Quality</option>
                    <option value="wrong_orientation">Wrong Orientation</option>
                    <option value="missing_pages">Missing Pages</option>
                    <option value="blurry_text">Blurry/Unreadable Text</option>
                    <option value="other">Other Issue</option>
                </select>
                <button 
                    className="btn-secondary" 
                    style={{ padding: '8px 16px' }}
                    onClick={() => alert('Issue reported. Document will be flagged for review.')}
                >
                    Report Issue
                </button>
            </div>
            
            <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              <Save size={18} /> Confirm & Submit Form
            </button>
        </div>
      </form>
    </div>
  );
}
