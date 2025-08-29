






package main

import (
	"fmt"
	"log"
	"time"

	"github.com/nats-io/nats.go"
	"google.golang.org/protobuf/proto"

	pb "github.com/YOUR_USERNAME/rover-operations/contracts/proto/control.proto"
)

func main() {
	fmt.Println("Starting Rover Operations Edge Agent...")

	// Initialize NATS connection
	natsConn, err := initializeNATS()
	if err != nil {
		log.Fatalf("Failed to connect to NATS: %v", err)
	}
	defer natsConn.Close()

	// Load device capabilities from configuration
	capabilities, err := loadDeviceCapabilities()
	if err != nil {
		log.Fatalf("Failed to load device capabilities: %v", err)
	}
	fmt.Printf("Loaded device capabilities: %+v\n", capabilities)

	// Start command listener
	go startCommandListener(natsConn, capabilities)

	// Start status reporter
	go startStatusReporter(natsConn, capabilities)

	// Main loop - keep the agent running
	fmt.Println("Edge Agent is operational. Press Ctrl+C to exit.")
	select {} // Block forever
}

func initializeNATS() (*nats.Conn, error) {
	// Connect to NATS server
	return nats.Connect(nats.DefaultURL)
}

func loadDeviceCapabilities() (*pb.DeviceCapabilityModel, error) {
	// Load capabilities from configuration file or embedded data
	return &pb.DeviceCapabilityModel{
		DeviceId: "hello-tractor-01",
		Model:    "HelloTractorSimulated",
		FirmwareVersion: "v1.0.0-beta",
	}, nil
}

func startCommandListener(natsConn *nats.Conn, capabilities *pb.DeviceCapabilityModel) {
	// Subscribe to command topics from control broker
	sub, err := natsConn.Subscribe("commands."+capabilities.GetDeviceId(), func(msg *nats.Msg) {
		fmt.Printf("Received command: %s\n", string(msg.Data))

		var cmd pb.Command
		if err := proto.Unmarshal(msg.Data, &cmd); err != nil {
			log.Printf("Failed to unmarshal command: %v", err)
			return
		}

		// Process the command and execute against driver plugin
		processCommand(cmd, capabilities)
	})
	if err != nil {
		log.Fatalf("Failed to subscribe to commands: %v", err)
	}
	defer sub.Unsubscribe()

	fmt.Println("Command listener started")
}

func startStatusReporter(natsConn *nats.Conn, capabilities *pb.DeviceCapabilityModel) {
	ticker := time.NewTicker(1 * time.Second)

	for range ticker.C {
		statusUpdate := generateStatusUpdate(capabilities)
		data, err := proto.Marshal(statusUpdate)
		if err != nil {
			log.Printf("Failed to marshal status update: %v", err)
			continue
		}

		if err := natsConn.Publish("telemetry."+capabilities.GetDeviceId(), data); err != nil {
			log.Printf("Failed to publish telemetry: %v", err)
		}
	}

	fmt.Println("Status reporter started")
}

func processCommand(cmd pb.Command, capabilities *pb.DeviceCapabilityModel) {
	// Process the command based on its type
	switch cmdType := cmd.GetCommandType().(type) {
	case *pb.Command_DriveCommand:
		fmt.Printf("Processing drive command: %+v\n", cmdType.DriveCommand)
		// Execute against driver plugin

	case *pb.Command_SafetyCommand:
		if cmdType.SafetyCommand.EStopActivate {
			fmt.Println("E-stop activated! Executing hard stop...")
			// Implement emergency stop logic
		}

	default:
		fmt.Printf("Unhandled command type: %T\n", cmdType)
	}
}

func generateStatusUpdate(capabilities *pb.DeviceCapabilityModel) *pb.DeviceStatusUpdate {
	// Generate a simulated status update
	return &pb.DeviceStatusUpdate{
		SessionId: "active-session-123",
		StatusType: &pb.DeviceStatusUpdate_DriveStatus{
			DriveStatus: &pb.DriveStatus{
				CurrentSpeed: 0.5, // Simulated speed (m/s)
				SteerAngle:   0.0,
				IsMoving:     false,
				EmergencyStopActive: false,

				Latitude:      37.7749, // San Francisco coordinates
				Longitude:     -122.4194,
				Altitude:      15.0,
				HeadingDegrees: 0.0,
			},
		},
	}
}





