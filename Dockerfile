FROM python:3-slim

# Install PostgreSQL client, development packages, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uwsgi

# Expose port
EXPOSE 8000

# Create a non-root user and use it
RUN useradd -m appuser
USER appuser

# Copy uWSGI configuration file
COPY uwsgi.ini /app/uwsgi.ini

# Command to run the application
CMD ["uwsgi", "--ini", "uwsgi.ini"]
