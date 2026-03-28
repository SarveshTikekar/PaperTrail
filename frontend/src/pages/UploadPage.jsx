import React, { useState } from 'react';
import axios from 'axios';
import Dropzone from '../components/Upload/Dropzone';
import ProcessingFeedback from '../components/Upload/ProcessingFeedback';
import { useLanguage } from '../context/LanguageContext';
import OCRPanel from '../components/OCRPanel';

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
    const fileName = file.name.toLowerCase();
    if (fileName.includes('pan') || fileName.includes('49a')) {
      return 'pan_49a';
    }
    return 'voter_6';
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1>{t('uploadDoc')}</h1>
        <p className="text-muted">{t('uploadDesc')}</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 mb-8">
        <OCRPanel />
      </div>
      
      <div className="mt-8 pt-8 border-t border-gray-100">
        <h3 className="text-lg font-semibold mb-4 text-gray-400">Advanced Options (Internal Lab)</h3>
        <p className="text-sm text-gray-500 italic">
          The extraction above uses the new ROI-based multi-model engine.
        </p>
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
