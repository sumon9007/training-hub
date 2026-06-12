#!/usr/bin/env bash
# Training Hub — Azure Static Web Apps deploy
# Usage: ./infra/deploy.sh [resource-group] [location]

set -euo pipefail

RESOURCE_GROUP="${1:-training-hub-rg}"
LOCATION="${2:-eastus2}"

echo "============================================================"
echo "  Training Hub — Azure SWA Deploy"
echo "  Resource Group : ${RESOURCE_GROUP}"
echo "  Location       : ${LOCATION}"
echo "============================================================"

# ── 1. Resource group ─────────────────────────────────────────────────────
echo ""
echo "[1/4] Ensuring resource group..."
az group create \
  --name "${RESOURCE_GROUP}" \
  --location "${LOCATION}" \
  --output none
echo "  ✓ ${RESOURCE_GROUP}"

# ── 2. Deploy Bicep ──────────────────────────────────────────────────────
echo ""
echo "[2/4] Deploying Bicep (Azure Static Web Apps)..."
DEPLOY_OUTPUT=$(az deployment group create \
  --resource-group "${RESOURCE_GROUP}" \
  --template-file "$(dirname "$0")/main.bicep" \
  --parameters location="${LOCATION}" environment=prod \
  --query "properties.outputs" \
  --output json)

SWA_NAME=$(echo "${DEPLOY_OUTPUT}" | python3 -c "import sys,json; print(json.load(sys.stdin)['swaName']['value'])")
SWA_HOST=$(echo "${DEPLOY_OUTPUT}" | python3 -c "import sys,json; print(json.load(sys.stdin)['swaDefaultHostname']['value'])")
DEPLOY_TOKEN=$(echo "${DEPLOY_OUTPUT}" | python3 -c "import sys,json; print(json.load(sys.stdin)['deploymentToken']['value'])")
MEDIA_STORAGE_NAME=$(echo "${DEPLOY_OUTPUT}" | python3 -c "import sys,json; print(json.load(sys.stdin)['mediaStorageAccountName']['value'])")

echo "  ✓ SWA name         : ${SWA_NAME}"
echo "  ✓ Hostname         : ${SWA_HOST}"
echo "  ✓ Media storage    : ${MEDIA_STORAGE_NAME}"

# Fetch storage key (not output via Bicep to avoid ARM deployment history exposure)
MEDIA_STORAGE_KEY=$(az storage account keys list \
  --resource-group "${RESOURCE_GROUP}" \
  --account-name "${MEDIA_STORAGE_NAME}" \
  --query "[0].value" --output tsv)
echo "  ✓ Storage key      : retrieved"

# ── 3. Upload site content ────────────────────────────────────────────────
echo ""
echo "[3/4] Uploading site content via SWA CLI..."
SITE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# SWA CLI v2: CWD must not be inside artifact folder; use ~ to avoid restricted dirs
cd ~
npx --yes @azure/static-web-apps-cli@latest deploy "${SITE_ROOT}" \
  --deployment-token "${DEPLOY_TOKEN}" \
  --swa-config-location "${SITE_ROOT}" \
  --env production
cd "${SITE_ROOT}"

echo "  ✓ Site files uploaded"

# ── 4. Save outputs to .env ──────────────────────────────────────────────
echo ""
echo "[4/4] Writing .env..."
ENV_FILE="${SITE_ROOT}/.env"
cat > "${ENV_FILE}" <<EOF
AZURE_RESOURCE_GROUP=${RESOURCE_GROUP}
AZURE_SWA_NAME=${SWA_NAME}
AZURE_SWA_URL=https://${SWA_HOST}
AZURE_SWA_DEPLOYMENT_TOKEN=${DEPLOY_TOKEN}
AZURE_MEDIA_STORAGE_ACCOUNT=${MEDIA_STORAGE_NAME}
AZURE_MEDIA_STORAGE_KEY=${MEDIA_STORAGE_KEY}
EOF
echo "  ✓ .env written"

echo ""
echo "============================================================"
echo "  Deploy complete!"
echo ""
echo "  Live URL       : https://${SWA_HOST}"
echo ""
echo "  Media storage  : https://${MEDIA_STORAGE_NAME}.blob.core.windows.net"
echo "  Containers     : diagrams / videos / questionbanks"
echo ""
echo "  Next — configure AAD auth:"
echo "    az staticwebapp appsettings set \\"
echo "      --name ${SWA_NAME} \\"
echo "      --setting-names AAD_CLIENT_ID=<value> AAD_CLIENT_SECRET=<value>"
echo ""
echo "  Upload a video:"
echo "    az storage blob upload --account-name ${MEDIA_STORAGE_NAME} \\"
echo "      --container-name videos --name az104/intro.mp4 --file ./intro.mp4"
echo ""
echo "  Upload a question bank:"
echo "    az storage blob upload --account-name ${MEDIA_STORAGE_NAME} \\"
echo "      --container-name questionbanks --name az104/questions.json --file ./questions.json"
echo "============================================================"
