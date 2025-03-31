# Use Python 3.12 as the base image Selection <3.13 pour compatibalité et >=3.12 pour le formatage améliorer
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Tesseract OCR and other dependencies git pour pip install qui est parfois fais via gitub :S libgl1 pour cv2 libpqDev pour psycopg2 libzbar0 (pyzbar) build essential a gcc (pour build du code C) (et permettre a psycopg2 de fonctionner)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    git\
    libpq-dev \
    libgl1-mesa-glx \
    libzbar0 \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the FastAPI app using the `fastapi run` command
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]