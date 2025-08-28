














package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"net"
	"time"

	"github.com/golang/protobuf/ptypes/empty"
	"google.golang.org/grpc"
	drivepb "github.com/YOUR_USERNAME/rover-operations/contracts/proto/drive"
)

const (
	defaultPort = ":50053"
	simUpdateInterval = 100 * time.Millisecond
	maxSpeedMps      = 2.0 // Maximum speed in meters per second for simulation
)

// HelloTractorSimulator implements the drive.HelloTractor service
type HelloTractorSimulator struct {
	drivepb.UnimplementedHelloTractorServer

	currentSpeed float64   // m/s (positive forward, negative reverse)
	steerAngle  float64   // degrees (-90 to +90)
	position    GeoPoint  // Current GPS position
	heading     float64   // degrees (0 = north, 90 = east)

	eStopActive bool      // Emergency stop status

	lastUpdate time.Time   // Time of last state update
}

// GeoPoint represents a geographic coordinate
type GeoPoint struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
}

func NewHelloTractorSimulator() *HelloTractorSimulator {
	return &HelloTractorSimulator{
		position:    GeoPoint{0.0, 0.0}, // Start at origin
		currentSpeed: 0,
		steerAngle:  0,
		eStopActive: false,
		lastUpdate:   time.Now(),
	}
}

// Drive implements the gRPC method to control tractor movement
func (s *HelloTractorSimulator) Drive(ctx context.Context, cmd *drivepb.DriveCommand) (*drivepb.CommandResponse, error) {
	if s.eStopActive {
		return &drivepb.CommandResponse{
			status: drivepb.Status_ESTOP_ACTIVE,
			response_data: &drivepb.CommandResponse_ErrorMessage{
				error_message: "Cannot execute command while E-stop is active",
			},
		}, nil
	}

	// Apply speed limits for safety
	speed := cmd.Speed
	if math.Abs(speed) > maxSpeedMps {
		log.Printf("Warning: Speed %.2f m/s exceeds maximum of %.2f, capping", speed, maxSpeedMps)
		if speed > 0 {
			speed = maxSpeedMps
		} else {
			speed = -maxSpeedMps
		}
	}

	// Apply steering limits
	steer := cmd.SteerAngle
	if steer < -90.0 || steer > 90.0 {
		log.Printf("Warning: Steering angle %.2f degrees out of range (-90 to +90), capping", steer)
		if steer < -90.0 {
			steer = -90.0
		} else if steer > 90.0 {
			steer = 90.0
		}
	}

	s.currentSpeed = speed
	s.steerAngle = steer

	// Update position based on movement (simplified physics)
	s.updatePosition()

	return &drivepb.CommandResponse{
		status: drivepb.Status_OK,
		response_data: &drivepb.CommandResponse_DriveStatus{
			drive_status: &drivepb.DriveStatus{
				current_speed: s.currentSpeed,
				steer_angle:  s.steerAngle,
				position:     &drivepb.GeoPoint{latitude: s.position.Latitude, longitude: s.position.Longitude},
				heading:      s.heading,
				timestamp:    timestampNow(),
			},
		},
	}, nil
}

// Safety implements the gRPC method for safety commands (E-stop)
func (s *HelloTractorSimulator) Safety(ctx context.Context, cmd *drivepb.SafetyCommand) (*drivepb.CommandResponse, error) {
	if cmd.EStopActivate && !cmd.EStopRelease {
		s.eStopActive = true
		log.Printf("EMERGENCY STOP ACTIVATED: %s", cmd.Reason)
		return &drivepb.CommandResponse{
			status: drivepb.Status_OK,
			response_data: &drivepb.CommandResponse_SafetyStatus{
				safety_status: &drivepb.SafetyStatus{
					e_stop_active: true,
					last_estop_reason: cmd.Reason,
					estop_timestamp: timestampNow(),
				},
			},
		}, nil
	}

	if !cmd.EStopActivate && cmd.EStopRelease {
		s.eStopActive = false
		log.Printf("EMERGENCY STOP RELEASED")
		return &drivepb.CommandResponse{
			status: drivepb.Status_OK,
			response_data: &drivepb.CommandResponse_SafetyStatus{
				safety_status: &drivepb.SafetyStatus{
					e_stop_active: false,
					last_estop_reason: "",
					estop_timestamp: timestampNow(),
				},
			},
		}, nil
	}

	return &drivepb.CommandResponse{
		status: drivepb.Status_OK,
		response_data: &drivepb.CommandResponse_SafetyStatus{
			safety_status: &drivepb.SafetyStatus{
				e_stop_active: s.eStopActive,
			},
		},
	}, nil
}

// GetStatus implements the gRPC method to retrieve current device status
func (s *HelloTractorSimulator) GetStatus(ctx context.Context, _ *empty.Empty) (*drivepb.DeviceStatusUpdate, error) {
	s.updatePosition() // Ensure position is up-to-date

	return &drivepb.DeviceStatusUpdate{
		position: drivepb.GeoPoint{latitude: s.position.Latitude, longitude: s.position.Longitude},
		current_speed: s.currentSpeed,
		heading:      s.heading,

		safety_status: &drivepb.SafetyStatus{
			e_stop_active: s.eStopActive,
		},

		timestamp: timestampNow(),
	}, nil
}

// updatePosition updates the simulator's position based on current speed and heading
func (s *HelloTractorSimulator) updatePosition() {
	if time.Since(s.lastUpdate) < simUpdateInterval {
		return // Don't update too frequently
	}

	s.lastUpdate = time.Now()

	// Only move if not stopped or in emergency mode
	if math.Abs(s.currentSpeed) > 0.1 && !s.eStopActive {
		// Convert speed from m/s to degrees latitude/longitude per second
		// This is a simplified approximation - real implementation would use proper geodesic calculations

		// Calculate distance moved (in meters)
		distance := s.currentSpeed * simUpdateInterval.Seconds()

		// Update position based on heading
		radians := degToRad(s.heading)

		deltaLat := distance * math.Cos(radians) / 111320.0 // Approximate meters to degrees latitude
		deltaLon := distance * math.Sin(radians) / (111320.0 * math.Cos(degToRad(s.position.Latitude)))

		s.position.Latitude += deltaLat
		s.position.Longitude += deltaLon

		log.Printf("Updated position: %.6f, %.6f | Speed: %.2f m/s | Heading: %.1f°",
			s.position.Latitude, s.position.Longitude, s.currentSpeed, s.heading)
	}
}

// timestampNow returns a protobuf Timestamp representing the current time
func timestampNow() *drivepb.Timestamp {
	now := time.Now()
	return &drivepb.Timestamp{
		Seconds: now.Unix(),
		Nanos:   int32(now.Nanosecond()),
	}
}

// degToRad converts degrees to radians
func degToRad(degrees float64) float64 {
	return degrees * math.Pi / 180.0
}

func main() {
	fmt.Println("Starting Hello Tractor Simulation Service...")

	sim := NewHelloTractorSimulator()

	// Set up gRPC server
	lis, err := net.Listen("tcp", defaultPort)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	drivepb.RegisterHelloTractorServer(grpcServer, sim)

	fmt.Printf("Simulation service running on port %s\n", defaultPort)
	fmt.Println("Press Ctrl+C to stop")

	// Start the server
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}














