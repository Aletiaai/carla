# Stage 1: Build
# Using an official Python runtime as a parent image
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt



# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
# Create non root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed dependencies and app code
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app /home/appuser/.local

# Set environment variables
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PORT=8000 \
    WORKERS=4
# Switch to non-root user
USER appuser

#Expose and run
EXPOSE ${PORT}
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]