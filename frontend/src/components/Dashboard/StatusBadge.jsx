import React from 'react';
import { Clock, CheckCircle, AlertCircle } from 'lucide-react';
import './StatusBadge.css';

export default function StatusBadge({ status }) {
  let icon, label, variantClasses;

  switch (status) {
    case 'verified':
      icon = <CheckCircle size={14} />;
      label = 'Verified';
      variantClasses = 'badge-verified';
      break;
    case 'pending':
      icon = <AlertCircle size={14} />;
      label = 'Pending Verification';
      variantClasses = 'badge-pending';
      break;
    case 'processing':
    default:
      icon = <Clock size={14} />;
      label = 'Processing';
      variantClasses = 'badge-processing';
      break;
  }

  return (
    <div className={`status-badge ${variantClasses}`}>
      {icon}
      <span>{label}</span>
      <div className="badge-glow"></div>
    </div>
  );
}
