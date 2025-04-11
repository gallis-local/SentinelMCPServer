# Use Python 3.8+ as the base image
FROM python:3.13-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code to the container
COPY . .

# Install the package in development mode
RUN pip install -e .

# Set environment variables
# These can be overridden at runtime
ENV MCP_CONNECTION_TYPE=stdio
ENV AUTHENTICATION_TYPE=client_secret

# Expose port 8000 for SSE and browser authentication
EXPOSE 8000

# Set up entrypoint
CMD ["python", "-m", "sentinel_mcp"]
