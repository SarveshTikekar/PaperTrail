import React, { useState } from 'react';
import axios from 'axios';
import Dropzone from '../components/Upload/Dropzone';
import ProcessingFeedback from '../components/Upload/ProcessingFeedback';
import { useLanguage } from '../context/LanguageContext';

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);
  const { t } = useLanguage();

  const handleUpload = async () => {
    if (!files || files.length === 0) return;
    setIsProcessing(true);
    setUploadResults([]);

    try {
      const results = [];

      for (const file of files) {
        // Determine form type based on file content or user selection
        // For now, we'll use a simple heuristic or prompt user
        const formType = determineFormType(file);

        const formData = new FormData();
        formData.append('image', file);
        formData.append('form_type', formType);

        const response = await axios.post('http://127.0.0.1:8000/api/lab/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        results.push({
          file: file.name,
          formType,
          data: response.data,
          success: true
        });
      }

      setUploadResults(results);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadResults([{
        file: files[0]?.name || 'Unknown',
        success: false,
        error: error.response?.data?.error || error.message
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const determineFormType = (file) => {
    // Simple heuristic: if filename contains 'pan' or '49a', assume PAN form
    // Otherwise default to voter ID
    const fileName = file.name.toLowerCase();
    if (fileName.includes('pan') || fileName.includes('49a')) {
      return 'pan_49a';
    }
    return 'voter_6'; // Default to voter ID
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

      {uploadResults.length > 0 && !isProcessing && (
        <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3>Upload Results:</h3>
          {uploadResults.map((result, index) => (
            <div key={index} style={{ marginBottom: '16px', padding: '12px', backgroundColor: result.success ? '#d4edda' : '#f8d7da', borderRadius: '4px' }}>
              <strong>{result.file}</strong> ({result.formType || 'Unknown type'})
              {result.success ? (
                <div>
                  <p style={{ color: '#155724', margin: '8px 0' }}>✅ Successfully processed!</p>
                  <details>
                    <summary>View extracted data</summary>
                    <pre style={{ fontSize: '12px', marginTop: '8px', whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p style={{ color: '#721c24', margin: '8px 0' }}>❌ Error: {result.error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
