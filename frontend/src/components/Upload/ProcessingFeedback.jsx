import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle, Database } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './ProcessingFeedback.css';

const STEPS = [
  'Uploading Image',
  'Preprocessing & Enhancing',
  'Running OCR Engine',
  'Mapping Fields'
];

export default function ProcessingFeedback({ isProcessing, onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isProcessing) {
      setCurrentStep(0);
      return;
    }

    // Mock processing progression
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= STEPS.length - 1) {
          clearInterval(interval);
          setTimeout(() => {
            if (onComplete) onComplete();
            // Removed auto-navigation for now
          }, 1000);
          return prev;
        }
        return prev + 1;
      });
    }, 1500); // 1.5s per step for demonstration

    return () => clearInterval(interval);
  }, [isProcessing, navigate, onComplete]);

  if (!isProcessing) return null;

  return (
    <div className="processing-overlay">
      <div className="processing-card glass-panel">
        <div className="process-header flex-center">
          <Database className="process-icon" />
          <h2>Extracting Data</h2>
        </div>
        
        <div className="steps-container">
          {STEPS.map((step, idx) => {
            const isCompleted = currentStep > idx;
            const isActive = currentStep === idx;
            const isPending = currentStep < idx;

            return (
              <div key={step} className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                <div className="step-icon">
                  {isCompleted ? (
                    <CheckCircle className="icon-success" size={24} />
                  ) : isActive ? (
                    <Loader2 className="icon-spin icon-primary" size={24} />
                  ) : (
                    <div className="circle-pending" />
                  )}
                </div>
                <div className="step-content">
                  <h4 className={`step-title ${isPending ? 'text-muted' : ''}`}>{step}</h4>
                  {isActive && <p className="step-desc text-muted animate-fade-in">Please wait...</p>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
