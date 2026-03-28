import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Eye, EyeOff, FileImage } from 'lucide-react';

export default function ImagePane({ activeBoxId, imageUrl }) {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [showBoxes, setShowBoxes] = useState(true);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);

  return (
    <div className="image-viewer-container">
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '12px',
          padding: '8px 12px',
          background: 'var(--bg-secondary)',
          borderRadius: '6px',
        }}
      >
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button className="btn-secondary" onClick={handleZoomOut} style={{ padding: '4px 8px' }}>
            <ZoomOut size={16} />
          </button>
          <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>{Math.round(zoom * 100)}%</span>
          <button className="btn-secondary" onClick={handleZoomIn} style={{ padding: '4px 8px' }}>
            <ZoomIn size={16} />
          </button>
          <button className="btn-secondary" onClick={handleRotate} style={{ padding: '4px 8px' }}>
            <RotateCw size={16} />
          </button>
          <button className="btn-secondary" onClick={() => setShowBoxes((prev) => !prev)} style={{ padding: '4px 8px' }}>
            {showBoxes ? <Eye size={16} /> : <EyeOff size={16} />}
          </button>
        </div>

        <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', fontWeight: 600 }}>
          {activeBoxId ? `Focused field: ${activeBoxId}` : 'Select a field to highlight it here'}
        </div>
      </div>

      <div className="image-canvas-wrapper" style={{ display: 'grid', placeItems: 'center', minHeight: '440px' }}>
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Document to verify"
            className="verification-image"
            id="verification-img"
            style={{
              transform: `scale(${zoom}) rotate(${rotation}deg)`,
              transformOrigin: 'center center',
              maxHeight: '720px',
              objectFit: 'contain',
            }}
          />
        ) : (
          <div
            style={{
              display: 'grid',
              placeItems: 'center',
              textAlign: 'center',
              color: 'var(--text-secondary)',
              gap: '10px',
            }}
          >
            <FileImage size={30} />
            <div>
              <div style={{ fontWeight: 700 }}>No uploaded image available</div>
              <div style={{ fontSize: '0.82rem' }}>Upload a form first to review the extracted fields beside it.</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
