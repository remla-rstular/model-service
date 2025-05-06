FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# TODO: work around having to install git - access release URL?
RUN apt-get update && \
apt-get install --no-install-recommends -y git && \
rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

ENV PORT=8000
EXPOSE ${PORT}

ARG SERVICE_VERSION="N/A"
ENV SERVICE_VERSION=${SERVICE_VERSION}

# Copy over requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the cache directory
RUN mkdir -p /root/.cache

# Copy over the rest of the files
COPY model_service ./model_service


CMD ["python3", "-m", "model_service"]
