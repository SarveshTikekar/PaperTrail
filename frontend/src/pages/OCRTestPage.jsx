import React from 'react';
import axios from 'axios';
import { FlaskConical, Loader2, CheckCircle2, AlertTriangle, FileJson, FileSearch } from 'lucide-react';

const FORM_TYPES = [
  { value: 'pan_49a', label: 'PAN Card - Form 49A' },
  { value: 'voter_6', label: 'Voter ID - Form 6' },
];

const RECOMMENDED_METHOD = 'ollama_vision';

export default function OCRTestPage() {
  const [file, setFile] = React.useState(null);
  const [formType, setFormType] = React.useState('pan_49a');
  const [methods, setMethods] = React.useState([]);
  const [extractionMethod, setExtractionMethod] = React.useState('ollama_vision');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [result, setResult] = React.useState(null);

  React.useEffect(() => {
    const loadMethods = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/lab/methods/');
        const available = response.data || [];
        setMethods(available);
        const preferred = [RECOMMENDED_METHOD, 'minicpm_vision', 'local_ocr'].find(
          (slug) => available.some((method) => method.slug === slug && method.is_enabled)
        );
        if (preferred) {
          setExtractionMethod(preferred);
        }
      } catch (err) {
        setError(err?.message || 'Could not load OCR methods.');
      }
    };
    loadMethods();
  }, []);

  const selectedMethod = methods.find((method) => method.slug === extractionMethod);

  const handleSubmit = async () => {
    if (!file) {
      setError('Please choose an image first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('form_type', formType);
      formData.append('extraction_method', extractionMethod);
      const response = await axios.post('http://127.0.0.1:8000/api/lab/ocr-test/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'OCR test failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1320px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
        <div
          style={{
            width: '44px',
            height: '44px',
            display: 'grid',
            placeItems: 'center',
            borderRadius: '12px',
            background: 'var(--accent-subtle)',
            color: 'var(--accent-primary)',
          }}
        >
          <FlaskConical size={20} />
        </div>
        <div>
          <h1 style={{ margin: 0 }}>OCR Test Bench</h1>
          <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
            Upload one image, choose a model, and inspect raw OCR text plus parsed field output without saving a record.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px minmax(0, 1fr)', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '18px' }}>
          <h3 style={{ marginBottom: '14px' }}>Test Settings</h3>

          <div style={{ display: 'grid', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Form Type</div>
              <div style={{ display: 'grid', gap: '8px' }}>
                {FORM_TYPES.map((item) => (
                  <label key={item.value} className={`form-type-option ${formType === item.value ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      className="visually-hidden"
                      checked={formType === item.value}
                      onChange={() => setFormType(item.value)}
                    />
                    <div className="form-type-radio" />
                    <div>
                      <span className="form-type-name">{item.label}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>OCR Method</div>
              <div style={{ display: 'grid', gap: '8px' }}>
                {methods.map((method) => (
                  <label
                    key={method.slug}
                    className={`form-type-option ${extractionMethod === method.slug ? 'selected' : ''}`}
                    style={{ opacity: method.is_enabled ? 1 : 0.55 }}
                  >
                    <input
                      type="radio"
                      className="visually-hidden"
                      checked={extractionMethod === method.slug}
                      onChange={() => setExtractionMethod(method.slug)}
                      disabled={!method.is_enabled}
                    />
                    <div className="form-type-radio" />
                    <div>
                      <span className="form-type-name" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span>{method.name}</span>
                        {method.slug === RECOMMENDED_METHOD ? (
                          <span
                            style={{
                              fontSize: '0.64rem',
                              fontWeight: 700,
                              padding: '2px 8px',
                              borderRadius: '999px',
                              background: 'var(--accent-subtle)',
                              color: 'var(--accent-primary)',
                            }}
                          >
                            Recommended
                          </span>
                        ) : null}
                      </span>
                      <span className="form-type-lang">{method.description}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>Image</div>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '10px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-tertiary)',
                  color: 'var(--text-primary)',
                }}
              />
              {file ? (
                <div style={{ marginTop: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {file.name} - {(file.size / 1024).toFixed(1)} KB
                </div>
              ) : null}
            </div>

            {selectedMethod ? (
              <div
                style={{
                  padding: '12px',
                  borderRadius: '10px',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                }}
              >
                <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>{selectedMethod.name}</div>
                <div>{selectedMethod.description}</div>
              </div>
            ) : null}

            <button className="btn-primary" onClick={handleSubmit} disabled={loading || !file} style={{ justifyContent: 'center', width: '100%' }}>
              {loading ? (
                <>
                  <Loader2 size={16} className="icon-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  Running OCR Test
                </>
              ) : (
                <>
                  <FlaskConical size={16} />
                  Run OCR Test
                </>
              )}
            </button>

            {error ? (
              <div
                style={{
                  display: 'flex',
                  gap: '8px',
                  alignItems: 'flex-start',
                  padding: '12px',
                  borderRadius: '10px',
                  background: 'var(--conf-low-bg)',
                  border: '1px solid rgba(220, 38, 38, 0.18)',
                  color: 'var(--conf-low)',
                }}
              >
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '0.8rem' }}>{error}</div>
              </div>
            ) : null}
          </div>
        </div>

        <div style={{ display: 'grid', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <FileSearch size={16} />
              <h3 style={{ margin: 0 }}>Raw OCR Output</h3>
              {result ? (
                <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {result.extraction_method}
                </span>
              ) : null}
            </div>
            <pre
              style={{
                margin: 0,
                minHeight: '240px',
                maxHeight: '360px',
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                padding: '14px',
                borderRadius: '12px',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                fontSize: '0.78rem',
                lineHeight: 1.55,
              }}
            >
              {result?.raw_text || 'Run a test to inspect the raw OCR text here.'}
            </pre>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <CheckCircle2 size={16} />
                <h3 style={{ margin: 0 }}>Parsed Fields</h3>
              </div>
              <pre
                style={{
                  margin: 0,
                  minHeight: '320px',
                  maxHeight: '420px',
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  padding: '14px',
                  borderRadius: '12px',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.76rem',
                  lineHeight: 1.5,
                }}
              >
                {result ? JSON.stringify(result.parsed_values, null, 2) : 'Parsed field values will appear here.'}
              </pre>
            </div>

            <div className="glass-panel" style={{ padding: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <FileJson size={16} />
                <h3 style={{ margin: 0 }}>Notes and Debug</h3>
              </div>
              <pre
                style={{
                  margin: 0,
                  minHeight: '320px',
                  maxHeight: '420px',
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  padding: '14px',
                  borderRadius: '12px',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.76rem',
                  lineHeight: 1.5,
                }}
              >
                {result ? JSON.stringify({ notes: result.notes, debug: result.debug }, null, 2) : 'Notes and debug payload will appear here.'}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
