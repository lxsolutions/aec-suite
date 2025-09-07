










package main

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "github.com/YOUR_USERNAME/rover-operations/contracts/proto/drive.proto"
)

func main() {
	fmt.Println("Starting Hello Tractor Simulation...")

	// Initialize gRPC server for simulation control
	simServer := setupSimulationServer()

	fmt.Println("Tractor simulator is operational")
	select {} // Block forever
}

func setupSimulationServer() *grpc.Server {
	server := grpc.NewServer()

	// Register the tractor service implementation
	tractorService := NewHelloTractorSimulator()
	pb.RegisterHelloTractorServer(server, tractorService)

	fmt.Println("gRPC simulation server initialized")

	return server
}

// HelloTractorSimulator implements the drive.HelloTractorServer interface
type HelloTractorSimulator struct {
	mu             sync.Mutex
	currentSpeed   float64 // m/s
	currentHeading float64 // degrees (0 = north)
	position       *pb.GeoPoint
	safetyStatus   pb.SafetyStatus
}

func NewHelloTractorSimulator() *HelloTractorSimulator {
	return &HelloTractorSimulator{
		position: &pb.GeoPoint{Latitude: 37.7749, Longitude: -122.4194}, // San Francisco
		safetyStatus: pb.SafetyStatus{
			eStopActive: false,
			emergencyMode: false,
		},
	}
}

func (s *HelloTractorSimulator) Drive(ctx context.Context, cmd *pb.DriveCommand) (*pb.CommandResponse, error) {
	fmt.Printf("Received drive command: speed=%.2f, steer_angle=%.1f\n",
		cmd.Speed, cmd.SteerAngle)

	s.mu.Lock()
	defer s.mu.Unlock()

	if s.safetyStatus.EStopActive {
		return &pb.CommandResponse{
			status: pb.Status_ESTOP_ACTIVE,
			response_data: &pb.CommandResponse_SafetyStatus{&s.safetyStatus},
		}, nil
	}

	// Update simulation state based on command
	s.currentSpeed = cmd.Speed

	// Simple physics model for position update (stub)
	if s.position != nil {
		newHeading := normalizeAngle(s.currentHeading + (cmd.SteerAngle * 0.1))
		s.currentHeading = newHeading

		// Update position based on speed and heading
		distanceMoved := cmd.Speed * 0.5 // 0.5 second timestep for simulation
		if distanceMoved > 0 {
			radians := degToRad(newHeading)
			s.position.Latitude += (distanceMoved / EARTH_CIRCUMFERENCE_METERS) *
				cos(radians)
			s.position.Longitude += (distanceMoved / EARTH_CIRCUMFERENCE_METERS) /
				(cos(degToRad(s.position.Latitude)) * sin(radians))
		}
	}

	return &pb.CommandResponse{
		status: pb.Status_OK,
		response_data: &pb.CommandResponse_DriveStatus{&pb.DriveStatus{
			speed: s.currentSpeed,
			heading: s.currentHeading,
			position: s.position,
		}},
	}, nil
}

func (s *HelloTractorSimulator) Safety(ctx context.Context, cmd *pb.SafetyCommand) (*pb.CommandResponse, error) {
	fmt.Printf("Received safety command: e_stop_activate=%v, e_stop_release=%v\n",
		cmd.EStopActivate, cmd.EStopRelease)

	s.mu.Lock()
	defer s.mu.Unlock()

	if cmd.EStopActivate && !s.safetyStatus.EStopActive {
		s.safetyStatus.EStopActive = true
		s.currentSpeed = 0 // Emergency stop

		fmt.Println("EMERGENCY STOP ACTIVATED")
	} else if cmd.EStopRelease && s.safetyStatus.EStopActive {
		s.safetyStatus.EStopActive = false
		fmt.Println("Emergency stop released")
	}

	return &pb.CommandResponse{
		status: pb.Status_OK,
		response_data: &pb.CommandResponse_SafetyStatus{&s.safetyStatus},
	}, nil
}

func (s *HelloTractorSimulator) GetStatus(ctx context.Context, _ *empty.Empty) (*pb.DeviceStatusUpdate, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	return &pb.DeviceStatusUpdate{
		timestamp: timestamppb.Now(),
		position: s.position,
		current_speed: s.currentSpeed,
		current_heading: s.currentHeading,
		safety_status: &s.safetyStatus,
	}, nil
}

// Helper functions for simulation physics

const (
	EARTH_CIRCUMFERENCE_METERS = 40075016.8 // meters at equator
)

func degToRad(degrees float64) float64 {
	return degrees * (math.Pi / 180)
}

func radToDeg(radians float64) float64 {
	return radians * (180 / math.Pi)
}

func normalizeAngle(degrees float64) float64 {
	normalized := degrees % 360
	if normalized < 0 {
		normalized += 360
	}
	return normalized
}










