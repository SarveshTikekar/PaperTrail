import React, { useState } from 'react';
import { UploadCloud, FileImage, X, Layers } from 'lucide-react';
import './Dropzone.css';

export default function Dropzone({ onFilesAccepted }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const validateAndProcessFiles = (newFiles) => {
    setError(null);
    if (!newFiles || newFiles.length === 0) return;
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    const validList = Array.from(newFiles).filter(file => validTypes.includes(file.type));
    
    if (validList.length !== newFiles.length) {
      setError('Some files were rejected. Please upload valid JPG, PNG, or PDF files.');
    }

    if (validList.length > 0) {
      const merged = [...files, ...validList];
      setFiles(merged);
      if (onFilesAccepted) onFilesAccepted(merged);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    validateAndProcessFiles(e.dataTransfer.files);
  };

  const handleChange = (e) => {
    validateAndProcessFiles(e.target.files);
  };

  const removeFile = (indexToRemove) => {
    const updated = files.filter((_, idx) => idx !== indexToRemove);
    setFiles(updated);
    if (onFilesAccepted) onFilesAccepted(updated.length > 0 ? updated : null);
  };

  if (files.length > 0) {
    return (
      <div className="preview-container glass-panel animate-fade-in">
        <div className="flex-between" style={{ marginBottom: '16px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Layers className="text-muted" size={20} />
                {files.length} Document{files.length > 1 ? 's' : ''} Queued
            </h3>
            <label htmlFor="fileInputAdd" className="btn-secondary" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
               Add More
            </label>
        </div>
        
        <input 
          type="file" 
          id="fileInputAdd" 
          className="hidden-input" 
          accept="image/jpeg, image/png, image/jpg, application/pdf"
          onChange={handleChange}
          multiple
        />

        <div className="file-list">
          {files.map((file, idx) => (
            <div key={idx} className="file-list-item glass-panel flex-between" style={{ padding: '12px 16px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <FileImage size={24} className="text-secondary" />
                  <div>
                    <span style={{ fontWeight: 600, display: 'block', fontSize: '0.9rem' }}>{file.name}</span>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
              </div>
              <button 
                onClick={() => removeFile(idx)} 
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
                className="hover-danger"
              >
                <X size={20} />
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input 
        type="file" 
        id="fileInput" 
        className="hidden-input" 
        accept="image/jpeg, image/png, image/jpg, application/pdf"
        onChange={handleChange}
        multiple
      />
      
      <UploadCloud size={48} className={`drop-icon ${isDragActive ? 'active' : ''}`} />
      
      <h3>{isDragActive ? "Drop your files here" : "Drag & Drop your form images"}</h3>
      <p className="text-muted">Supports Batch Upload. JPG and PNG up to 10MB.</p>
      
      {error && <p className="error-text">{error}</p>}
      
      <label htmlFor="fileInput" className="btn-primary" style={{ marginTop: '20px' }}>
        Select Files
      </label>
    </div>
  );
}
