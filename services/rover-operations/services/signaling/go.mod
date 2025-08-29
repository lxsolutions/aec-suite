


module github.com/YOUR_USERNAME/rover-operations/services/signaling

go 1.22

require (
    google.golang.org/protobuf v1.30.0
    github.com/nats-io/nats.go v1.17.0
    github.com/pion/webrtc/v3 v3.4.5
    github.com/gorilla/mux v1.8.0
)

replace (
    google.golang.org/protobuf => ../protobuf
)



