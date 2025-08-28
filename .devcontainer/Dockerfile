


FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    make \
    jq \
    yq \
    protobuf-compiler \
    libprotobuf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and pnpm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@9

# Install uv (modern Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Go
RUN curl -fsSL https://go.dev/dl/go1.22.0.linux-amd64.tar.gz | tar -C /usr/local -xzf -

# Install buf (protobuf tooling)
RUN curl -sSL "https://github.com/bufbuild/buf/releases/download/v1.30.0/buf-$(uname -s)-$(uname -m)" -o /usr/local/bin/buf && chmod +x /usr/local/bin/buf

# Install just (modern task runner)
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Set up environment
ENV PATH="/root/.cargo/bin:/usr/local/go/bin:/root/.local/bin:${PATH}"
ENV GOROOT=/usr/local/go
ENV GOPATH=/go

# Create workspace directory
WORKDIR /workspace

# Set up entrypoint
CMD ["sleep", "infinity"]


