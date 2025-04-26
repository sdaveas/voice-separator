#!/bin/bash

# Google Cloud project details
PROJECT_ID="voice-separator-458012"
REGION="europe-southwest1"
SERVICE_NAME="voice-separator"

log_in() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q '@'; then
        echo "Not logged in. Authenticating..."
        gcloud auth login
    else
        echo "Already logged in as $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
    fi
}

enable_service_if_needed() {
  local service=$1
  
  if ! gcloud services list --enabled --filter="name:$service" --quiet | grep -q "$service"; then
    echo "Enabling $service..."
    gcloud services enable "$service"
  else
    echo "$service is already enabled."
  fi
}

log_in

echo "Setting project and region..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

echo "Enabling required services..."
enable_service_if_needed run.googleapis.com
enable_service_if_needed artifactregistry.googleapis.com
enable_service_if_needed cloudbuild.googleapis.com

gcloud projects add-iam-policy-binding 56847 \
  --member="user:br3gan187@gmail.com" \
  --role="roles/cloudbuild.buildViewer"

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --allow-unauthenticated

echo "Deployment complete! Visit the Cloud Run service URL to access your app." 