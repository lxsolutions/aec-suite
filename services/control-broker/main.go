




















package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"

	"github.com/YOUR_USERNAME/rover-operations/contracts/proto/gen/go/control/v1"
	"github.com/YOUR_USERNAME/rover-operations/services/control-broker/internal/config"
	"github.com/YOUR_USERNAME/rover-operations/services/control-broker/internal/server"
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
	slog.Info("Starting control-broker service", "version", cfg.Version, "env", cfg.Environment)

	// Initialize gRPC server
	grpcServer := server.NewGRPCServer(cfg)

	// Register services
	v1.RegisterControlServiceServer(grpcServer.Server(), server.NewControlService())

	slog.Info("gRPC server listening", "address", fmt.Sprintf("%s:%d", cfg.Host, cfg.Port))

	// Start the server in a goroutine
	go func() {
		if err := grpcServer.Start(); err != nil {
			slog.Error("Failed to start gRPC server", "error", err)
			os.Exit(1)
		}
	}()

	// Graceful shutdown on termination signals
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt)

	<-quit
	slog.Info("Shutting down control-broker service...")

	if err := grpcServer.Stop(); err != nil {
		slog.Error("Failed to stop gRPC server gracefully", "error", err)
	}

	slog.Info("Control-broker service stopped successfully")
}






