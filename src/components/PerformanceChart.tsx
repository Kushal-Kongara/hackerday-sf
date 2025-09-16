import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Phone, PhoneOff, Voicemail, Forward } from 'lucide-react';
import './PerformanceChart.css';

interface CallStats {
  success: number;
  rejected: number;
  voicemail: number;
  forwarded: number;
}

interface PerformanceChartProps {
  data: CallStats;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => {
  const chartData = [
    {
      name: 'Successful Calls',
      value: data.success,
      color: '#10b981',
      icon: Phone
    },
    {
      name: 'Rejected Calls',
      value: data.rejected,
      color: '#ef4444',
      icon: PhoneOff
    },
    {
      name: 'Voicemail',
      value: data.voicemail,
      color: '#f59e0b',
      icon: Voicemail
    },
    {
      name: 'Forwarded',
      value: data.forwarded,
      color: '#3b82f6',
      icon: Forward
    }
  ];

  const totalCalls = data.success + data.rejected + data.voicemail + data.forwarded;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = totalCalls > 0 ? ((data.value / totalCalls) * 100).toFixed(1) : 0;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{data.name}</p>
          <p className="tooltip-value">{data.value} calls ({percentage}%)</p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = ({ payload }: any) => {
    return (
      <div className="custom-legend">
        {payload.map((entry: any, index: number) => {
          const IconComponent = chartData[index].icon;
          const percentage = totalCalls > 0 ? ((entry.value / totalCalls) * 100).toFixed(1) : 0;
          return (
            <div key={index} className="legend-item">
              <div className="legend-color" style={{ backgroundColor: entry.color }}></div>
              <IconComponent size={16} />
              <span className="legend-text">{entry.name}</span>
              <span className="legend-value">{entry.value} ({percentage}%)</span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="performance-chart">
      <div className="chart-header">
        <h2>Call Performance</h2>
        <div className="total-calls">
          Total Calls: <span className="total-number">{totalCalls}</span>
        </div>
      </div>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={120}
              paddingAngle={5}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomLegend />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      <div className="stats-summary">
        <div className="stat-item">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value">
            {totalCalls > 0 ? ((data.success / totalCalls) * 100).toFixed(1) : 0}%
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Rejection Rate</div>
          <div className="stat-value">
            {totalCalls > 0 ? ((data.rejected / totalCalls) * 100).toFixed(1) : 0}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceChart;
