






















package server

import (
	"context"
	"fmt"

	"github.com/YOUR_USERNAME/rover-operations/contracts/proto/gen/go/control/v1"
	"github.com/YOUR_USERNAME/rover-operations/services/control-broker/internal/config"
	"google.golang.org/grpc"
)

type GRPCServer struct {
	cfg *config.Config
	srv *grpc.Server
}

func NewGRPCServer(cfg *config.Config) *GRPCServer {
	return &GRPCServer{
		cfg: cfg,
		srv: grpc.NewServer(),
	}
}

func (s *GRPCServer) Server() *grpc.Server {
	return s.srv
}

func (s *GRPCServer) Start() error {
	listenAddr := fmt.Sprintf("%s:%d", s.cfg.Host, s.cfg.Port)
	return s.srv.Serve(listenAddr)
}

func (s *GRPCServer) Stop() error {
	s.srv.GracefulStop()
	return nil
}

type ControlService struct {
	v1.UnimplementedControlServiceServer

	// Add fields for session management, policy engine client, etc.
}

func NewControlService() *ControlService {
	return &ControlService{}
}

// Example method implementation
func (s *ControlService) CreateSession(ctx context.Context, req *v1.CreateSessionRequest) (*v1.SessionResponse, error) {
	// Implementation would go here

	return &v1.SessionResponse{
		Status: "success",
	}, nil
}








