include .env
export

# --- Configuration ---
GCLOUD_PROJECT_ID := $(GCLOUD_PROJECT_ID)	
SERVICE_NAME := learning-mcp
REGION       := europe-west1
SA_EMAIL     := $(SERVICE_ACCOUNT)
FOLDER_ID    := $(GDRIVE_FOLDER_ID)
FILE_ID      := $(GDRIVE_FILE_ID)

.PHONY: deploy
deploy: check-env
	@echo "🚀 Deploying $(SERVICE_NAME) to Cloud Run (Region: $(REGION))..."
	gcloud run deploy $(SERVICE_NAME) \
		--project $(GCLOUD_PROJECT_ID) \
		--source . \
		--no-allow-unauthenticated \
		--service-account $(SA_EMAIL) \
		--region $(REGION) \
		--set-env-vars GOOGLE_DRIVE_FOLDER_ID=$(FOLDER_ID),GOOGLE_DRIVE_FILE_ID=$(FILE_ID),LOG_LEVEL=INFO \
		--port 8080 \
		--timeout 3600 \
		--min-instances 0 \
		--max-instances 1
	@echo "✅ Deployment complete."
	@echo "🔗 Service URL: $$(gcloud run services describe $(SERVICE_NAME) --platform managed --region $(REGION) --format='value(status.url)')"

.PHONY: check-env
check-env:
	@if [ -z "$(SERVICE_ACCOUNT)" ]; then echo "❌ ERROR: SERVICE_ACCOUNT is not set in .env"; exit 1; fi
	@if [ -z "$(GDRIVE_FOLDER_ID)" ]; then echo "❌ ERROR: GDRIVE_FOLDER_ID is not set in .env"; exit 1; fi
	@echo "🔍 Environment Check: PASSED"

check-auth:
	@echo "🔐 Verifying GCP Authentication..."
	@gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q . || \
		(echo "❌ ERROR: No active GCP account found. Run 'gcloud auth login' first."; exit 1)
	@echo "🎯 Project Context: $(PROJECT_ID)"

.PHONY: logs
logs:
	gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$(SERVICE_NAME)" --limit 20 --order desc

.PHONY: proxy
proxy:
	@echo "🔌 Tunneling to $(SERVICE_NAME)..."
	gcloud run services proxy $(SERVICE_NAME) --port=8080 --region $(REGION)