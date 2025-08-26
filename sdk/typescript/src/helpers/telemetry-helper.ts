















import * as grpc from '@grpc/grpc-js';
import { loadPackageDefinition } from '@grpc/proto-loader';

export enum SensorType {
  UNKNOWN = 'UNKNOWN',
  GPS = 'GPS',            // Global Positioning System
  IMU = 'IMU',            // Inertial Measurement Unit (accelerometer, gyroscope)
  ENGINE = 'ENGINE',      // Engine status and metrics
  BATTERY = 'BATTERY',    // Battery level and health
  CONTROL_INPUTS = 'CONTROL_INPUTS' // Operator control inputs
}

export interface GeoPoint {
  latitude: number;   // Degrees (WGS84)
  longitude: number;
}

interface Timestamp {
  seconds: number;
  nanos: number;

  static now(): Timestamp {
    const now = new Date();
    return {
      seconds: Math.floor(now.getTime() / 1000),
      nanos: (now.getTime() % 1000) * 1_000_000
    };
  }
}

interface GpsData {
  position: GeoPoint;
  altitudeMeters?: number;

  satellitesInView?: number;
  horizontalAccuracyMeters?: number;
}

interface ImuData {
  accelerationX: number;   // m/s² (vehicle frame)
  accelerationY: number;
  accelerationZ: number;

  angularRateX?: number;    // rad/s
  angularRateY?: number;
  angularRateZ?: number;
}

export interface TelemetryEvent {
  deviceId: string;
  sensorType: SensorType;

  gpsData?: GpsData;
  imuData?: ImuData;
  engineData?: any;
  batteryData?: any;
  controlInputs?: any;
  customSensorData?: any;

  timestamp?: Timestamp;   // When the data was recorded
}

class TelemetryHelper {
  private client: any;
  private endpoint: string;

  constructor(endpoint = 'localhost:8082') {
    this.endpoint = endpoint;
    this.client = null;
  }

  async connect(): Promise<boolean> {
    try {
      const packageDefinition = await loadPackageDefinition(
        '/workspace/rover-operations/contracts/proto/telemetry/telemetry.proto',
        { keepCase: true }
      );

      const client = grpc.loadPackageDefinition(packageDefinition).telemetry.TelemetryService;
      this.client = new client(this.endpoint, grpc.credentials.createInsecure());

      // Test connection by sending a simple ping
      await this.testConnection();
      return true;

    } catch (error) {
      console.error(`Failed to connect to ${this.endpoint}:`, error);
      return false;
    }
  }

  private async testConnection(): Promise<void> {
    const testEvent: TelemetryEvent = {
      deviceId: 'test-device',
      sensorType: SensorType.GPS,
      gpsData: {
        position: { latitude: 0, longitude: 0 },
        timestamp: Timestamp.now()
      }
    };

    try {
      await new Promise((resolve, reject) => {
        this.client.IngestEvent(testEvent, (error: Error | null, response: any) => {
          if (error || !response.success) {
            reject(error || new Error(`Connection test failed: ${response.message}`));
          } else {
            resolve(true);
          }
        });
      });

    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
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

  async ingestGpsData(deviceId: string, latitude: number, longitude: number,
                      altitudeMeters?: number): Promise<{ success: boolean; message: string }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const event: TelemetryEvent = {
        deviceId,
        sensorType: SensorType.GPS,
        gpsData: {
          position: { latitude, longitude },
          altitudeMeters: altitudeMeters || 0.0,
          timestamp: Timestamp.now()
        }
      };

      await new Promise((resolve, reject) => {
        this.client.IngestEvent(event, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return { success: true, message: 'GPS data ingested successfully' };

    } catch (error) {
      console.error('Error ingesting GPS data:', error);
      return { success: false, message: `Error ingesting GPS data: ${String(error)}` };
    }
  }

  async queryRecentData(deviceId: string, sensorType: SensorType,
                        minutesBack = 5): Promise<{ success: boolean; events?: TelemetryEvent[]; message: string }> {
    if (!this.client) {
      return { success: false, message: 'Not connected' };
    }

    try {
      const now = Timestamp.now();
      const startTime: Timestamp = {
        seconds: now.seconds - (minutesBack * 60),
        nanos: now.nanos
      };

      // Create query request
      const queryRequest = {
        deviceId,
        sensorType,
        startTime,
        endTime: now,
        maxResults: 100
      };

      const response = await new Promise((resolve, reject) => {
        this.client.QueryEvents(queryRequest, (error: Error | null, response: any) => {
          if (error) {
            reject(error);
          } else {
            resolve(response);
          }
        });
      });

      return {
        success: true,
        events: response.events || [],
        message: `Retrieved ${response.events?.length || 0} events`
      };

    } catch (error) {
      console.error('Error querying telemetry:', error);
      return { success: false, message: `Error querying telemetry: ${String(error)}` };
    }
  }

  static createGpsEvent(deviceId: string, latitude: number, longitude: number,
                        altitudeMeters?: number): TelemetryEvent {
    return {
      deviceId,
      sensorType: SensorType.GPS,
      gpsData: {
        position: { latitude, longitude },
        altitudeMeters: altitudeMeters || 0.0,
        timestamp: Timestamp.now()
      }
    };
  }

  static createImuEvent(deviceId: string,
                       accelX: number, accelY: number, accelZ: number,
                       gyroX?: number, gyroY?: number, gyroZ?: number): TelemetryEvent {
    return {
      deviceId,
      sensorType: SensorType.IMU,
      imuData: {
        accelerationX: accelX,
        accelerationY: accelY,
        accelerationZ: accelZ,
        angularRateX: gyroX || 0.0,
        angularRateY: gyroY || 0.0,
        angularRateZ: gyroZ || 0.0,
        timestamp: Timestamp.now()
      }
    };
  }
}

export default TelemetryHelper;















