# GCP Emotion Decoding Chatbot

Multimodal Emotion Decoding Chatbot powered by Google Cloud Vertex AI (Gemini Multimodal). It analyzes emotions from text and images and exposes clean REST APIs with a deployable Cloud Run service.

Repository owner: moatazalsbak
Project name: gcp-emotion-decoding-chatbot

Key features:
- Text emotion analysis (primary emotion, confidence, intensity, explanation)
- Image-based emotion analysis (facial cues, body language, context)
- Multimodal fusion (text + image consistency analysis)
- Flask REST API with /api/health, /api/analyze/text, /api/analyze/image, /api/analyze/multimodal
- Dockerized and ready for Cloud Run
- Scripts for one-click deployment and API testing
- Example configuration, troubleshooting, and verified links

Quick links:
- GitHub Repo: https://github.com/moatazalsbak/gcp-emotion-decoding-chatbot
- Vertex AI Docs: https://cloud.google.com/vertex-ai/docs
- Vertex AI Gemini Vision: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/overview
- Cloud Run Docs: https://cloud.google.com/run/docs
- Cloud Build Docs: https://cloud.google.com/build/docs


1) Repository Structure

- app.py                  Main Flask server integrating Vertex AI GenerativeModel
- Dockerfile              Production-ready image (multi-stage, non-root, healthcheck)
- requirements.txt        Python dependencies
- .env.example            Environment configuration template
- scripts/
  - deploy.sh             End-to-end deployment to Cloud Run via Cloud Build
  - test_api.py           Script to test all API endpoints with summary output

Add later if needed (optional):
- templates/              HTML templates for a simple web UI (index.html)
- static/                 Static assets (CSS/JS/images)
- config/                 Extra YAML/JSON configs
- data/                   Sample data and assets


2) Prerequisites

- A Google Cloud project with billing enabled: https://console.cloud.google.com/
- gcloud CLI installed: https://cloud.google.com/sdk/docs/install
- Python 3.10+ installed locally
- Service Account with roles: Vertex AI User, Storage Admin, Cloud Run Admin, Cloud Build Editor
  Docs: https://cloud.google.com/iam/docs/understanding-roles


3) Setup (Local)

- Clone the repo
  git clone https://github.com/moatazalsbak/gcp-emotion-decoding-chatbot.git
  cd gcp-emotion-decoding-chatbot

- Create and populate .env
  cp .env.example .env
  # Edit .env with your GCP project, region, bucket, etc.

- Create a service account key and export GOOGLE_APPLICATION_CREDENTIALS
  # Console: https://console.cloud.google.com/iam-admin/serviceaccounts
  # Create key (JSON) and download locally
  export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/sa-key.json

- Create and activate a virtual environment
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate

- Install dependencies
  pip install -r requirements.txt

- Run the app locally
  export PORT=8080
  python app.py

- Verify health
  curl http://localhost:8080/api/health


4) Vertex AI Configuration

- Enable Vertex AI API
  https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com

- Initialize Vertex AI in code
  app.py calls vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
  Ensure the env variables in .env are set and the service account has access.

- Model name
  The code uses GenerativeModel with MODEL_NAME=gemini-pro-vision for multimodal.
  Model catalog: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/overview


5) REST API Endpoints

Base URL (local): http://localhost:8080
Base URL (Cloud Run): provided after deploy (see scripts/deploy.sh output)

- GET /api/health
  Returns service, version, and timestamp.
  Example: curl http://localhost:8080/api/health

- POST /api/analyze/text
  Request: { "text": "I feel great and excited!" }
  Response: JSON with primary_emotion, confidence, intensity, explanation
  Example:
    curl -X POST -H "Content-Type: application/json" \
      -d '{"text":"I feel great and excited!"}' \
      http://localhost:8080/api/analyze/text

- POST /api/analyze/image
  Request: { "image": "<base64>" } or { "image_uri": "gs://bucket/path.jpg" }
  Response: JSON with detected emotions and visual cues

- POST /api/analyze/multimodal
  Request: { "text": "caption", "image": "<base64>" } or using image_uri
  Response: JSON with overall emotion, text-based and image-based emotions, consistency


6) Deployment (Cloud Run)

- Make sure gcloud is authenticated and project set
  gcloud auth login
  gcloud config set project YOUR_PROJECT_ID

- One-command deploy using our script
  chmod +x scripts/deploy.sh
  ./scripts/deploy.sh

  The script will:
  - Validate env (.env required)
  - Enable APIs (Cloud Build, Run, Vertex AI, Storage)
  - Create GCS bucket if missing
  - Build and push image with Cloud Build
  - Deploy to Cloud Run with sensible defaults
  - Print the service URL and a health check

- Manual commands (alternative)
  gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME .
  gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $GCP_LOCATION \
    --allow-unauthenticated

- After deploy: test health
  curl https://SERVICE_URL/api/health

Cloud Run docs: https://cloud.google.com/run/docs/deploying


7) Testing

- Local testing with the script
  python scripts/test_api.py --url http://localhost:8080 \
    --text "I am feeling very anxious today"

- Cloud Run testing
  python scripts/test_api.py --url https://SERVICE_URL \
    --text "The picture looks joyful" --image path/to/test.jpg

The script prints a summary of passed/failed tests with colored output.


8) Sample Output

- Health check
  {
    "status": "healthy",
    "service": "GCP Emotion Decoding Chatbot",
    "version": "1.0.0",
    "timestamp": "2025-10-28T10:00:00"
  }

- Text analysis (example, format may vary by model response)
  {
    "primary_emotion": "joy",
    "confidence": 92,
    "secondary_emotions": ["excitement"],
    "intensity": "high",
    "explanation": "Positive language with strong excitement"
  }


9) Troubleshooting

- Vertex AI init errors
  Ensure GOOGLE_APPLICATION_CREDENTIALS path is correct and SA has Vertex AI roles.
  Docs: https://cloud.google.com/vertex-ai/docs/start/cloud-environment

- Permission denied on GCS
  Grant Storage Admin or appropriate bucket permissions.
  Docs: https://cloud.google.com/storage/docs/access-control

- 403 on Cloud Run
  If not using --allow-unauthenticated, configure IAM for invoker role.
  Docs: https://cloud.google.com/run/docs/authenticating/public

- Large images timeout
  Increase --timeout in Cloud Run or reduce image size; adjust requests timeouts in scripts.

- Model not found or not available in region
  Verify VERTEX_MODEL and GCP_LOCATION; see model availability per region.
  https://cloud.google.com/vertex-ai/generative-ai/docs/learn/regions


10) Security and Costs

- Do not commit real credentials. Use .env and secrets managers where possible.
- Cloud Run and Vertex AI incur costs. Review pricing:
  - Vertex AI pricing: https://cloud.google.com/vertex-ai/pricing
  - Cloud Run pricing: https://cloud.google.com/run/pricing
  - Cloud Build pricing: https://cloud.google.com/build/pricing


11) Roadmap (Optional Enhancements)

- Add audio input support (speech emotion via embeddings + LLM reasoning)
- Add a simple web UI (templates/index.html)
- Add CI/CD with GitHub Actions
- Add structured JSON schema validation of model outputs


12) License

- Choose a license if you intend to open source (MIT, Apache-2.0, etc.)
  https://choosealicense.com/


Acknowledgements
- Google Cloud Vertex AI Gemini Multimodal: https://cloud.google.com/vertex-ai/generative-ai/docs
- Flask: https://flask.palletsprojects.com/
- Cloud Run: https://cloud.google.com/run
