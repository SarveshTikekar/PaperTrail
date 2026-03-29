import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, HelpCircle, Save, FileSearch } from 'lucide-react';

export default function DataPane({ data, onFieldFocus, rawText, documentStatus, onSave }) {
  const [fields, setFields] = useState(data);

  useEffect(() => {
    setFields(data);
  }, [data]);

  const getConfidenceClass = (score) => {
    const val = parseFloat(score || 0);
    if (val >= 0.8) return 'conf-high';
    if (val >= 0.5) return 'conf-medium';
    return 'conf-low';
  };

  const getConfidenceIcon = (score) => {
    const val = parseFloat(score || 0);
    if (val >= 0.8) return <CheckCircle size={14} color="var(--conf-high)" />;
    if (val >= 0.5) return <AlertTriangle size={14} color="var(--conf-medium)" />;
    return <HelpCircle size={14} color="var(--conf-low)" />;
  };

  const normalizeBool = (val) => {
    if (typeof val === 'boolean') return val;
    const str = String(val || '').toLowerCase().trim();
    return ['true', 'yes', '1', 'checked'].includes(str);
  };

  const handleChange = (fieldId, value) => {
    setFields((current) => current.map((field) => (field.id === fieldId ? { ...field, value } : field)));
  };

  return (
    <div className="data-pane-inner animate-fade-in">
      <div
        style={{
          padding: '12px 14px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '18px',
          display: 'flex',
          justifyContent: 'space-between',
          gap: '14px',
          alignItems: 'center',
        }}
      >
        <div>
          <h4 style={{ margin: '0 0 4px 0', fontSize: '0.9rem' }}>Verification Record</h4>
          <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Status: <span className="mono">{documentStatus}</span>
          </p>
        </div>
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
      </div>

      <form onSubmit={(e) => e.preventDefault()}>
        <div className="stagger-children">
          {fields.length ? (
            fields.map((field) => {
              const isBool = typeof field.value === 'boolean' || ['true', 'false'].includes(String(field.value).toLowerCase().trim());
              
              return (
                <div className="field-group" key={field.id}>
                  <label className="field-label">{field.label}</label>
                  <div className="editable-input-container">
                    {isBool ? (
                      <label className={`checkbox-field ${getConfidenceClass(field.confidence)}`}>
                        <input
                          type="checkbox"
                          checked={normalizeBool(field.value)}
                          onChange={(e) => handleChange(field.id, e.target.checked)}
                          onFocus={() => onFieldFocus(field.id)}
                          onBlur={() => onFieldFocus(null)}
                        />
                        <span className="checkbox-text">{normalizeBool(field.value) ? 'Selected / Yes' : 'Not Selected / No'}</span>
                        <div className="conf-dot" style={{ position: 'absolute', top: 10, right: 14 }}>
                           {getConfidenceIcon(field.confidence)}
                        </div>
                      </label>
                    ) : (
                      <>
                        <input
                          type="text"
                          value={field.value}
                          className={`editable-input ${getConfidenceClass(field.confidence)}`}
                          onChange={(e) => handleChange(field.id, e.target.value)}
                          onFocus={() => onFieldFocus(field.id)}
                          onBlur={() => onFieldFocus(null)}
                        />
                        <div className="conf-icon-wrapper" title={`Confidence: ${field.confidence}`}>
                          {getConfidenceIcon(field.confidence)}
                        </div>
                      </>
                    )}
                  </div>

                  <div
                    style={{
                      fontSize: '0.72rem',
                      marginTop: '5px',
                      color: 'var(--text-tertiary)',
                      display: 'flex',
                      gap: '4px',
                      alignItems: 'center',
                    }}
                  >
                    OCR: <span className="mono">{field.originalOCR || '-'}</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div
              style={{
                padding: '18px',
                borderRadius: 'var(--radius-md)',
                border: '1px dashed var(--border-subtle)',
                color: 'var(--text-secondary)',
                textAlign: 'center',
              }}
            >
              No extracted fields available for this record yet.
            </div>
          )}
        </div>

        <div style={{ marginTop: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
          <button
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '11px' }}
            onClick={() => onSave(fields)}
          >
            <Save size={15} /> Save Verification Data
          </button>
        </div>
      </form>

      <div
        style={{
          marginTop: '18px',
          padding: '14px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontWeight: 700 }}>
          <FileSearch size={15} />
          Raw OCR Text
        </div>
        <pre
          style={{
            margin: 0,
            fontSize: '0.76rem',
            lineHeight: 1.5,
            color: 'var(--text-secondary)',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            maxHeight: '220px',
            overflow: 'auto',
          }}
        >
          {rawText || 'No OCR text available.'}
        </pre>
      </div>
    </div>
  );
}
