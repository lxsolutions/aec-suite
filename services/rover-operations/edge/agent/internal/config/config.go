
























package config

import (
	"log/slog"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Environment string
	LogLevel    slog.Leveler
	Version     string
	Host        string
	Port        int
	ControlBrokerURL string

	// NATS configuration for policy updates and E-stop events
	NATSURLs       []string
	NATSPingPeriod time.Duration

	// Driver plugin configuration
	DriverConfig struct {
		Type      string // e.g., "hello-tractor"
		PluginPath string
	}
}

func LoadConfig() (*Config, error) {
	v := viper.New()
	v.SetEnvPrefix("EDGE_AGENT")
	v.AutomaticEnv()

	cfg := &Config{
		Environment: "development",
		LogLevel:    slog.LevelInfo,
		Version:     "0.1.0",
		Host:        "0.0.0.0",
		Port:        50053, // Different from control broker
		ControlBrokerURL: "localhost:50051",

		NATSURLs:       []string{"nats://localhost:4222"},
		NATSPingPeriod: time.Second * 5,

		DriverConfig: struct {
			Type      string
			PluginPath string
		}{
			Type:      "hello-tractor",
			PluginPath: "/app/plugins/hello-tractor.so", // For dynamic loading (Linux)
		},
	}

	v.BindEnv("ENVIRONMENT")
	v.BindEnv("LOG_LEVEL")
	v.BindEnv("VERSION")
	v.BindEnv("HOST")
	v.BindEnv("PORT")
	v.BindEnv("CONTROL_BROKER_URL")

	if err := v.Unmarshal(cfg); err != nil {
		return nil, err
	}

	slog.Info("Loaded edge agent configuration", "env", cfg.Environment)

	return cfg, nil
}









