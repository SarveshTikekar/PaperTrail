import React, { useRef, useState, useEffect } from 'react';

// Mock function to simulate rendering bounding boxes over an image
export default function ImagePane({ activeBoxId }) {
  const containerRef = useRef(null);
  const [imgDims, setImgDims] = useState({ width: 0, height: 0 });

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
  };

  return (
    <div className="image-viewer-container">
      <div className="image-canvas-wrapper" ref={containerRef}>
        <img 
          src={dummyImageUrl} 
          alt="Document to verify" 
          className="verification-image"
          onLoad={handleImageLoad}
          id="verification-img"
        />
        
        {imgDims.width > 0 && (
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
