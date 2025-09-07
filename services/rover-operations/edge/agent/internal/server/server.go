
























package server

import (
	"context"
	"fmt"

	"github.com/YOUR_USERNAME/rover-operations/contracts/proto/gen/go/control/v1"
)

type Agent struct {
	cfg           *config.Config
	controlClient v1.ControlServiceClient
	driver        Driver
}

func NewAgent(cfg *config.Config, controlClient v1.ControlServiceClient, driver Driver) *Agent {
	return &Agent{
		cfg:           cfg,
		controlClient: controlClient,
		driver:        driver,
	}
}

func (a *Agent) Start(ctx context.Context) error {
	// Initialize NATS connection for policy updates and E-stop events
	natsConn, err := connectToNATS(a.cfg.NATSURLs)
	if err != nil {
		return fmt.Errorf("failed to connect to NATS: %w", err)
	}

	go a.handlePolicyUpdates(ctx, natsConn)

	// Start WebRTC server for video/control data channel
	err = a.startWebRTCServer()
	if err != nil {
		return fmt.Errorf("failed to start WebRTC server: %w", err)
	}

	slog.Info("Edge agent started successfully")

	return nil
}

func (a *Agent) Stop() error {
	// Cleanup resources
	a.driver.Shutdown()

	return nil
}

// LoadDriverPlugin loads the device driver plugin based on configuration
func LoadDriverPlugin(ctx context.Context, cfg config.DriverConfig) (Driver, error) {
	switch cfg.Type {
	case "hello-tractor":
		return NewHelloTractorDriver(cfg.PluginPath)
	default:
		return nil, fmt.Errorf("unsupported driver type: %s", cfg.Type)
	}
}










