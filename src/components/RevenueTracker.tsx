import React from 'react';
import { DollarSign, TrendingUp, Target, Calendar } from 'lucide-react';
import './RevenueTracker.css';

interface RevenueData {
  dailyRevenue: number;
  successRate: number;
  totalCalls: number;
}

interface RevenueTrackerProps {
  data: RevenueData;
}

const RevenueTracker: React.FC<RevenueTrackerProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const calculateProjectedMonthly = () => {
    // Assuming 8 hours of work per day, 22 working days per month
    const dailyHours = 8;
    const workingDaysPerMonth = 22;
    const callsPerHour = data.totalCalls > 0 ? data.totalCalls / (dailyHours * 0.5) : 0; // Assuming half day of data
    const monthlyCalls = callsPerHour * dailyHours * workingDaysPerMonth;
    const monthlyRevenue = monthlyCalls * (data.successRate / 100) * 25; // $25 per successful sale
    return monthlyRevenue;
  };

  const projectedMonthly = calculateProjectedMonthly();
  const revenuePerCall = data.totalCalls > 0 ? data.dailyRevenue / data.totalCalls : 0;

  return (
    <div className="revenue-tracker">
      <div className="revenue-header">
        <h2>Revenue Analytics</h2>
        <div className="date-indicator">
          <Calendar size={16} />
          <span>Today</span>
        </div>
      </div>

      <div className="revenue-main">
        <div className="primary-metric">
          <div className="metric-icon">
            <DollarSign size={32} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Daily Revenue</div>
            <div className="metric-value">{formatCurrency(data.dailyRevenue)}</div>
            <div className="metric-subtitle">
              {data.totalCalls} calls made
            </div>
          </div>
        </div>

        <div className="revenue-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <TrendingUp size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Success Rate</div>
              <div className="stat-value">{data.successRate.toFixed(1)}%</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Target size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Revenue/Call</div>
              <div className="stat-value">{formatCurrency(revenuePerCall)}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="projection-section">
        <div className="projection-header">
          <h3>Monthly Projection</h3>
          <div className="projection-note">Based on current performance</div>
        </div>
        <div className="projection-value">
          {formatCurrency(projectedMonthly)}
        </div>
        <div className="projection-breakdown">
          <div className="breakdown-item">
            <span className="breakdown-label">Avg. calls/day:</span>
            <span className="breakdown-value">{Math.round(data.totalCalls * 2)}</span>
          </div>
          <div className="breakdown-item">
            <span className="breakdown-label">Working days/month:</span>
            <span className="breakdown-value">22</span>
          </div>
          <div className="breakdown-item">
            <span className="breakdown-label">Revenue per sale:</span>
            <span className="breakdown-value">$25</span>
          </div>
        </div>
      </div>

      <div className="performance-indicators">
        <div className="indicator">
          <div className="indicator-dot success"></div>
          <span>High Performance</span>
        </div>
        <div className="indicator">
          <div className="indicator-dot warning"></div>
          <span>Optimization Needed</span>
        </div>
      </div>
    </div>
  );
};

export default RevenueTracker;
