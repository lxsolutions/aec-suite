





package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	fmt.Println("Starting Rover Operations Signaling Server...")

	r := mux.NewRouter()
	setupRoutes(r)

	fmt.Println("Signaling server listening on :8081")
	if err := http.ListenAndServe(":8081", r); err != nil {
		log.Fatalf("Failed to serve HTTP: %v", err)
	}
}

func setupRoutes(r *mux.Router) {
	r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Signaling Server is healthy"))
	})

	// WebRTC signaling endpoints
	r.HandleFunc("/signaling/offer", handleOffer).Methods("POST")
	r.HandleFunc("/signaling/answer", handleAnswer).Methods("POST")
	r.HandleFunc("/signaling/ice", handleICE).Methods("POST")

	// Room management endpoints (for future multi-device support)
	r.HandleFunc("/rooms", listRooms).Methods("GET")
	r.HandleFunc("/rooms/{roomId}", getRoomStatus).Methods("GET")
}

func handleOffer(w http.ResponseWriter, r *http.Request) {
	// TODO: Handle WebRTC offer from client
	fmt.Fprintf(w, "Received WebRTC offer")
}

func handleAnswer(w http.ResponseWriter, r *http.Request) {
	// TODO: Handle WebRTC answer from peer
	fmt.Fprintf(w, "Received WebRTC answer")
}

func handleICE(w http.ResponseWriter, r *http.Request) {
	// TODO: Handle ICE candidates exchange
	fmt.Fprintf(w, "Received ICE candidate")
}

func listRooms(w http.ResponseWriter, r *http.Request) {
	// TODO: List active signaling rooms
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("[]")) // Empty array for now
}

func getRoomStatus(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	roomId := vars["roomId"]
	fmt.Fprintf(w, "Status for room %s", roomId)
}




