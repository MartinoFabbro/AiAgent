FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy entire project
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Default command to run Streamlit
CMD ["streamlit", "run", "app.py"]