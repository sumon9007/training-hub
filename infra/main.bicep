// Training Hub — Infrastructure
// Deploys two resources in one pass:
//   1. Azure Static Web Apps (Free) — hosts the site, enforces AAD auth routes
//   2. Storage Account (Standard_LRS) — private blob containers for diagrams, videos, question banks
//
// Usage: ./infra/deploy.sh [resource-group] [location]
// Custom domain: az staticwebapp hostname set --name <swa-name> --hostname <domain>

@description('Azure region for the SWA resource (limited regions; eastus2 recommended)')
param location string = 'eastus2'

@description('Environment tag')
param environment string = 'prod'

// ── Azure Static Web App ──────────────────────────────────────────────────

resource swa 'Microsoft.Web/staticSites@2022-09-01' = {
  name: 'traininghub-${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {}
  tags: {
    project: 'training-hub'
    environment: environment
  }
}

// ── Storage Account (media assets: diagrams, videos, question banks) ────

@description('Storage account name for course media assets (max 24 chars: 7 prefix + 13 uniqueString)')
param mediaStorageName string = 'thmedia${uniqueString(resourceGroup().id)}'

resource mediaStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: mediaStorageName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false    // all containers private; access via SAS only
    publicNetworkAccess: 'Enabled'
  }
  tags: { project: 'training-hub', environment: environment }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: mediaStorage
  name: 'default'
  properties: {
    cors: {
      corsRules: [
        {
          allowedOrigins: [
            'https://*.azurestaticapps.net'
            'http://localhost:4280'
            'http://localhost:8080'
          ]
          allowedMethods: ['GET', 'HEAD', 'OPTIONS']
          allowedHeaders: ['*']
          exposedHeaders: ['Content-Length', 'Content-Type']
          maxAgeInSeconds: 3600
        }
      ]
    }
  }
}

resource diagramsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'diagrams'
  properties: { publicAccess: 'None' }
}

resource videosContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'videos'
  properties: { publicAccess: 'None' }
}

resource questionbanksContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'questionbanks'
  properties: { publicAccess: 'None' }
}

// ── Outputs ───────────────────────────────────────────────────────────────

@description('Default SWA hostname (e.g. <random>.azurestaticapps.net)')
output swaDefaultHostname string = swa.properties.defaultHostname

@description('SWA resource name')
output swaName string = swa.name

@description('Deployment API key (used by CLI and GitHub Actions)')
#disable-next-line outputs-should-not-contain-secrets
output deploymentToken string = swa.listSecrets().properties.apiKey

@description('Resource group name')
output resourceGroupName string = resourceGroup().name

@description('Media storage account name')
output mediaStorageAccountName string = mediaStorage.name
