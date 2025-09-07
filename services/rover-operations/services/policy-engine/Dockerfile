











# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install protobuf compiler and dependencies
RUN apk add --no-cache git \
    && rm -rf /var/cache/apk/*

COPY go.mod go.sum ./
RUN go mod download

COPY *.go */*.go ./proto/*.proto .

# Generate gRPC code from proto files
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest \
    && protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative ./proto/*.proto

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -o policy-engine -v .

# Runtime stage
FROM alpine:latest AS runtime

WORKDIR /app

COPY --from=builder /app/policy-engine .
COPY config.yaml ./

EXPOSE 50052

CMD ["./policy-engine", "--config", "config.yaml"]










