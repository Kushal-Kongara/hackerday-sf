import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export interface CallStats {
  success: number;
  rejected: number;
  voicemail: number;
  forwarded: number;
}

export interface RevenueData {
  dailyRevenue: number;
  successRate: number;
  totalCalls: number;
}

export interface AgentStatus {
  isRunning: boolean;
  activeAgents: number;
  totalAgents: number;
  callsInQueue: number;
  nextCallIn: string;
}

export interface AgentConfig {
  maxCallsPerHour: number;
  callDuration: number;
  retryAttempts: number;
  voiceModel: string;
  targetAudience: string;
}

// API functions
export const apiService = {
  // Get current call statistics
  getCallStats: async (): Promise<CallStats> => {
    try {
      const response = await api.get('/api/stats/calls');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch call stats:', error);
      // Return mock data if API fails
      return {
        success: 0,
        rejected: 0,
        voicemail: 0,
        forwarded: 0
      };
    }
  },

  // Get revenue data
  getRevenueData: async (): Promise<RevenueData> => {
    try {
      const response = await api.get('/api/stats/revenue');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch revenue data:', error);
      // Return mock data if API fails
      return {
        dailyRevenue: 0,
        successRate: 0,
        totalCalls: 0
      };
    }
  },

  // Get agent status
  getAgentStatus: async (): Promise<AgentStatus> => {
    try {
      const response = await api.get('/api/agent/status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agent status:', error);
      // Return mock data if API fails
      return {
        isRunning: false,
        activeAgents: 0,
        totalAgents: 1,
        callsInQueue: 0,
        nextCallIn: '--:--'
      };
    }
  },

  // Start agent
  startAgent: async (config?: Partial<AgentConfig>): Promise<boolean> => {
    try {
      const response = await api.post('/api/agent/start', config || {});
      return response.data.success;
    } catch (error) {
      console.error('Failed to start agent:', error);
      return false;
    }
  },

  // Stop agent
  stopAgent: async (): Promise<boolean> => {
    try {
      const response = await api.post('/api/agent/stop');
      return response.data.success;
    } catch (error) {
      console.error('Failed to stop agent:', error);
      return false;
    }
  },

  // Update agent configuration
  updateAgentConfig: async (config: AgentConfig): Promise<boolean> => {
    try {
      const response = await api.put('/api/agent/config', config);
      return response.data.success;
    } catch (error) {
      console.error('Failed to update agent config:', error);
      return false;
    }
  },

  // Get agent configuration
  getAgentConfig: async (): Promise<AgentConfig> => {
    try {
      const response = await api.get('/api/agent/config');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agent config:', error);
      // Return default config if API fails
      return {
        maxCallsPerHour: 20,
        callDuration: 300,
        retryAttempts: 2,
        voiceModel: 'premium',
        targetAudience: 'sports-fans'
      };
    }
  },

  // Get real-time updates via WebSocket or polling
  subscribeToUpdates: (callback: (data: { callStats: CallStats; revenueData: RevenueData; agentStatus: AgentStatus }) => void) => {
    // This would typically use WebSocket or Server-Sent Events
    // For now, we'll use polling as a fallback
    const interval = setInterval(async () => {
      try {
        const [callStats, revenueData, agentStatus] = await Promise.all([
          apiService.getCallStats(),
          apiService.getRevenueData(),
          apiService.getAgentStatus()
        ]);
        
        callback({ callStats, revenueData, agentStatus });
      } catch (error) {
        console.error('Failed to fetch real-time updates:', error);
      }
    }, 5000); // Poll every 5 seconds

    // Return cleanup function
    return () => clearInterval(interval);
  }
};

export default api;
