import React, { useState } from 'react';
import Dropzone from '../components/Upload/Dropzone';
import ProcessingFeedback from '../components/Upload/ProcessingFeedback';
import { useLanguage } from '../context/LanguageContext';

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const { t } = useLanguage();

  const handleUpload = () => {
    if (!files || files.length === 0) return;
    setIsProcessing(true);
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1>{t('uploadDoc')}</h1>
        <p className="text-muted">{t('uploadDesc')}</p>
      </div>

      <Dropzone onFilesAccepted={setFiles} />

      <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
        <button 
          className="btn-primary" 
          onClick={handleUpload} 
          disabled={!files || files.length === 0}
          style={{ opacity: (!files || files.length === 0) ? 0.5 : 1, cursor: (!files || files.length === 0) ? 'not-allowed' : 'pointer'}}
        >
          {files && files.length > 1 ? t('processDocs') : t('processDocs')}
        </button>
      </div>

      {isProcessing && (
        <ProcessingFeedback 
          isProcessing={isProcessing} 
          onComplete={() => setIsProcessing(false)}
        />
      )}
    </div>
  );
}
