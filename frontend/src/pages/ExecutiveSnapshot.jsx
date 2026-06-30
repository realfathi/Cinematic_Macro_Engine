import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend, ReferenceArea } from 'recharts';
import { Lightbulb, Info } from 'lucide-react';
import api from '../api';
import CrisisLegend from '../components/CrisisLegend';

const COLORS = ['#00e5ff', '#2979ff', '#ffb300', '#ff1744'];

const formatCurrency = (val) => {
  if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
  if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
  if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
  return `$${val}`;
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        {label !== undefined && label !== '' && <p className="label">{`${label}`}</p>}
        {payload.map((entry, index) => {
          const name = entry.name || '';
          return (
            <p key={index} className="intro" style={{ color: entry.color || entry.fill }}>
              {`${name}: ${name.toLowerCase().includes('revenue') || name.toLowerCase().includes('box_office') || name.toLowerCase().includes('sales') || name.toLowerCase().includes('profit') ? formatCurrency(entry.value) : entry.value}`}
            </p>
          );
        })}
      </div>
    );
  }
  return null;
};

const ExecutiveSnapshot = () => {
  const { eraFilter } = useOutletContext();
  const [trends, setTrends] = useState([]);
  const [top10, setTop10] = useState([]);
  const [profitability, setProfitability] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartType, setChartType] = useState('area'); // Visual Option

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [resTrends, resTop10, resProfit] = await Promise.all([
          api.get(`/industry-trends?era=${eraFilter}`),
          api.get(`/top-blockbusters?era=${eraFilter}`),
          api.get(`/profitability-split?era=${eraFilter}`)
        ]);
        setTrends(resTrends.data);
        setTop10(resTop10.data);
        setProfitability(resProfit.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [eraFilter]);

  if (loading && trends.length === 0) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '100px' }}>Loading data...</div>;

  const trendsSorted = [...trends].sort((a, b) => a.release_year - b.release_year);

  const totalRevenue = trendsSorted.reduce((sum, item) => sum + (item.total_box_office || 0), 0);
  const totalMovies = trendsSorted.reduce((sum, item) => sum + (item.movies_released || 0), 0);
  const totalProfit = trendsSorted.reduce((sum, item) => sum + (item.net_profit || 0), 0);
  const totalBudget = trendsSorted.reduce((sum, item) => sum + (item.total_industry_budget || 0), 0);
  
  // Calculate true weighted ROI across the entire dataset: (Total Profit / Total Budget) * 100
  const avgRoi = totalBudget > 0 ? (totalProfit / totalBudget) * 100 : 0;

  const crisisBlocks = [];
  let currentBlock = null;

  trendsSorted.forEach((p) => {
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
      <h1 className="page-title">Executive Snapshot</h1>
      
      <div className="insight-card">
        <Lightbulb className="insight-icon" size={24} />
        <div>
          <strong>AI Insight:</strong> Based on the overall industry trends, periods of economic crisis frequently align with dips in average ROI. 
          However, Gross Sales have generally trended upward over time despite these dips. The blockbuster tier dominates profitability.
        </div>
      </div>

      <CrisisLegend />
      
      <div style={{ display: 'flex', gap: '30px', alignItems: 'flex-start' }}>
        <div className="kpi-grid" style={{ flex: '0 0 250px' }}>
          <div className="kpi-card" title="Total Box Office Revenue for all movies in the dataset">
            <div className="kpi-value" style={{ color: 'var(--color-teal)' }}>{formatCurrency(totalRevenue)}</div>
            <div className="kpi-label">Gross Sales</div>
          </div>
          <div className="kpi-card" title="Total number of movies released">
            <div className="kpi-value" style={{ color: 'var(--color-blue)' }}>{totalMovies.toLocaleString()}</div>
            <div className="kpi-label">Total Films Released</div>
          </div>
          <div className="kpi-card" title="Total Net Profit (Gross Sales minus Budgets)">
            <div className="kpi-value" style={{ color: 'var(--color-red)' }}>{formatCurrency(totalProfit)}</div>
            <div className="kpi-label">Profit</div>
          </div>
          <div className="kpi-card" title="True Weighted Average Return on Investment (Total Profit / Total Budget)">
            <div className="kpi-value" style={{ color: 'var(--color-yellow)' }}>{avgRoi.toFixed(1)}%</div>
            <div className="kpi-label">Avg ROI</div>
          </div>
        </div>

        <div className="charts-grid" style={{ flex: 1, marginTop: 0 }}>
          
          <div className="chart-card">
            <div className="chart-info-icon">
              <Info size={18} />
              <div className="tooltip-text">Shows the total box office revenue generated by all films in the dataset over time. The shaded yellow areas indicate periods of macroeconomic crisis.</div>
            </div>
            <div className="chart-title">
              <span>Gross Revenue Over Time</span>
              <button className="chart-toggle-btn" onClick={() => setChartType(prev => prev === 'area' ? 'line' : 'area')}>
                Toggle {chartType === 'area' ? 'Line' : 'Area'}
              </button>
            </div>
            <div style={{ width: '100%', height: 250 }}>
              <ResponsiveContainer>
                {chartType === 'area' ? (
                  <AreaChart data={trendsSorted} margin={{ top: 10, right: 10, left: 30, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--color-teal)" stopOpacity={0.5}/>
                        <stop offset="95%" stopColor="var(--color-teal)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="release_year" stroke="var(--text-secondary)" />
                    <YAxis stroke="var(--text-secondary)" tickFormatter={formatCurrency} />
                    <Tooltip content={<CustomTooltip />} />
                    {crisisBlocks.map((block, index) => (
                      <ReferenceArea key={`cr-area-1-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.1} strokeOpacity={0} />
                    ))}
                    <Area type="monotone" dataKey="total_box_office" name="Gross Revenue" stroke="var(--color-teal)" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                  </AreaChart>
                ) : (
                  <LineChart data={trendsSorted} margin={{ top: 10, right: 10, left: 30, bottom: 0 }}>
                    <XAxis dataKey="release_year" stroke="var(--text-secondary)" />
                    <YAxis stroke="var(--text-secondary)" tickFormatter={formatCurrency} />
                    <Tooltip content={<CustomTooltip />} />
                    {crisisBlocks.map((block, index) => (
                      <ReferenceArea key={`cr-area-1-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.1} strokeOpacity={0} />
                    ))}
                    <Line type="monotone" dataKey="total_box_office" name="Gross Revenue" stroke="var(--color-teal)" strokeWidth={3} dot={false} />
                  </LineChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-info-icon">
              <Info size={18} />
              <div className="tooltip-text">A breakdown of films by their profit multiples (Gross Revenue / Budget). Blockbusters earn &gt;5x their budget, while Flops fail to break even.</div>
            </div>
            <h3 className="chart-title">Profitability Margin Split</h3>
            <div style={{ width: '100%', height: 250 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={profitability}
                    dataKey="movie_count"
                    nameKey="profitability_tier"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {profitability.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px', color: 'var(--text-secondary)' }}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
            <div className="chart-info-icon">
              <Info size={18} />
              <div className="tooltip-text">The 10 highest-grossing films of all time within the selected era, showing absolute gross revenue.</div>
            </div>
            <h3 className="chart-title">Top 10 Blockbusters</h3>
            <div style={{ width: '100%', height: 350 }}>
              <ResponsiveContainer>
                {(() => {
                  const top10Sorted = [...top10]
                    .sort((a, b) => b.revenue - a.revenue)
                    .reverse();

                  return (
                    <BarChart data={top10Sorted} layout="vertical" margin={{ top: 5, right: 10, left: 40, bottom: 5 }}>
                      <XAxis type="number" stroke="var(--text-secondary)" tickFormatter={formatCurrency} />
                      <YAxis dataKey="title" type="category" stroke="var(--text-secondary)" width={140} tick={{ fontSize: 11 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="revenue" name="Revenue" fill="var(--color-teal)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  );
                })()}
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
            <div className="chart-info-icon">
              <Info size={18} />
              <div className="tooltip-text">The volume-weighted average Return on Investment for all films released in a given year. Calculated as (Total Profit / Total Budget).</div>
            </div>
            <h3 className="chart-title">Avg ROI per Year</h3>
            <div style={{ width: '100%', height: 250 }}>
              <ResponsiveContainer>
                <BarChart data={trendsSorted} margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
                  <XAxis dataKey="release_year" stroke="var(--text-secondary)" />
                  <YAxis stroke="var(--text-secondary)" tickFormatter={(val) => `${val}%`} />
                  <Tooltip content={<CustomTooltip />} />
                  
                  {crisisBlocks.map((block, index) => (
                    <ReferenceArea key={`cr-area-2-${index}`} x1={block.start} x2={block.end} fill="var(--color-yellow)" fillOpacity={0.1} strokeOpacity={0} />
                  ))}
                  
                  <Bar dataKey="avg_roi" name="Avg ROI (%)" fill="var(--color-blue)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ExecutiveSnapshot;