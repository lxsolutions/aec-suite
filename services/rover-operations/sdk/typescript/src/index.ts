












/**
 * Rover Operations TypeScript SDK
 *
 * This module provides helper functions and type definitions for working with the
 * Rover Operations platform from Next.js applications.
 */

// Export a main client class for testing
export class RoverClient {
  private connected: boolean = false;
  private endpoint: string;

  constructor(endpoint: string = 'localhost:50051') {
    this.endpoint = endpoint;
  }

  async connect(): Promise<void> {
    this.connected = true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  async sendCommand(command: string): Promise<string> {
    if (!this.connected) {
      throw new Error('Client not connected');
    }
    return `Command sent: ${command}`;
  }
}

