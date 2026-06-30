import React from 'react';
import { AlertTriangle } from 'lucide-react';

const CrisisLegend = () => {
  return (
    <div className="crisis-legend-card" style={{ 
      display: 'flex', 
      alignItems: 'flex-start', 
      gap: '12px', 
      backgroundColor: 'var(--panel-bg)',
      borderLeft: '4px solid var(--color-yellow)',
      padding: '12px 16px',
      borderRadius: '8px',
      marginBottom: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
    }}>
      <AlertTriangle color="var(--color-yellow)" size={24} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
        <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>
          What is a "Crisis" Year? (Yellow Highlights on Charts)
        </strong>
        The engine identifies a year as a <strong>Crisis</strong> if any of the following macroeconomic conditions are met:
        <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px' }}>
          <li><strong>GDP Growth Rate</strong> is negative (&lt; 0%).</li>
          <li><strong>Unemployment Rate</strong> exceeds 8.0%.</li>
          <li>A major geopolitical or economic event explicitly marked as an <strong>"Economic Crisis"</strong> occurred.</li>
        </ul>
        Years failing these conditions are marked as <strong>Stable</strong>.
      </div>
    </div>
  );
};

export default CrisisLegend;
