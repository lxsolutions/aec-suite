














import * as grpc from '@grpc/grpc-js';
import { loadPackageDefinition } from '@grpc/proto-loader';

export interface DriveCommand {
  speed: number;          // m/s (positive for forward, negative for reverse)
  steerAngle: number;    // degrees (-90 to +90)
}

export interface SafetyCommand {
  eStopActivate?: boolean;
  eStopRelease?: boolean;
  reason?: string;
}

export enum Status {
  UNKNOWN = 'UNKNOWN',
  OK = 'OK',
  ESTOP_ACTIVE = 'ESTOP_ACTIVE',
  COMMAND_BLOCKED = 'COMMAND_BLOCKED'
}

export interface DriveStatus {
  currentSpeed: number;      // m/s
  steerAngle: number;        // degrees (-90 to +90)
  position?: GeoPoint;
  heading?: number;           // degrees (0 = north, 90 = east)

  timestamp?: string;         // ISO format timestamp
}

export interface SafetyStatus {
  eStopActive: boolean;
  emergencyMode: boolean;

  lastEStopReason?: string;
  estopTimestamp?: string;
}

interface GeoPoint {
  latitude: number;   // Degrees (WGS84)
  longitude: number;
}

class HelloTractorClient {
  private client: any;
  private endpoint: string;

  constructor(endpoint = 'localhost:50053') {
    this.endpoint = endpoint;
    this.client = null;
  }

  async connect(): Promise<boolean> {
    try {
      const packageDefinition = await loadPackageDefinition(
        '/workspace/rover-operations/contracts/proto/drive/drive.proto',
        { keepCase: true }
      );

      const client = grpc.loadPackageDefinition(packageDefinition).drive.HelloTractor;
      this.client = new client(this.endpoint, grpc.credentials.createInsecure());

      // Test connection by getting status
      await this.getStatus();
      return true;

    } catch (error) {
      console.error(`Failed to connect to ${this.endpoint}:`, error);
      return false;
    }
  }

  disconnect(): void {
    if (this.client) {
      try {
        // In a real implementation, we might want to clean up resources
      } finally {
        this.client = null;
      }
    }
  }

  async drive(command: DriveCommand): Promise<{ success: boolean; status?: Status; message: string; responseData?: any }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const response = await new Promise((resolve, reject) => {
        this.client.Drive(command, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return {
        success: true,
        status: Status[response.status],
        message: 'Drive command successful',
        responseData: response.response_data
      };

    } catch (error) {
      console.error('Error sending drive command:', error);
      return { success: false, message: `Error sending drive command: ${String(error)}` };
    }
  }

  async emergencyStop(): Promise<{ success: boolean; message: string }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const command: SafetyCommand = {
        eStopActivate: true,
        reason: 'Emergency stop activated via SDK'
      };

      const response = await new Promise((resolve, reject) => {
        this.client.Safety(command, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return {
        success: true,
        message: 'Emergency stop activated'
      };

    } catch (error) {
      console.error('Error activating emergency stop:', error);
      return { success: false, message: `Error activating emergency stop: ${String(error)}` };
    }
  }

  async releaseEmergencyStop(): Promise<{ success: boolean; message: string }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const command: SafetyCommand = {
        eStopRelease: true,
        reason: 'Emergency stop released via SDK'
      };

      const response = await new Promise((resolve, reject) => {
        this.client.Safety(command, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return {
        success: true,
        message: 'Emergency stop released'
      };

    } catch (error) {
      console.error('Error releasing emergency stop:', error);
      return { success: false, message: `Error releasing emergency stop: ${String(error)}` };
    }
  }

  async getStatus(): Promise<{ success: boolean; status?: DriveStatus | SafetyStatus; message: string }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const response = await new Promise((resolve, reject) => {
        this.client.GetStatus({}, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return {
        success: true,
        status: response,
        message: 'Status retrieved successfully'
      };

    } catch (error) {
      console.error('Error getting status:', error);
      return { success: false, message: `Error getting status: ${String(error)}` };
    }
  }
}

export default HelloTractorClient;














