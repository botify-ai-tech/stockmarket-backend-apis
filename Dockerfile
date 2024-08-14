# Use the official Python base image
FROM python:3.11-slim
# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*
# Download and install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install
    
# Install Python TA-Lib package
RUN pip install ta-lib
# Set the working directory (optional)
WORKDIR /app
# Specify the command to run (optional)
CMD ["python3"]