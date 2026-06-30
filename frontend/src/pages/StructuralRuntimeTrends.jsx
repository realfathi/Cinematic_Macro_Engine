import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { ComposedChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, ScatterChart, Scatter, ZAxis, ReferenceArea } from 'recharts';
import { Lightbulb, Info } from 'lucide-react';
import api from '../api';
import CrisisLegend from '../components/CrisisLegend';
import StreamingLegend from '../components/StreamingLegend';

const COLORS = [
  '#ff1744', // Red
  '#00e5ff', // Cyan
  '#ffb300', // Amber
  '#651fff', // Purple
  '#00e676', // Green
  '#2979ff', // Blue
  '#0031f5c2', // blue
  '#757575', // Grey (Always maps to 'Other' since it's the 8th item)
];

const formatCurrency = (value) => {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value}`;
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="label">{`${label}`}</p>
        {payload.map((entry, index) => {
          let value = entry.value;
          if (entry.name.toLowerCase().includes('investment') || entry.name.toLowerCase().includes('budget')) {
            value = formatCurrency(value);
          }
          if (entry.name === '5Y All Films' || entry.name === '5Y Top 100') {
            value = `${value}m`;
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

const StructuralRuntimeTrends = () => {
  const { eraFilter } = useOutletContext();
  const [runtime, setRuntime] = useState([]);
  const [genreShare, setGenreShare] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [elasticity, setElasticity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [resRuntime, resGenreShare, resRatings, resElasticity] = await Promise.all([
          api.get(`/runtime-paradox?era=${eraFilter}`),
          api.get(`/decade-genre-share?era=${eraFilter}`),
          api.get(`/rating-kpis?era=${eraFilter}`),
          api.get(`/budget-elasticity?era=${eraFilter}`)
        ]);
        setRuntime(resRuntime.data);
        setGenreShare(resGenreShare.data);
        setRatings(resRatings.data);
        setElasticity(resElasticity.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [eraFilter]);

  if (loading && runtime.length === 0) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '100px' }}>Loading data...</div>;

  // Process data for charts
  const runtimeSorted = runtime.slice().sort((a, b) => a.release_year - b.release_year).map(item => ({
    ...item,
    runtime_premium: item.ma5_runtime_top100 && item.ma5_runtime_all
      ? Number((item.ma5_runtime_top100 - item.ma5_runtime_all).toFixed(2))
      : null
  }));

  const streamingBlocks = [];
  let currentBlock = null;

  runtimeSorted.forEach((p) => {
    if (p.streaming_era_flag && p.streaming_era_flag !== 'Pre-Streaming') {
      if (!currentBlock) {
        currentBlock = { start: p.release_year, end: p.release_year };
      } else {
        currentBlock.end = p.release_year;
      }
    } else {
      if (currentBlock) {
        streamingBlocks.push(currentBlock);
        currentBlock = null;
      }
    }
  });
  if (currentBlock) streamingBlocks.push(currentBlock);

  const decades = [...new Set(genreShare.map(item => item.decade))];

  // 1. Calculate total share across all decades for each genre
  const genreTotals = {};
  genreShare.forEach(g => {
    genreTotals[g.genre] = (genreTotals[g.genre] || 0) + g.genre_share_pct;
  });

  // 2. Pick the top 7 most popular genres overall
  const topGenres = Object.entries(genreTotals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)
    .map(entry => entry[0]);

  const displayGenres = [...topGenres, 'Other'];

  // 3. Build the grouped data
  const genreData = decades.map(decade => {
    const obj = { decade, Other: 0 };
    topGenres.forEach(g => obj[g] = 0);

    const decadeRecords = genreShare.filter(g => g.decade === decade);
    decadeRecords.forEach(record => {
      if (topGenres.includes(record.genre)) {
        obj[record.genre] = record.genre_share_pct;
      } else {
        obj.Other += record.genre_share_pct;
      }
    });

    obj.Other = Number(obj.Other.toFixed(2));
    return obj;
  });

  // Histogram simulation for ratings
  // Group ratings into bins of 0.5
  const bins = {};
  ratings.forEach(r => {
    const bin = Math.floor(r.weighted_rating * 2) / 2;
    bins[bin] = (bins[bin] || 0) + 1;
  });
  const ratingData = Object.keys(bins).sort().map(bin => ({
    bin: `${parseFloat(bin).toFixed(1)}`,
    count: bins[bin]
  }));

  return (
    <div>
      <h1 className="page-title">Structural & Runtime Trends</h1>

      <div className="insight-card">
        <Lightbulb className="insight-icon" size={24} />
        <div>
          <strong>AI Insight:</strong> Notice the distinct shift in Runtime Trends during the Streaming Era (highlighted in purple), especially for Top 100 films.
          Additionally, Budget Elasticity demonstrates how higher GDP Growth typically encourages significantly larger film budgets.
          <br /><br />
          <strong>Data Note:</strong> The <em>5Y All Films</em> and <em>5Y Top 100</em> series use a true <strong>volume-weighted 5-year rolling average</strong>. This is a more accurate calculation that sums the total runtime and divides by the total number of films over the 5-year window, properly weighting years with more releases instead of just averaging the yearly averages.
        </div>
      </div>

      <StreamingLegend />

      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">Shows the 5-year rolling average runtime for all films versus the top 100 grossing films. The purple area highlights the rise of streaming platforms.</div>
          </div>
          <h3 className="chart-title">Runtime Trends & Streaming Era</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <ComposedChart data={runtimeSorted} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                {streamingBlocks.map((block, index) => (
                  <ReferenceArea key={`streaming-block-r-${index}`} x1={block.start} x2={block.end} fill="#8b5cf6" fillOpacity={0.15} strokeOpacity={0} />
                ))}
                <XAxis dataKey="release_year" stroke="var(--text-secondary)" type="category" />
                <YAxis stroke="var(--text-secondary)" tickFormatter={(val) => `${val}m`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                <Line type="monotone" dataKey="ma5_runtime_all" name="5Y All Films" stroke="var(--color-blue)" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="ma5_runtime_top100" name="5Y Top 100" stroke="var(--color-teal)" strokeWidth={3} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">The difference in minutes between the average Top 100 blockbuster runtime and the average for all films. A positive premium means blockbusters are generally longer.</div>
          </div>
          <h3 className="chart-title">Blockbuster Runtime Premium (Delta)</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <ComposedChart data={runtimeSorted} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                {streamingBlocks.map((block, index) => (
                  <ReferenceArea key={`streaming-block-d-${index}`} x1={block.start} x2={block.end} fill="#8b5cf6" fillOpacity={0.15} strokeOpacity={0} />
                ))}
                <XAxis dataKey="release_year" stroke="var(--text-secondary)" type="category" />
                <YAxis stroke="var(--text-secondary)" label={{ value: 'Minutes', angle: -90, position: 'insideLeft', fill: 'var(--text-secondary)' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                <Bar dataKey="runtime_premium" name="Premium (Minutes)" fill="var(--color-red)" opacity={0.8} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">The percentage of market share held by the top genres in each decade, showing shifting audience tastes over time.</div>
          </div>
          <h3 className="chart-title">Genre Share by Decade</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={genreData} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                <XAxis dataKey="decade" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" wrapperStyle={{ color: 'var(--text-secondary)' }} />
                {displayGenres.map((genre, idx) => (
                  <Bar key={genre} dataKey={genre} stackId="a" fill={COLORS[idx % COLORS.length]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">A histogram of films binned by their weighted IMDb rating, showing the overall quality distribution.</div>
          </div>
          <h3 className="chart-title">Weighted Rating Distribution</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={ratingData} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                <XAxis dataKey="bin" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Movies Count" fill="var(--color-blue)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-info-icon">
            <Info size={18} />
            <div className="tooltip-text">A scatter plot showing how total industry investment and average movie budgets respond to macroeconomic GDP growth rates.</div>
          </div>
          <h3 className="chart-title">Budget Elasticity vs GDP</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <ScatterChart margin={{ top: 10, right: 10, left: 30, bottom: 0 }}>
                <XAxis dataKey="gdp_growth_rate" name="GDP Growth %" stroke="var(--text-secondary)" type="number" />
                <YAxis dataKey="total_industry_investment" name="Total Investment" stroke="var(--text-secondary)" type="number" tickFormatter={formatCurrency} />
                <ZAxis dataKey="avg_movie_budget" range={[20, 400]} name="Avg Budget" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                <Scatter name="Years" data={elasticity} fill="var(--color-teal)" opacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StructuralRuntimeTrends;
