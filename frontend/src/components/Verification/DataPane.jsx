import React from 'react';
import { AlertTriangle, CheckCircle, HelpCircle, Save, Info, RotateCw } from 'lucide-react';

export default function DataPane({ data, onFieldFocus }) {
  
  const isDuplicateDetected = true;
  
  const getConfidenceIcon = (conf) => {
    if (conf === 'high') return <CheckCircle size={16} color="var(--conf-high)" />;
    if (conf === 'medium') return <AlertTriangle size={16} color="var(--conf-medium)" />;
    return <HelpCircle size={16} color="var(--conf-low)" />;
  };

  const getConfidenceClass = (conf) => `conf-${conf}`;

  return (
    <div className="data-pane-inner animate-fade-in">
      {isDuplicateDetected && (
        <div style={{
          padding: '12px 14px',
          background: 'var(--conf-low-bg)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-start'
        }}>
          <AlertTriangle color="var(--conf-low)" size={18} style={{ flexShrink: 0, marginTop: '1px' }} />
          <div>
            <h4 style={{ color: 'var(--conf-low)', margin: '0 0 2px 0', fontSize: '0.85rem' }}>
              Potential Duplicate Detected
            </h4>
            <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              A record with a matching Name and Date of Birth already exists. Review carefully before confirming.
            </p>
          </div>
        </div>
      )}

      <div className="confidence-legend">
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.72rem', fontWeight: 600 }}>
          <span style={{ color: 'var(--conf-high)', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--conf-high)', borderRadius: '50%', display: 'inline-block' }} /> High
          </span>
          <span style={{ color: 'var(--conf-medium)', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--conf-medium)', borderRadius: '50%', display: 'inline-block' }} /> Medium
          </span>
          <span style={{ color: 'var(--conf-low)', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--conf-low)', borderRadius: '50%', display: 'inline-block' }} /> Low
          </span>
        </div>
      </div>

      <form onSubmit={(e) => e.preventDefault()}>
        <div className="stagger-children">
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
              
              <div style={{ fontSize: '0.72rem', marginTop: '5px', color: 'var(--text-tertiary)', display: 'flex', gap: '4px', alignItems: 'center' }}>
                <Info size={11} /> 
                OCR: <span className="mono">{field.originalOCR}</span>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
          {/* Action buttons from main — restyled */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
            <button 
              className="btn-secondary" 
              style={{ flex: 1, color: 'var(--conf-low)', borderColor: 'rgba(239, 68, 68, 0.3)', fontSize: '0.82rem', justifyContent: 'center' }}
              onClick={() => alert('Document rejected. This will be flagged for manual review.')}
            >
              <AlertTriangle size={14} /> Reject
            </button>
            <button 
              className="btn-secondary" 
              style={{ flex: 1, color: 'var(--conf-medium)', borderColor: 'rgba(245, 158, 11, 0.3)', fontSize: '0.82rem', justifyContent: 'center' }}
              onClick={() => alert('Re-scan requested. Document will be sent back for re-processing.')}
            >
              <RotateCw size={14} /> Re-scan
            </button>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginBottom: '14px' }}>
            <select 
              style={{ 
                flex: 1, 
                padding: '8px 12px', 
                border: '1px solid var(--border-subtle)', 
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-primary)',
                color: 'var(--text-primary)',
                fontSize: '0.82rem',
                fontFamily: 'var(--font-sans)'
              }}
              defaultValue=""
            >
              <option value="" disabled>Report Issue...</option>
              <option value="wrong_scan">Wrong Document Scanned</option>
              <option value="poor_quality">Poor Image Quality</option>
              <option value="wrong_orientation">Wrong Orientation</option>
              <option value="missing_pages">Missing Pages</option>
              <option value="blurry_text">Blurry/Unreadable Text</option>
              <option value="other">Other Issue</option>
            </select>
            <button 
              className="btn-ghost" 
              style={{ fontSize: '0.82rem' }}
              onClick={() => alert('Issue reported. Document will be flagged for review.')}
            >
              Report
            </button>
          </div>

          <button className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '11px' }}>
            <Save size={15} /> Confirm & Submit Form
          </button>
        </div>
      </form>
    </div>
  );
}
