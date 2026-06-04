# Use python:3.11-slim as base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (curl is needed for the healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to the container
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Healthcheck to verify service availability
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit command
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
