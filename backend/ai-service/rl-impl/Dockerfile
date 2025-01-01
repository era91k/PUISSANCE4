# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and your code
COPY requirements.txt ./
COPY . ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the TensorBoard port
EXPOSE 6006

# Default command to run your script
CMD ["python", "train.py"]