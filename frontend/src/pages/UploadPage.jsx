import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import OCRPanel from '../components/OCRPanel';

export default function UploadPage() {
  const { t } = useLanguage();

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
    </div>
  );
}
