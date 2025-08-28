






















package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"

	"github.com/YOUR_USERNAME/rover-operations/contracts/proto/gen/go/control/v1"
	"github.com/YOUR_USERNAME/rover-operations/edge/agent/internal/config"
	"github.com/YOUR_USERNAME/rover-operations/edge/agent/internal/server"
)

func main() {
	ctx := context.Background()

	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		slog.Error("Failed to load configuration", "error", err)
		os.Exit(1)
	}

	// Initialize logger with appropriate level and format
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level:   cfg.LogLevel,
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if a.Key == "time" && len(groups) > 0 && groups[0] == "error" {
				return slog.Attr{}
			}
			return a
		},
	}))

	slog.SetDefault(logger)
	slog.Info("Starting edge agent", "version", cfg.Version, "env", cfg.Environment)

	// Initialize gRPC client for control broker communication
	controlClient := server.NewControlBrokerClient(cfg.ControlBrokerURL)

	// Load device driver plugin
	driver, err := server.LoadDriverPlugin(ctx, cfg.DriverConfig)
	if err != nil {
		slog.Error("Failed to load driver plugin", "error", err)
		os.Exit(1)
	}

	agent := server.NewAgent(
		cfg,
		controlClient,
		driver,
	)

	// Start the agent
	err = agent.Start(ctx)
	if err != nil {
		slog.Error("Error starting edge agent", "error", err)
		os.Exit(1)
	}

	slog.Info("Edge agent started successfully")

	// Graceful shutdown on termination signals
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt)

	<-quit
	slog.Info("Shutting down edge agent...")

	if err := agent.Stop(); err != nil {
		slog.Error("Failed to stop edge agent gracefully", "error", err)
	}

	slog.Info("Edge agent stopped successfully")
}







