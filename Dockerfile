# Use an official FastAPI image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set the working directory
WORKDIR /

# Copy the application files
COPY . /

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI default port
EXPOSE 8000

# Run the application
CMD ["fastapi", "run", "src/gateway.py"]