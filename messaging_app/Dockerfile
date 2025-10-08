# Use official Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Note: When running the container, use -p to map ports (e.g., -p 8000:8000)
# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

