#!/bin/bash
# Deployment script for GCP Cloud Functions

# Set variables
FUNCTION_NAME="l3-options-trading"
REGION="us-central1"
RUNTIME="python311"
ENTRY_POINT="trading_handler"

echo "Deploying L3 Options Trading to GCP Cloud Functions..."

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=. \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --set-env-vars ALPACA_PAPER=true

echo "Deployment complete!"
echo "Function URL:"
gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format='value(serviceConfig.uri)'
