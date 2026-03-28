import React, { useState } from 'react';
import ImagePane from './ImagePane';
import DataPane from './DataPane';
import './Verification.css';

export default function DualPaneLayout({ initialData, imageUrl, rawText, documentStatus, onSave }) {
  const [activeBoxId, setActiveBoxId] = useState(null);

  // When a user clicks a form field on the right, it highlights the bounding box on the left.
  const handleFieldFocus = (fieldId) => {
    setActiveBoxId(fieldId);
  };

  return (
    <div className="dual-pane-container">
      <div className="pane-wrapper left-pane glass-panel">
        <div className="pane-header">
          <h3>Document Image</h3>
          <span className="text-muted">Uploaded source document</span>
        </div>
        <div className="pane-content">
           <ImagePane activeBoxId={activeBoxId} imageUrl={imageUrl} />
        </div>
      </div>
      
      <div className="pane-wrapper right-pane glass-panel">
         <div className="pane-header">
          <h3>Extracted Data</h3>
          <span className="text-muted">Review, correct, and confirm</span>
        </div>
        <div className="pane-content data-content">
           <DataPane
             data={initialData}
             onFieldFocus={handleFieldFocus}
             rawText={rawText}
             documentStatus={documentStatus}
             onSave={onSave}
           />
        </div>
      </div>
    </div>
  );
}
