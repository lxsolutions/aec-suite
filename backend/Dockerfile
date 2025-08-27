





# Use official Python image from the Poetry cache
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for psycopg2 and ifcopenshell
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry.lock and pyproject.toml first for cache efficiency
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies using Poetry
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Create a shell script to run the application with uvicorn
COPY docker-entrypoint.sh /usr/local/bin/

# Make the entrypoint executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["uvicorn", "backend.src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


