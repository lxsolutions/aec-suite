
/**
 * Basic test for the Rover Operations SDK
 */

import { RoverClient } from './index';

describe('Rover Operations SDK', () => {
  test('should create a client instance', () => {
    // This is a basic smoke test to ensure the SDK can be imported
    expect(RoverClient).toBeDefined();
    expect(typeof RoverClient).toBe('function');
  });

  test('should have required methods', () => {
    // Test that the client has the expected methods
    const clientMethods = Object.getOwnPropertyNames(RoverClient.prototype);
    expect(clientMethods).toContain('connect');
    expect(clientMethods).toContain('disconnect');
    expect(clientMethods).toContain('sendCommand');
  });
});
