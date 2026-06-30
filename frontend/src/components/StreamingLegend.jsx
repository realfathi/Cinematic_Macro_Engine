import React from 'react';
import { Tv } from 'lucide-react';

const StreamingLegend = () => {
  return (
    <div className="streaming-legend-card" style={{ 
      display: 'flex', 
      alignItems: 'flex-start', 
      gap: '12px', 
      backgroundColor: 'var(--panel-bg)',
      borderLeft: '4px solid var(--color-purple)',
      padding: '12px 16px',
      borderRadius: '8px',
      marginBottom: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
    }}>
      <Tv color="var(--color-purple)" size={24} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
        <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>
          What is the "Streaming Era"? (Purple Highlights on Charts)
        </strong>
        The engine identifies the period from <strong>2007 to Present</strong> as the Streaming Era due to a massive shift in film distribution and consumption habits:
        <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px' }}>
          <li><strong>2007:</strong> Netflix introduces streaming video on demand, fundamentally changing the market.</li>
          <li>The widespread global adoption of high-speed broadband and smart connected TVs.</li>
          <li>A marked structural shift in <strong>average runtime</strong> and <strong>budget elasticity</strong> as studios optimize for home viewing versus theatrical releases.</li>
        </ul>
      </div>
    </div>
  );
};

export default StreamingLegend;
