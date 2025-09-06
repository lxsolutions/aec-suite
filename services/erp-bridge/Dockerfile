

FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the libs directory for shared modules
COPY ../../libs/ ./libs/

# Copy the source code
COPY src/ .

# Set Python path to include libs directory
ENV PYTHONPATH=/app/libs:/app

CMD ["python", "main.py"]

