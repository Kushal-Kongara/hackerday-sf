// Vapi Integration Service
// This service handles all Vapi-related functionality

export interface VapiConfig {
  assistantId: string;
  phoneNumber: string;
  apiKey: string;
  baseUrl?: string;
}

export interface CallResult {
  success: boolean;
  callId?: string;
  error?: string;
}

export interface CallStatus {
  id: string;
  status: 'initiated' | 'ringing' | 'answered' | 'ended' | 'failed';
  duration?: number;
  transcript?: string;
}

class VapiService {
  private config: VapiConfig | null = null;
  private currentCall: CallStatus | null = null;

  // Initialize Vapi with configuration
  initialize(config: VapiConfig): void {
    this.config = config;
    console.log('Vapi service initialized with config:', config);
  }

  // Make an outbound call using Vapi
  async makeCall(phoneNumber: string, assistantId?: string): Promise<CallResult> {
    if (!this.config) {
      return {
        success: false,
        error: 'Vapi not initialized. Please configure your API key and assistant ID.'
      };
    }

    try {
      // In a real implementation, you would use the Vapi SDK here
      // For now, we'll simulate the API call
      const callId = `call_${Date.now()}`;
      
      // Simulate API call to Vapi
      const response = await this.simulateVapiCall({
        assistantId: assistantId || this.config.assistantId,
        phoneNumber: phoneNumber,
        apiKey: this.config.apiKey
      });

      if (response.success) {
        this.currentCall = {
          id: callId,
          status: 'initiated'
        };
        
        // Simulate call progression
        this.simulateCallProgression(callId);
        
        return {
          success: true,
          callId: callId
        };
      } else {
        return {
          success: false,
          error: response.error || 'Failed to initiate call'
        };
      }
    } catch (error) {
      console.error('Vapi call error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // End the current call
  async endCall(): Promise<CallResult> {
    if (!this.currentCall) {
      return {
        success: false,
        error: 'No active call to end'
      };
    }

    try {
      // In a real implementation, you would call Vapi's end call API
      this.currentCall.status = 'ended';
      this.currentCall = null;
      
      return {
        success: true
      };
    } catch (error) {
      console.error('Error ending call:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to end call'
      };
    }
  }

  // Get current call status
  getCurrentCall(): CallStatus | null {
    return this.currentCall;
  }

  // Simulate Vapi API call (replace with actual Vapi SDK)
  private async simulateVapiCall(params: {
    assistantId: string;
    phoneNumber: string;
    apiKey: string;
  }): Promise<{ success: boolean; error?: string }> {
    // This is a placeholder for the actual Vapi API call
    // In a real implementation, you would use the Vapi SDK:
    // 
    // const vapi = new Vapi(apiKey);
    // const call = await vapi.calls.create({
    //   assistantId: params.assistantId,
    //   phoneNumber: params.phoneNumber
    // });
    
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simulate successful call initiation
        resolve({ success: true });
      }, 1000);
    });
  }

  // Simulate call progression (ringing -> answered -> ended)
  private simulateCallProgression(callId: string): void {
    setTimeout(() => {
      if (this.currentCall && this.currentCall.id === callId) {
        this.currentCall.status = 'ringing';
      }
    }, 2000);

    setTimeout(() => {
      if (this.currentCall && this.currentCall.id === callId) {
        this.currentCall.status = 'answered';
      }
    }, 5000);

    // Simulate call ending after 30 seconds
    setTimeout(() => {
      if (this.currentCall && this.currentCall.id === callId) {
        this.currentCall.status = 'ended';
        this.currentCall = null;
      }
    }, 35000);
  }

  // Validate configuration
  validateConfig(config: Partial<VapiConfig>): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.apiKey) {
      errors.push('API key is required');
    }

    if (!config.assistantId) {
      errors.push('Assistant ID is required');
    }

    if (!config.phoneNumber) {
      errors.push('Phone number is required');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// Export singleton instance
export const vapiService = new VapiService();

// Export utility functions
export const formatPhoneNumber = (phone: string): string => {
  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, '');
  
  // Add country code if not present
  if (cleaned.length === 10) {
    return `+1${cleaned}`;
  } else if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+${cleaned}`;
  }
  
  return phone.startsWith('+') ? phone : `+${cleaned}`;
};

export const validatePhoneNumber = (phone: string): boolean => {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length >= 10 && cleaned.length <= 15;
};
