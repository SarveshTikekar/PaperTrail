import React, { useMemo, useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { AlertTriangle, CheckCircle, Clock, FileCheck } from 'lucide-react';
import DualPaneLayout from '../components/Verification/DualPaneLayout';
import { findRecord, getLatestRecord, updateStoredRecord, saveRecord } from '../utils/records';
import axios from 'axios';

function useSelectedRecord() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const recordId = params.get('id');
  return recordId ? findRecord(recordId) : getLatestRecord();
}

export default function VerificationPage() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const recordId = params.get('id');

  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [savedAt, setSavedAt] = useState('');
  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  React.useEffect(() => {
    const loadRecord = async () => {
      // 1. Try local storage first
      const local = recordId ? findRecord(recordId) : getLatestRecord();
      if (local) {
        setRecord(local);
        return;
      }

      // 2. Fallback to API if ID provided but not in local storage
      if (recordId) {
        setLoading(true);
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/lab/records/${recordId}/`);
          const fetchedRecord = saveRecord(response.data);
          setRecord(fetchedRecord);
        } catch (err) {
          setError(err?.response?.data?.error || 'Record not found on server.');
        } finally {
          setLoading(false);
        }
      }
    };

    loadRecord();
  }, [recordId]);

  const selectedRecord = record;

  const documentStatus = selectedRecord?.status || 'pending';
  
  // Multi-page extraction logic
  const pages = selectedRecord?.pages || [];
  const isMultiPage = pages.length > 1;
  const currentFields = isMultiPage ? pages[currentPageIndex].review_fields : selectedRecord?.review_fields || [];
  const currentRawText = isMultiPage ? pages[currentPageIndex].raw_text : selectedRecord?.raw_text || '';

  const statusCfg = useMemo(() => {
    switch (documentStatus) {
      case 'verified':
        return { icon: <CheckCircle size={14} />, text: 'Verified', color: 'var(--conf-high)', bg: 'var(--conf-high-bg)' };
      case 'flagged':
        return { icon: <AlertTriangle size={14} />, text: 'Flagged', color: 'var(--conf-medium)', bg: 'var(--conf-medium-bg)' };
      default:
        return { icon: <Clock size={14} />, text: 'Pending Review', color: 'var(--text-secondary)', bg: 'var(--bg-tertiary)' };
    }
  }, [documentStatus]);

  const handleSave = (fields) => {
    if (!selectedRecord) return;
    updateStoredRecord(selectedRecord.id, {
      review_fields: fields,
      status: 'verified',
    });
    setSavedAt(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }));
  };

  if (loading) {
    return (
      <div className="flex-center" style={{ height: '70vh', flexDirection: 'column', gap: '12px' }}>
        <div style={{ padding: '20px', borderRadius: '12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
          <div className="icon-spin" style={{ margin: '0 auto 12px auto' }}>
            <Clock size={32} color="var(--accent-primary)" />
          </div>
          <h3 style={{ margin: 0 }}>Fetching Record...</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Retrieving data from PaperTrail backend</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="animate-fade-in" style={{ height: '100%' }}>
        <div className="glass-panel" style={{ padding: '28px', maxWidth: '760px', margin: '0 auto', borderLeft: '4px solid var(--conf-low)' }}>
          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', marginBottom: '12px' }}>
            <AlertTriangle color="var(--conf-low)" size={24} />
            <h2 style={{ margin: 0 }}>Loading Failed</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>{error}</p>
          <button className="btn-primary" onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  if (!selectedRecord) {
    return (
      <div className="animate-fade-in" style={{ height: '100%' }}>
        <div className="glass-panel" style={{ padding: '28px', maxWidth: '760px', margin: '0 auto' }}>
          <h1 style={{ marginTop: 0 }}>Verification</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 0 }}>
            No uploaded record is available yet. Upload a PAN Form 49A or Voter Form 6 first, then open verification from the upload result.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ height: '100%' }}>
      <div className="flex-between" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              padding: '8px',
              background: 'var(--accent-subtle)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--accent-primary)',
              display: 'flex',
            }}
          >
            <FileCheck size={18} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.35rem', margin: 0 }}>
              Record <span className="mono" style={{ color: 'var(--text-secondary)' }}>{selectedRecord.id}</span>
            </h1>
            <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
              {selectedRecord.form_type} • {selectedRecord.extraction_method || 'local_ocr'} {savedAt ? `• saved at ${savedAt}` : ''}
            </p>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 10px',
              borderRadius: '6px',
              background: statusCfg.bg,
              color: statusCfg.color,
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          >
            {statusCfg.icon} {statusCfg.text}
          </div>
        </div>
      </div>

      {selectedRecord.notes?.length ? (
        <div
          style={{
            padding: '12px 14px',
            background: 'var(--conf-medium-bg)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px',
            display: 'flex',
            gap: '10px',
            alignItems: 'flex-start',
          }}
        >
          <AlertTriangle color="var(--conf-medium)" size={18} style={{ flexShrink: 0, marginTop: '1px' }} />
          <div>
            <h4 style={{ color: 'var(--conf-medium)', margin: '0 0 2px 0', fontSize: '0.85rem' }}>OCR Notes</h4>
            <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {selectedRecord.notes.join(' | ')}
            </p>
          </div>
        </div>
      ) : null}

      <DualPaneLayout
        initialData={currentFields}
        imageUrl={selectedRecord.image_url}
        rawText={currentRawText}
        documentStatus={documentStatus}
        onSave={handleSave}
      />
      {isMultiPage && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '16px' }}>
          <button 
            className="btn-ghost" 
            disabled={currentPageIndex === 0}
            onClick={() => setCurrentPageIndex(p => p - 1)}
          >
            Previous Page
          </button>
          <span style={{ fontSize: '0.9rem', alignSelf: 'center' }}>
            Page {currentPageIndex + 1} of {pages.length}
          </span>
          <button 
            className="btn-ghost" 
            disabled={currentPageIndex === pages.length - 1}
            onClick={() => setCurrentPageIndex(p => p + 1)}
          >
            Next Page
          </button>
        </div>
      )}
    </div>
  );
}
