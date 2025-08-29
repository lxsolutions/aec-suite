







package main

import (
	"fmt"
	"log"
	"time"

	pb "github.com/YOUR_USERNAME/rover-operations/contracts/proto/control.proto"
)

func main() {
	fmt.Println("Starting Hello Tractor Driver (Simulated)...")

	// Initialize the simulated tractor
	tractor := NewHelloTractorDriver()

	// Start simulation loop
	simulateTractor(tractor)
}

type HelloTractorDriver struct {
	currentSpeed    float64 // m/s
	steerAngle      float64 // degrees
	position        Position
	isMoving        bool
	eStopActive     bool

	telemetryChannel chan *pb.DeviceStatusUpdate
}

type Position struct {
	Latitude  float64
	Longitude float64
	Altitude  float32
	Heading   float32 // degrees from north (0-360)
}

func NewHelloTractorDriver() *HelloTractorDriver {
	return &HelloTractorDriver{
		position: Position{
			Latitude:  37.7749, // Starting position in San Francisco
			Longitude: -122.4194,
			Altitude:  15.0,
			Heading:   0.0,
		},
		telemetryChannel: make(chan *pb.DeviceStatusUpdate),
	}
}

func simulateTractor(driver *HelloTractorDriver) {
	ticker := time.NewTicker(1 * time.Second)

	for range ticker.C {
		driver.updatePosition()
		status := driver.generateTelemetry()

		fmt.Printf("Simulated position: Lat=%f, Lon=%f, Speed=%.2fm/s\n",
			status.GetDriveStatus().GetLatitude(),
			status.GetDriveStatus().GetLongitude(),
			status.GetDriveStatus().GetCurrentSpeed())

		driver.telemetryChannel <- status
	}
}

func (d *HelloTractorDriver) updatePosition() {
	if d.eStopActive || d.currentSpeed == 0 {
		return // Don't move if stopped or in E-stop mode
	}

	// Simple movement simulation based on current speed and heading
	d.position.Latitude += d.currentSpeed * 0.01 * math.Cos(d.position.Heading * (math.Pi / 180))
	d.position.Longitude += d.currentSpeed * 0.01 * math.Sin(d.position.Heading * (math.Pi / 180))

	// Update heading based on steer angle
	if d.steerAngle != 0 {
		d.position.Heading = normalizeHeading(d.position.Heading + d.steerAngle*0.5)
	}
}

func normalizeHeading(heading float32) float32 {
	for heading < 0 {
		heading += 360
	}
	for heading >= 360 {
		heading -= 360
	}
	return heading
}

func (d *HelloTractorDriver) generateTelemetry() *pb.DeviceStatusUpdate {
	return &pb.DeviceStatusUpdate{
		SessionId: "simulated-session",
		StatusType: &pb.DeviceStatusUpdate_DriveStatus{
			DriveStatus: &pb.DriveStatus{
				CurrentSpeed:      d.currentSpeed,
				SteerAngle:        d.steerAngle,
				IsMoving:          d.isMoving && !d.eStopActive,
				EmergencyStopActive: d.eStopActive,

				Latitude:      d.position.Latitude,
				Longitude:     d.position.Longitude,
				Altitude:      d.position.Altitude,
				HeadingDegrees: float32(d.position.Heading),
			},
		},
	}
}

func (d *HelloTractorDriver) ExecuteCommand(cmd pb.Command) (*pb.CommandResponse, error) {
	switch cmdType := cmd.GetCommandType().(type) {
	case *pb.Command_DriveCommand:
		return d.executeDriveCommand(cmdType.DriveCommand)

	case *pb.Command_SafetyCommand:
		if cmdType.SafetyCommand.EStopActivate {
			d.eStopActive = true
			d.currentSpeed = 0 // Immediate stop
			fmt.Println("E-stop activated! Tractor halted.")
			return &pb.CommandResponse{
				Success: true,
				ErrorMessage: "",
				ResponseData: &pb.CommandResponse_SafetyStatus{
					SafetyStatus: &pb.SafetyStatus{
						EStopActive: true,
					},
				},
			}, nil
		}

	default:
		return &pb.CommandResponse{
			Success: false,
			ErrorMessage: "Unsupported command type",
		}, nil
	}
}

func (d *HelloTractorDriver) executeDriveCommand(cmd *pb.CommandDrive) (*pb.CommandResponse, error) {
	if d.eStopActive {
		fmt.Println("Cannot execute drive command while E-stop is active")
		return &pb.CommandResponse{
			Success: false,
			ErrorMessage: "E-stop active - commands blocked",
		}, nil
	}

	d.currentSpeed = cmd.GetSpeed()
	d.steerAngle = cmd.GetSteerAngle()

	if d.currentSpeed != 0 {
		d.isMoving = true
	} else {
		d.isMoving = false
	}

	fmt.Printf("Executing drive command: speed=%.2f, steer=%.1f°\n",
		cmd.GetSpeed(), cmd.GetSteerAngle())

	return &pb.CommandResponse{
		Success: true,
		ErrorMessage: "",
		ResponseData: &pb.CommandResponse_DriveStatus{
			DriveStatus: d.generateTelemetry().GetDriveStatus(),
		},
	}, nil
}





