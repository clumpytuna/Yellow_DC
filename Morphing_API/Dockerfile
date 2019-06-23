# Use an official Python runtime as a parent image
FROM python:3.7.2

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY ../requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["./run_ml.sh"]
