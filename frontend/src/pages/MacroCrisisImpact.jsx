import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, ComposedChart, Line, ReferenceArea } from 'recharts';
import { Lightbulb, Info } from 'lucide-react';
import api from '../api';
import CrisisLegend from '../components/CrisisLegend';

const COLORS = ['#00e5ff', '#2979ff', '#ff1744', '#ffb300', '#757575'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="label">{`${label}`}</p>
        {payload.map((entry, index) => {
          let value = entry.value;
          if (entry.name.toLowerCase().includes('revenue') || entry.name.toLowerCase().includes('budget')) {
            value = formatCurrency(value);
          }
          return (
            <p key={index} className="intro" style={{ color: entry.color || entry.fill }}>
              {`${entry.name}: ${value}`}
            </p>
          );
        })}
      </div>
    );
  }
  return null;
};

export const formatCurrency = (value) => {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value}`;
};

const MacroCrisisImpact = () => {
  const { eraFilter } = useOutletContext();
  const [escapism, setEscapism] = useState([]);
  const [budget, setBudget] = useState([]);
  const [production, setProduction] = useState([]);
  const [comedy, setComedy] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [resEscapism, resBudget, resProd, resComedy] = await Promise.all([
          api.get(`/escapism-index?era=${eraFilter}`),
          api.get(`/budget-dilemma?era=${eraFilter}`),
          api.get(`/production-density?era=${eraFilter}`),
          api.get(`/comedy-paradox?era=${eraFilter}`)
        ]);
        setEscapism(resEscapism.data);
        setBudget(resBudget.data);
        setProduction(resProd.data);
        setComedy(resComedy.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [eraFilter]);

  if (loading && escapism.length === 0) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '100px' }}>Loading data...</div>;

  const eras = [...new Set(escapism.map(item => item.era_type))];
  const genres = [...new Set(escapism.map(item => item.genre))];
  
  const escapismData = genres.map(genre => {
    const obj = { genre };
    eras.forEach(era => {
      const found = escapism.find(e => e.genre === genre && e.era_type === era);
      obj[era] = found ? found.market_share_pct : 0;
    });
    return obj;
  });

  const yearsBudget = [...new Set(budget.map(item => item.release_year))];
  const tiers = [...new Set(budget.map(item => item.budget_tier))];
  const budgetData = yearsBudget.map(year => {
    const obj = { year };
    tiers.forEach(tier => {
      const found = budget.find(b => b.release_year === year && b.budget_tier === tier);
      obj[tier] = found ? found.film_count : 0;
    });
    return obj;
  });

  const productionSorted = [...production].sort((a, b) => a.release_year - b.release_year);

  const crisisBlocks = [];
  let currentBlock = null;

  productionSorted.forEach((p) => {
    if (p.era_type === 'Crisis') {
      if (!currentBlock) {
        currentBlock = { start: p.release_year, end: p.release_year };
      } else {
        currentBlock.end = p.release_year;
      }
    } else {
      if (currentBlock) {
        crisisBlocks.push(currentBlock);
        currentBlock = null;
      }
    }
  });
  if (currentBlock) crisisBlocks.push(currentBlock);

  return (
    <div>
      <h1 className="page-title">Macro & Crisis Impact</h1>
      
      <div className="insight-card">
        <Lightbulb className="insight-icon" size={24} />
        <div>
          <strong>AI Insight:</strong> During crises, the budget tier distribution shifts, and certain genres increase in market share (The Escapism Index). Notice how the GDP Growth tracks closely with overall production density.
        </div>
      </div>

      <CrisisLegend />
      
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">Shows the average market share of genres during stable periods vs crisis periods. Notice which genres grow when the economy is struggling.</div>
          </div>
          <h3 className="chart-title">Escapism Index (Market Share by Era)</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={escapismData} margin={{ top: 10, right: 10, left: 20, bottom: 20 }}>
                <XAxis dataKey="genre" stroke="var(--text-secondary)" angle={-45} textAnchor="end" height={60} tick={{fontSize: 11}} />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                <Bar dataKey="Stable" fill="var(--color-teal)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Crisis" fill="var(--color-red)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">A stacked bar chart displaying the volume of films produced across different budget tiers over time.</div>
          </div>
          <h3 className="chart-title">Budget Tier Distribution Over Time</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={budgetData} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                {crisisBlocks.map((block, index) => (
                  <ReferenceArea key={`crisis-block-b-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.15} strokeOpacity={0} />
                ))}
                <XAxis dataKey="year" stroke="var(--text-secondary)" type="category" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                {tiers.map((tier, idx) => (
                  <Bar key={tier} dataKey={tier} stackId="a" fill={COLORS[idx % COLORS.length]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">Compares the macroeconomic GDP growth rate against the total number of films released (production density).</div>
          </div>
          <h3 className="chart-title">GDP Growth vs Production Density</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <ComposedChart data={productionSorted} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                {crisisBlocks.map((block, index) => (
                  <ReferenceArea key={`crisis-block-p-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.15} strokeOpacity={0} />
                ))}
                <XAxis dataKey="release_year" stroke="var(--text-secondary)" type="category" />
                <YAxis yAxisId="left" stroke="var(--text-secondary)" />
                <YAxis yAxisId="right" orientation="right" stroke="var(--color-teal)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                <Bar yAxisId="left" dataKey="total_films" name="Total Films" fill="var(--color-blue)" radius={[4, 4, 0, 0]} />
                <Line yAxisId="right" type="monotone" dataKey="gdp_growth_rate" name="GDP Growth %" stroke="var(--color-teal)" strokeWidth={3} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">Examines the trend for Comedy films, comparing their 5-year rolling average revenue against their average audience rating.</div>
          </div>
          <h3 className="chart-title">Comedy Paradox: Revenue vs Rating (5-Year MA)</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <ComposedChart data={comedy} margin={{ top: 10, right: 10, left: 30, bottom: 0 }}>
                {crisisBlocks.map((block, index) => (
                  <ReferenceArea key={`crisis-block-c-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.15} strokeOpacity={0} />
                ))}
                <XAxis dataKey="release_year" stroke="var(--text-secondary)" type="category" />
                <YAxis yAxisId="left" stroke="var(--color-teal)" tickFormatter={formatCurrency} />
                <YAxis yAxisId="right" orientation="right" stroke="var(--color-red)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                <Line yAxisId="left" type="monotone" dataKey="ma5_revenue" name="MA5 Revenue" stroke="var(--color-teal)" strokeWidth={3} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="ma5_rating" name="MA5 Rating" stroke="var(--color-red)" strokeWidth={3} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MacroCrisisImpact;