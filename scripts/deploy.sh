#!/bin/bash
# GCP Emotion Decoding Chatbot - Deployment Script
# This script deploys the chatbot to Google Cloud Run

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GCP Emotion Decoding Chatbot Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found. Please create one from .env.example${NC}"
    exit 1
fi

# Validate required environment variables
required_vars=("GCP_PROJECT_ID" "GCP_LOCATION" "SERVICE_NAME" "GCS_BUCKET_NAME")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Error: Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${GREEN}Project ID: $GCP_PROJECT_ID${NC}"
echo -e "${GREEN}Location: $GCP_LOCATION${NC}"
echo -e "${GREEN}Service Name: $SERVICE_NAME${NC}"
echo ""

# Set GCP project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Create GCS bucket if it doesn't exist
echo -e "${YELLOW}Checking GCS bucket...${NC}"
if ! gsutil ls -b gs://$GCS_BUCKET_NAME &> /dev/null; then
    echo -e "${YELLOW}Creating GCS bucket: $GCS_BUCKET_NAME${NC}"
    gsutil mb -p $GCP_PROJECT_ID -l $GCP_LOCATION gs://$GCS_BUCKET_NAME
    echo -e "${GREEN}Bucket created successfully${NC}"
else
    echo -e "${GREEN}Bucket already exists${NC}"
fi

# Build Docker image using Cloud Build
echo -e "${YELLOW}Building Docker image with Cloud Build...${NC}"
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME .

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $GCP_LOCATION \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_LOCATION=$GCP_LOCATION,GCS_BUCKET_NAME=$GCS_BUCKET_NAME,VERTEX_MODEL=$VERTEX_MODEL \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $GCP_LOCATION --format 'value(status.url)')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}Health Check: $SERVICE_URL/api/health${NC}"
echo ""
echo -e "${YELLOW}Test the deployment:${NC}"
echo -e "curl $SERVICE_URL/api/health"
echo ""

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
sleep 5
if curl -s -f "$SERVICE_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✓ Health check passed!${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi

echo -e "${GREEN}Deployment script completed!${NC}"
