




package main

import (
	"fmt"
	"log"
	"net"

	"github.com/gorilla/mux"
	"google.golang.org/grpc"

	pb "github.com/YOUR_USERNAME/rover-operations/services/control-broker/pkg/api"
	"github.com/YOUR_USERNAME/rover-operations/services/control-broker/internal/server"
)

func main() {
	fmt.Println("Starting Rover Operations Control Broker...")

	// Initialize gRPC server
	grpcServer := grpc.NewServer()

	// Create control broker service implementation
	brokerService := server.NewControlBrokerService()
	pb.RegisterControlBrokerServer(grpcServer, brokerService)

	// Start gRPC server
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	go func() {
		fmt.Println("gRPC server listening on :50051")
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("Failed to serve gRPC: %v", err)
		}
	}()

	// Initialize REST API
	r := mux.NewRouter()
	setupRESTRoutes(r, brokerService)

	fmt.Println("Control Broker REST API listening on :8080")
	if err := http.ListenAndServe(":8080", r); err != nil {
		log.Fatalf("Failed to serve HTTP: %v", err)
	}
}

func setupRESTRoutes(r *mux.Router, service *server.ControlBrokerService) {
	r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Control Broker is healthy"))
	})

	// Add more REST endpoints as needed
}




