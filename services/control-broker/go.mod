

module github.com/YOUR_USERNAME/rover-operations/services/control-broker

go 1.22

require (
    google.golang.org/protobuf v1.30.0
    github.com/nats-io/nats.go v1.17.0
    github.com/jackc/pgx/v5 v5.4.0
    github.com/gorilla/mux v1.8.0
    google.golang.org/grpc v1.62.0
)

replace (
    google.golang.org/protobuf => ../protobuf
)


