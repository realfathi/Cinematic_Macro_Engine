import React, { useEffect, useState } from 'react';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import sql from 'react-syntax-highlighter/dist/esm/languages/prism/sql';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Database, Loader2 } from 'lucide-react';
import api from '../api';

SyntaxHighlighter.registerLanguage('sql', sql);

const QueriesView = () => {
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQueries = async () => {
      try {
        const response = await api.get('/queries');
        setQueries(response.data);
      } catch (error) {
        console.error("Error fetching queries:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchQueries();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Loader2 className="lucide-spin" size={48} color="#00e5ff" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="page-title">
        <Database size={28} style={{ marginRight: '10px' }} />
        Database Queries
      </h1>
      
      <div className="insight-card">
        <Database className="insight-icon" size={24} />
        <div>
          <strong>Architecture Transparency:</strong> Explore all analytical queries used to power the Cinematic Macro Engine. 
          The backend dynamically serves these raw queries for educational purposes.
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        {queries.map((q, i) => (
          <div key={i} className="query-container" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="query-header">
              <h3>{q.name}</h3>
            </div>
            <div className="query-desc">
              {q.description}
            </div>
            <SyntaxHighlighter 
              language="sql" 
              style={vscDarkPlus} 
              customStyle={{ margin: 0, padding: '20px', borderRadius: '0 0 12px 12px' }}
            >
              {q.sql}
            </SyntaxHighlighter>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QueriesView;
