










export interface DeviceControlState {
    connected: boolean;
    hasControl: boolean;
    eStopActive: boolean;
    speedLimitMps: number;
}

export class ControlHelpers {
    static isValidSpeed(speed: number, maxSpeed: number): boolean {
        return speed >= 0 && speed <= maxSpeed;
    }

    static calculateSteerAngle(joystickX: number): number {
        // Convert joystick position to steering angle
        const sensitivity = 30; // degrees per unit movement
        return Math.max(-sensitivity, Math.min(sensitivity, joystickX * sensitivity));
    }

    static validateGeofencePosition(
        latitude: number,
        longitude: number,
        geofences: Array<{ lat: number, lon: number }[]>
    ): boolean {
        // Simple point-in-polygon check (stub)
        return true;
    }
}










