import React, { useRef, useState, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCw, AlertTriangle, Eye, EyeOff } from 'lucide-react';

// Mock function to simulate rendering bounding boxes over an image
export default function ImagePane({ activeBoxId }) {
  const containerRef = useRef(null);
  const [imgDims, setImgDims] = useState({ width: 0, height: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [showBoxes, setShowBoxes] = useState(true);
  const [imageQuality, setImageQuality] = useState('good'); // good, poor, blurry

  // We are using a dummy placeholder image for the demonstration
  const dummyImageUrl = 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80';

  // Mock bounding boxes (percentages to be responsive)
  const boundingBoxes = [
    { id: 'field_name', x: 20, y: 15, width: 40, height: 8 },
    { id: 'field_dob', x: 20, y: 28, width: 25, height: 8 },
    { id: 'field_address', x: 20, y: 41, width: 55, height: 12 },
    { id: 'field_id_number', x: 20, y: 58, width: 35, height: 8 },
  ];

  const handleImageLoad = (e) => {
    setImgDims({
      width: e.target.offsetWidth,
      height: e.target.offsetHeight
    });
    // Mock image quality detection
    setImageQuality(Math.random() > 0.7 ? 'poor' : 'good');
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.5));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);

  return (
    <div className="image-viewer-container">
      {/* Image Controls */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '12px',
        padding: '8px 12px',
        background: 'var(--bg-secondary)',
        borderRadius: '6px'
      }}>
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
          <button 
            className="btn-secondary" 
            onClick={() => setShowBoxes(!showBoxes)} 
            style={{ padding: '4px 8px' }}
          >
            {showBoxes ? <Eye size={16} /> : <EyeOff size={16} />}
          </button>
        </div>
        
        {imageQuality === 'poor' && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px',
            color: 'var(--conf-low)',
            fontSize: '0.8rem',
            fontWeight: '600'
          }}>
            <AlertTriangle size={16} />
            Poor Quality Image
          </div>
        )}
      </div>

      <div className="image-canvas-wrapper" ref={containerRef}>
        <img 
          src={dummyImageUrl} 
          alt="Document to verify" 
          className="verification-image"
          onLoad={handleImageLoad}
          id="verification-img"
          style={{ 
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'center top'
          }}
        />
        
        {imgDims.width > 0 && showBoxes && (
          <div className="bounding-box-layer" style={{ width: imgDims.width, height: imgDims.height }}>
            {boundingBoxes.map(box => (
              <div 
                key={box.id}
                className={`bounding-box ${activeBoxId === box.id ? 'active' : ''}`}
                style={{
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`
                }}
                title={`Bounding box for ${box.id}`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
