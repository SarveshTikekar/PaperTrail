import React, { useState } from 'react';
import axios from 'axios';
import { useLanguage } from '../context/LanguageContext';
import { Upload, FileText, ChevronRight, Loader2, CheckCircle, AlertCircle, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { saveRecord } from '../utils/records';
import './UploadPage.css';

const FORM_TYPES = [
  { value: 'pan_49a', label: 'PAN Card — Form 49A', lang: 'English' },
  { value: 'voter_6', label: 'Voter ID — Form 6', lang: 'Hindi + English' },
];

const STEPS = ['Select Form', 'Upload Image', 'Processing', 'Results'];

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [formType, setFormType] = useState('pan_49a');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const { t } = useLanguage();

  const currentStep = result ? 3 : loading ? 2 : file ? 1 : 0;

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) setFile(dropped);
  };

  const handleSubmit = async () => {
    if (!file) return setError('Please select a file first');
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('form_type', formType);

      const response = await axios.post('http://127.0.0.1:8000/api/lab/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const storedRecord = saveRecord(response.data);
      setResult(storedRecord);
    } catch (err) {
      setError(err?.response?.data?.error || err?.response?.data?.detail || err.message || 'OCR processing failed');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="upload-page animate-fade-in">
      <div className="upload-header">
        <div>
          <h1>{t('uploadDoc')}</h1>
          <p className="text-muted text-sm" style={{ marginTop: '4px' }}>
            {t('uploadDesc')}
          </p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="step-indicator">
        {STEPS.map((step, i) => (
          <div key={step} className={`step-dot ${i <= currentStep ? 'active' : ''} ${i < currentStep ? 'done' : ''}`}>
            <div className="step-circle">
              {i < currentStep ? <CheckCircle size={14} /> : <span>{i + 1}</span>}
            </div>
            <span className="step-text">{step}</span>
            {i < STEPS.length - 1 && <div className="step-line" />}
          </div>
        ))}
      </div>

      <div className="upload-grid">
        {/* Left: Form Config */}
        <div className="upload-config glass-panel">
          <h3 style={{ marginBottom: '16px' }}>Form Template</h3>
          <div className="form-type-list">
            {FORM_TYPES.map((ft) => (
              <label 
                key={ft.value} 
                className={`form-type-option ${formType === ft.value ? 'selected' : ''}`}
              >
                <input 
                  type="radio" 
                  name="formType" 
                  value={ft.value} 
                  checked={formType === ft.value}
                  onChange={() => setFormType(ft.value)}
                  className="visually-hidden"
                />
                <div className="form-type-radio" />
                <div>
                  <span className="form-type-name">{ft.label}</span>
                  <span className="form-type-lang">{ft.lang}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Right: Upload Area */}
        <div className="upload-area glass-panel">
          {result ? (
            <div className="result-container animate-fade-in">
              <div className="result-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className="result-icon-success">
                    <CheckCircle size={20} />
                  </div>
                  <div>
                    <h3 style={{ margin: 0 }}>Extraction Complete</h3>
                    <p className="text-muted text-xs" style={{ margin: 0 }}>{file?.name}</p>
                  </div>
                </div>
                <button onClick={resetForm} className="btn-ghost">
                  <X size={15} /> New Upload
                </button>
              </div>
              <div className="result-body">
                <pre className="result-json">{JSON.stringify(result, null, 2)}</pre>
                <button
                  onClick={() => navigate(`/verify?id=${encodeURIComponent(result.id)}`)}
                  className="btn-primary"
                  style={{ marginTop: '14px', width: '100%', justifyContent: 'center' }}
                >
                  Review Extracted Data
                </button>
              </div>
            </div>
          ) : (
            <>
              <div 
                className={`drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
                onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
                onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="fileInput"
                  accept="image/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  style={{ display: 'none' }}
                />

                {file ? (
                  <div className="file-preview animate-scale-in">
                    <div className="file-preview-icon">
                      <FileText size={28} />
                    </div>
                    <div className="file-preview-info">
                      <span className="file-preview-name">{file.name}</span>
                      <span className="file-preview-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setFile(null); }} 
                      className="btn-ghost"
                      style={{ color: 'var(--conf-low)' }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <label htmlFor="fileInput" className="drop-zone-content">
                    <div className="drop-zone-icon">
                      <Upload size={28} />
                    </div>
                    <h4 style={{ margin: '12px 0 4px' }}>
                      {dragActive ? 'Drop your file here' : 'Drag & drop your form image'}
                    </h4>
                    <p className="text-muted text-xs">JPG, PNG up to 10MB</p>
                  </label>
                )}
              </div>

              {error && (
                <div className="upload-error animate-fade-in">
                  <AlertCircle size={15} />
                  {error}
                </div>
              )}

              <button 
                onClick={handleSubmit} 
                className="btn-primary"
                disabled={!file || loading}
                style={{ width: '100%', justifyContent: 'center', marginTop: '16px', padding: '12px' }}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="icon-spin" style={{ animation: 'spin 1s linear infinite' }} /> 
                    Processing...
                  </>
                ) : (
                  <>
                    <ChevronRight size={16} />
                    Start Extraction
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
