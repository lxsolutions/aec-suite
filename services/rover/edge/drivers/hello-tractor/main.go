























package main

import (
	"context"
	"fmt"

	"github.com/YOUR_USERNAME/rover-operations/contracts/proto/gen/go/control/v1"
)

type HelloTractorDriver struct {
	capabilities v1.DeviceCapability
	simClient     v1.SimulationServiceClient // For simulated tractor

	isEStopActive bool
	currentSpeed   float64
	currentSteer   float64
}

func NewHelloTractorDriver(pluginPath string) (*HelloTractorDriver, error) {
	// In a real implementation, this would load the plugin
	return &HelloTractorDriver{
		capabilities: v1.DeviceCapability{
			Drive: &v1.DriveCapability{
				SetSpeed:    true,
				SetSteer:    true,
				EmergencyStop: true,
			},
			Sensors: &v1.SensorCapabilities{
				Gps:        true,
				Imu:        true,
				CameraFront: &v1.CameraSpec{Resolution: "1920x1080", Fps: 30},
			},
			Pto: nil, // Not implemented in hello-tractor
		},
		isEStopActive: false,
		currentSpeed:   0.0,
		currentSteer:   0.0,
	}, nil
}

func (d *HelloTractorDriver) Initialize(ctx context.Context) error {
	fmt.Println("Initializing Hello Tractor driver...")
	return nil
}

func (d *HelloTractorDriver) ExecuteCommand(ctx context.Context, cmd *v1.Command) (*v1.CommandResponse, error) {
	switch c := cmd.GetCommandType().(type) {
	case *v1.Command_Drive:
		return d.handleDriveCommand(ctx, c.Drive)
	case *v1.Command_Safety:
		return d.handleSafetyCommand(ctx, c.Safety)
	default:
		return nil, fmt.Errorf("unsupported command type: %T", cmd.GetCommandType())
	}
}

func (d *HelloTractorDriver) handleDriveCommand(ctx context.Context, driveCmd *v1.DriveCommand) (*v1.CommandResponse, error) {
	if d.isEStopActive {
		fmt.Println("Emergency stop active - ignoring drive command")
		return &v1.CommandResponse{
			Success: false,
			ErrorMessage: "Emergency stop active",
		}, nil
	}

	d.currentSpeed = float64(driveCmd.Speed)
	d.currentSteer = float64(driveCmd.SteerAngle)

	fmt.Printf("Executing drive command: speed=%.2f, steer=%.1f°\n", d.currentSpeed, d.currentSteer)

	return &v1.CommandResponse{
		Success: true,
	}, nil
}

func (d *HelloTractorDriver) handleSafetyCommand(ctx context.Context, safetyCmd *v1.SafetyCommand) (*v1.CommandResponse, error) {
	if safetyCmd.EStopActivate {
		d.isEStopActive = true
		fmt.Println("Emergency stop activated!")
		return &v1.CommandResponse{
			Success: true,
		}, nil
	}

	return &v1.CommandResponse{
		Success: false,
		ErrorMessage: "Unknown safety command",
	}, nil
}

func (d *HelloTractorDriver) GetStatus(ctx context.Context) (*v1.DeviceStatusUpdate, error) {
	status := v1.DriveStatus{
		CurrentSpeed:   float32(d.currentSpeed),
		SteerAngle:    float32(d.currentSteer),
		IsMoving:      d.currentSpeed != 0,
		EmergencyStopActive: d.isEStopActive,

		// Simulated GPS position
		Latitude:  47.6195, // Example coordinates (Seattle)
		Longitude: -122.338,
		Altitude:   float32(0),

		HeadingDegrees: float32(d.currentSteer), // Simplified for demo
	}

	return &v1.DeviceStatusUpdate{
		SessionId: "demo-session",
		StatusType: &v1.DeviceStatusUpdate_DriveStatus{DriveStatus: &status},
	}, nil
}

func (d *HelloTractorDriver) Shutdown() {
	fmt.Println("Shutting down Hello Tractor driver...")
	d.isEStopActive = true // Ensure vehicle stops on shutdown
}










