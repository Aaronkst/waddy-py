# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables
ENV POETRY_VERSION=1.8.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install Poetry and required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc libpq-dev && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . /app

# Expose the application port
EXPOSE 8000

# Run the application using Uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
