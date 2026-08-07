# --- Stage 1: Build & Dependency Installation ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install standard compiler dependencies if needed (e.g. system packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies to a local folder to easily copy
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Minimal Runtime Environment ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy installed libraries from the builder stage
COPY --from=builder /root/.local /home/appuser/.local
COPY main.py .

# Add local path to environment PATH variable so Python pulls from it
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Create a non-privileged system user and group
# Production best practice: Set explicit UID and GID (10001)
RUN groupadd -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup appuser

# Change ownership of application directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch executing context to the non-root user
USER 10001

EXPOSE 8000

# Start server using uvicorn binding to all interfaces on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
