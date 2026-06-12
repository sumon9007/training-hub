# Azure Fundamentals — Course Outline

## Course Overview
**Target Audience:** IT professionals, developers, and business users new to Azure and cloud computing
**Duration:** 4-5 hours
**Certification:** Microsoft Azure Fundamentals (AZ-900)
**Prerequisites:** Basic IT literacy — no prior cloud experience required

This course follows the **official AZ-900 exam blueprint**, organised into the three skills-measured
domains. Each module maps to one exam domain and carries its weighting. Hands-on labs are placed in
the domain where the skill is first applied.

---

## MODULE 1: Cloud Concepts
**Exam weighting:** 25–30%
Describe cloud computing, its benefits, and the cloud service and deployment models.

### Lesson 1: Cloud Computing & Benefits
- What is cloud computing? On-demand delivery of compute, storage, and networking over the internet
- Key characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service
- Business benefits: high availability, scalability (scale up/out), elasticity, agility, geo-distribution, disaster recovery
- Cloud reliability concepts: fault tolerance and the value of distributed infrastructure

### Lesson 2: CapEx, OpEx & the Consumption Model
- CapEx vs OpEx — shifting from capital to operational expenditure
- Consumption-based / pay-as-you-go model — pay only for what you use
- Total Cost of Ownership (TCO) and ROI of cloud adoption
- How the consumption model removes capacity-forecasting risk

### Lesson 3: Cloud Service Models & Shared Responsibility
- Infrastructure as a Service (IaaS) — most control; examples: Azure VMs, Azure Storage
- Platform as a Service (PaaS) — managed platform; examples: Azure App Service, Azure SQL
- Software as a Service (SaaS) — ready-to-use apps; examples: Microsoft 365, Dynamics 365
- Function as a Service (FaaS) / Serverless — Azure Functions
- Shared Responsibility Model — who manages what across IaaS / PaaS / SaaS
- Choosing the right service model for a workload

### Lesson 4: Cloud Deployment Models
- Public cloud — definition, benefits, when to use
- Private cloud — on-premises ownership, use cases (Azure Stack)
- Hybrid cloud — combining public and private; Azure Arc overview
- Multi-cloud — using multiple providers
- Comparison: cost, control, security, scalability across models

### LAB 1: Create a Free Microsoft Azure Account
- Prerequisites: Microsoft email account, credit card (identity verification only, not charged)
- Navigate to azure.microsoft.com/free and sign up with a Microsoft account
- Identity verification process
- Free tier benefits: $200 credit for 30 days, 55+ always-free services
- First look at the Azure portal: Home, All Services, Resource Groups, Subscriptions

### LAB 2: Switch to a Pay-As-You-Go Account
- When to upgrade from the free trial
- Navigate: portal.azure.com → Subscriptions → Upgrade
- Understand the Pay-As-You-Go billing model — no upfront commitment
- Pricing calculator overview — estimate costs before deploying
- Check current spend and forecasts

---

## MODULE 2: Azure Architecture & Services
**Exam weighting:** 35–40%
Describe the core architectural components of Azure and the main service categories.

### Lesson 1: Global Infrastructure
- Geographies, regions, and region pairs
- Availability Zones and datacenters
- Sovereign / specialised regions
- Choosing a region: latency, compliance, service availability, pricing

### Lesson 2: Azure Management Hierarchy & Resource Manager
- Management Groups → Subscriptions → Resource Groups → Resources
- Azure Resource Manager (ARM) — the deployment and management layer
- Resources, resource groups, and tagging basics
- How the hierarchy enables scaled governance

### Lesson 3: Compute Services
- Virtual Machines (IaaS) and VM scale sets
- Azure App Service (PaaS web apps)
- Azure Container Instances (ACI) and Azure Kubernetes Service (AKS)
- Azure Functions (serverless)
- Choosing the right compute option

### Lesson 4: Networking Services
- Virtual Network (VNet) and subnets
- VPN Gateway and ExpressRoute (hybrid connectivity)
- Azure DNS, Load Balancer, and CDN
- Public vs private endpoints

### Lesson 5: Storage Services
- Storage account services: Blob, Files, Queue, Table, Disk
- Access tiers: hot, cool, cold, archive
- Redundancy options: LRS, ZRS, GRS, GZRS
- Choosing storage for a workload

### Lesson 6: Identity, Access & Security
- Microsoft Entra ID (formerly Azure AD) — identities and tenants
- Authentication vs authorization
- Multi-Factor Authentication (MFA) and Single Sign-On (SSO)
- Conditional Access and Role-Based Access Control (RBAC)

---

## MODULE 3: Azure Management & Governance
**Exam weighting:** 30–35%
Describe cost management, governance and compliance, and the tools for managing and monitoring Azure.

### Lesson 1: Cost Management
- Factors affecting cost: resource type, region, bandwidth (egress), and consumption
- Pricing Calculator vs TCO Calculator — when to use each
- Azure Cost Management + Billing portal
- Budgets and cost alerts; ways to minimise cost (right-sizing, reservations, Azure Hybrid Benefit)

### Lesson 2: Governance & Compliance
- Azure Policy — enforce organisational rules and standards
- Resource locks — prevent accidental change or deletion
- Tags — organise resources and attribute cost
- Microsoft Cloud Adoption Framework for Azure
- Compliance: Microsoft Purview and the Service Trust Portal

### Lesson 3: Tools for Managing & Deploying
- Azure portal and Azure mobile app
- Azure CLI and Azure PowerShell
- Azure Cloud Shell
- Infrastructure as Code: ARM templates and Bicep

### Lesson 4: Monitoring Tools
- Azure Monitor — metrics, logs, alerts
- Log Analytics and Application Insights
- Azure Advisor — recommendations for cost, security, reliability, performance
- Azure Service Health — service issues and planned maintenance

### LAB 3: Create a Budget & Cost Alert in the Portal
- Navigate: portal.azure.com → Cost Management + Billing → Budgets
- Create a budget: amount, time period, reset period
- Configure alert conditions: % thresholds (e.g. 50%, 80%, 100%)
- Add alert recipients (email addresses)
- Review, create, and verify the alert appears in the Cost Management dashboard

### LAB 4: Set Up Azure CLI & Visual Studio Code
- Install Azure CLI (Windows MSI / `brew install azure-cli` / Linux curl script)
- Verify: `az --version`; sign in: `az login`
- Basic commands: `az account list`, `az group list`
- Install VS Code and the Azure extensions (Azure Account, Azure Resources, Bicep, Azure CLI Tools)
- Connect VS Code to your subscription and browse resources
