# Azure Administrator Associate — Course Outline
# AZ-104 Certification Track — aligned to the official AZ-104T00 course (6 Microsoft Learn learning paths)
# Grounded in the official study guide "Skills measured as of April 17, 2026"

## Course Overview
**Target Audience:** IT professionals, sysadmins, and cloud engineers moving into Azure administration
**Duration:** 16–20 hours (4-day instructor-led equivalent)
**Certification:** Microsoft Azure Administrator Associate (AZ-104) — pass mark 700/1000
**Prerequisites:** AZ-900 fundamentals or equivalent hands-on experience
**Exam Domains Covered:**
- Manage Azure identities and governance (20–25%)
- Implement and manage storage (15–20%)
- Deploy and manage Azure compute resources (20–25%)
- Implement and manage virtual networking (15–20%)
- Monitor and maintain Azure resources (10–15%)

---

## MODULE 0: Prerequisites — Azure Administration Tools
Mirrors learning path: *AZ-104: Prerequisites for Azure administrators*. No direct exam weight — tooling underpins every domain (ARM/Bicep skills are tested under Compute).
**Exam-Sim:** 5 questions · 8 min — coverage: tool selection portal vs CLI vs PowerShell (2), command completion az/Az cmdlets (2), management hierarchy (1)

### Lesson 1: The Azure Administrator Toolset
- The Azure administrator role: implement, manage, and monitor identity, governance, storage, compute, and networks
- Azure portal customization: dashboards, favorites, Cloud Shell from the portal
- Azure Cloud Shell: Bash vs PowerShell mode, persistent storage file share, timeout behavior
- When to use portal (one-off, visual) vs CLI/PowerShell (repeatable, scriptable) vs templates (declarative, idempotent)
- Management hierarchy recap: management groups → subscriptions → resource groups → resources
- Moving resources between resource groups and subscriptions — which resources can move, validation step
**Quiz:** Scenario — an admin must repeat the same 30-resource deployment in three environments with no configuration drift; pick the right tool (distractors: portal, ad-hoc CLI script, Cloud Shell session)
**Diagram:** png · management-hierarchy — Azure management hierarchy: management group → subscription → resource group → resources, with governance (policy/RBAC) inheritance arrows

### Lesson 2: Azure CLI & Azure PowerShell Essentials
- Azure CLI anatomy: `az <group> <subgroup> <verb>` — login, account set, output formats (json, table, tsv)
- JMESPath queries with `--query` for filtering output
- Az PowerShell module: `Connect-AzAccount`, Verb-AzNoun cmdlet pattern, `Get-AzContext`
- Idempotent scripting habits: `az group create` is safe to re-run; check-before-create patterns
- Choosing between Bash/CLI and PowerShell — team skills, OS, existing automation
- Common exam command patterns: complete-the-command questions
**Quiz:** Scenario — complete the CLI command to list only the names of VMs in a resource group as a flat list (distractors: wrong --query syntax, wrong output type, Get-AzVM mixed into az)
**Diagram:** none

### Lesson 3: ARM Templates & Bicep Fundamentals
- ARM template anatomy: $schema, parameters, variables, resources, outputs
- Bicep: declarative syntax over ARM JSON — modules, params, decompile/build
- Deployment modes: incremental (default) vs complete — the deleted-resources gotcha
- Deploying: `az deployment group create --template-file` / portal custom deployment
- Export a deployment as an ARM template; convert ARM JSON to Bicep with `az bicep decompile`
- Template specs for sharing templates inside an organization
**Quiz:** Scenario — a deployment in complete mode removed resources that weren't in the template; explain why and pick the prevention (distractors: RBAC, locks, incremental-mode misconceptions)
**Diagram:** mermaid · flowchart — Bicep → ARM JSON → ARM control plane → deployed resources pipeline, with decompile arrow back

### LAB 00: Environment Setup
**Objective:** Stand up a working admin toolchain — Cloud Shell, local CLI, and Bicep
**Est-Time:** 15 min
**Scenario:** New administrator onboarding: prepare the tools used in every later lab
**Steps:**
1. Open Cloud Shell from the portal (`>_` icon) — choose Bash, create the backing storage account
2. Switch Cloud Shell to PowerShell mode and back
3. Install Azure CLI locally and sign in
4. Install the Bicep tooling
5. Verify subscription context
**CLI:**
   az login
   az bicep install
   az account show --output table
**Expected-Output:** Table showing subscription name, ID, and "Enabled" state
**Validate:** `az account show --query user.name` returns your signed-in identity
**Cleanup:** None — keep the toolchain for all later labs

### LAB 03a: Manage Resources with Portal, PowerShell & CLI
**Objective:** Create the same resources three ways to build tool fluency
**Est-Time:** 20 min
**Scenario:** The exam tests command completion in both az CLI and Az PowerShell — build muscle memory by creating one resource group + managed disk per tool
**Steps:**
1. Portal: `Resource groups → Create` — name `az104-rg1`, region East US
2. Portal: create a Standard SSD managed disk in `az104-rg1`
3. PowerShell (Cloud Shell): create `az104-rg2` and a disk with `New-AzResourceGroup` / `New-AzDisk`
4. CLI (Cloud Shell Bash): create `az104-rg3` and a disk
**CLI:**
   az group create --name az104-rg3 --location eastus
   az disk create --resource-group az104-rg3 --name az104-disk3 --sku StandardSSD_LRS --size-gb 32
**Expected-Output:** JSON with `"provisioningState": "Succeeded"` for both commands
**Validate:** `az group list --query "[?starts_with(name,'az104-rg')].name" --output tsv` lists all three groups
**Cleanup:** `az group delete --name az104-rg1 --yes --no-wait` (repeat for rg2, rg3)

---

## MODULE 1: Manage Azure Identities & Governance
Mirrors learning path: *AZ-104: Manage identities and governance in Azure*.
**Exam weight: 20–25%**
**Exam-Sim:** 8 questions · 12 min — coverage: Entra users/groups/licenses (2), external users + SSPR (1), RBAC roles and scopes (2), Policy effects and remediation (2), locks/tags/cost (1)

### Lesson 1: Microsoft Entra ID for Administrators
- Microsoft Entra ID vs on-premises AD DS vs Microsoft Entra Domain Services — what each provides
- Tenants and directories; how subscriptions trust exactly one tenant
- Entra ID editions: Free vs P1 vs P2 — which admin features need which license
- Users: cloud identities, directory-synchronized identities, guest (external) users
- Administrative units — scoping admin permissions to a subset of users/groups
**Quiz:** Scenario — an app needs legacy Kerberos/NTLM auth in Azure without deploying domain controllers; pick the right identity service (distractors: Entra ID alone, AD DS on a VM, B2C)
**Diagram:** mermaid · flowchart — Entra tenant → users/groups/devices/apps relationships, with subscription trust arrow

### Lesson 2: Users, Groups & Licenses
- Creating users: portal, bulk CSV upload, `az ad user create`, New-MgUser
- Manage user and group properties; usage location requirement before license assignment
- Group types: Security vs Microsoft 365; membership: Assigned vs Dynamic User vs Dynamic Device
- Dynamic membership rules: syntax `(user.department -eq "IT")`, processing delay gotcha
- Manage licenses in Entra ID: direct vs group-based licensing, license conflict resolution
- Manage external users: B2B guest invitations, redemption, guest access restrictions
**Quiz:** Scenario — 200 contractors must automatically receive a license while in the Contractors department and lose it when they leave; pick the mechanism (distractors: direct assignment, M365 group, manual PowerShell)
**Diagram:** none

### Lesson 3: Self-Service Password Reset & Secure Access
- SSPR enablement scopes: None / Selected / All — group-based rollout
- Authentication methods: mobile app notification/code, email, phone; number required to reset
- SSPR licensing: cloud-only free for cloud users; writeback needs P1
- Registration: combined security info registration with MFA
- MFA at the level AZ-104 tests: enabling, per-user vs Conditional Access awareness
**Quiz:** Scenario — pilot SSPR for only the Helpdesk group with two required methods; pick the configuration steps (distractors: enable All, per-user MFA, password protection)
**Diagram:** none

### Lesson 4: Azure RBAC
- RBAC model: security principal + role definition + scope = role assignment
- Built-in roles the exam loves: Owner, Contributor, Reader, User Access Administrator + service-specific (VM Contributor, Storage Blob Data Reader)
- Assign roles at management group / subscription / resource group / resource scope — inheritance downward
- Interpret access assignments: effective permissions are the UNION of assignments; Deny assignments win
- Azure RBAC vs Entra ID directory roles — resource plane vs directory plane
- Least privilege: narrowest built-in role at the narrowest scope (custom roles are out of scope for the current exam)
**Quiz:** Scenario — a contractor needs to view resources in one resource group only, least privilege; pick role + scope (distractors: Reader@subscription, Contributor@RG, Global Reader directory role)
**Diagram:** png · rbac-scope-chain — RBAC inheritance: management group → subscription → resource group → resource, with a role assignment at RG scope and inheritance arrows

### Lesson 5: Azure Policy, Locks & Tags
- Azure Policy vs RBAC: what gets created (governance) vs who can act (access)
- Policy definitions → initiatives → assignments; assignment scope and exclusions
- Effects: Deny, Audit, AuditIfNotExists, DeployIfNotExists, Modify, Append — exam decision points
- Remediation tasks: fixing existing non-compliant resources (DINE/Modify need a managed identity)
- Resource locks: ReadOnly vs CanNotDelete — inheritance, the ReadOnly-breaks-list-keys gotcha
- Tags: apply/manage on resources and RGs; tags do NOT inherit by default — enforce/inherit via Policy
**Quiz:** Scenario — every new resource must get the cost-center tag copied from its resource group automatically; pick effect type (distractors: Deny, Audit, Append)
**Diagram:** mermaid · flowchart — Policy evaluation flow: assignment → evaluation → effect (compliant / deny / audit / remediate)

### Lesson 6: Subscriptions, Management Groups & Cost Management
- When to use multiple subscriptions: billing separation, policy boundaries, scale limits
- Management groups: up to 6 levels, root MG, design patterns (by department / by environment)
- Moving resources across resource groups and subscriptions — validation, GUID stays, region does NOT change
- Cost Management: cost analysis views, budgets with action-group alerts, exports
- Azure Advisor recommendation categories: cost, security, reliability, operational excellence, performance
**Quiz:** Scenario — finance demands an alert at 80% of a monthly spend threshold per subscription plus recommendations to downsize idle VMs; pick the tool combination (distractors: Monitor metric alerts only, Policy, Activity log)
**Diagram:** none

### LAB 01: Manage Microsoft Entra ID Identities
**Objective:** Create and manage users, groups, and a guest account
**Est-Time:** 20 min
**Scenario:** Onboard a new team: two users, one security group with dynamic membership, one external consultant
**Steps:**
1. Portal: `Microsoft Entra ID → Users → New user` — create `az104-user1` with Usage location set
2. Create a security group `IT Lab Administrators` with Assigned membership; add user1
3. Create a dynamic user group with rule `(user.jobTitle -eq "IT Lab Administrator")`
4. Update user1's job title and watch dynamic membership populate (allow a few minutes)
5. Invite an external user via `Users → New user → Invite external user`
**CLI:**
   az ad user create --display-name "az104-user1" --user-principal-name az104-user1@$TENANT_DOMAIN --password "ProvideAStrongOne!" --force-change-password-next-sign-in true
   az ad group create --display-name "IT Lab Administrators" --mail-nickname itlabadmins
**Expected-Output:** JSON containing the new user's `objectId` and the group's `id`
**Validate:** `az ad group member list --group "IT Lab Administrators" --query "[].displayName"` includes az104-user1
**Cleanup:** Delete the lab users and groups from `Microsoft Entra ID → Users / Groups` (or `az ad user delete --id ...`)

### LAB 02a: Subscriptions & RBAC
**Objective:** Assign a built-in role at resource-group scope and interpret effective access
**Est-Time:** 15 min
**Scenario:** Grant the IT Lab Administrators group rights to manage VMs in one resource group only, then prove what they can and cannot do
**Steps:**
1. Portal: create resource group `az104-rbac-rg`
2. `az104-rbac-rg → Access control (IAM) → Add role assignment` — role: Virtual Machine Contributor → assign to IT Lab Administrators
3. Review `Access control (IAM) → Check access` for az104-user1
4. Observe inherited assignments from subscription scope in the Role assignments tab
**CLI:**
   az role assignment create --assignee "<group-object-id>" --role "Virtual Machine Contributor" --resource-group az104-rbac-rg
**Expected-Output:** JSON with `"scope": ".../resourceGroups/az104-rbac-rg"` and the roleDefinitionId
**Validate:** `az role assignment list --resource-group az104-rbac-rg --output table` shows the group with Virtual Machine Contributor
**Cleanup:** `az role assignment delete --assignee "<group-object-id>" --resource-group az104-rbac-rg` then delete the RG

### LAB 02b: Governance via Azure Policy
**Objective:** Enforce tagging with Azure Policy and remediate non-compliant resources
**Est-Time:** 20 min
**Scenario:** Finance requires every resource to carry a `costcenter` tag; existing untagged resources must be fixed automatically
**Steps:**
1. Portal: `Policy → Definitions` — find built-in "Inherit a tag from the resource group if missing"
2. Assign at resource-group scope with tag name `costcenter`; enable a system-assigned managed identity (Modify effect)
3. Tag the resource group itself: `costcenter = lab`
4. Create an untagged storage account in the RG
5. Create a remediation task from `Policy → Remediation` and confirm the tag appears
**CLI:**
   az policy assignment create --name inherit-costcenter --policy "ea3f2387-9b95-492a-a190-fcdc54f7b070" --resource-group az104-policy-rg --mi-system-assigned --location eastus --params '{"tagName":{"value":"costcenter"}}'
**Expected-Output:** JSON assignment with `"provisioningState": "Succeeded"` and an `identity` block
**Validate:** `az policy state list --resource-group az104-policy-rg --query "[?complianceState=='NonCompliant'] | length(@)"` returns 0 after remediation
**Cleanup:** `az policy assignment delete --name inherit-costcenter --resource-group az104-policy-rg` then delete the RG

---

## MODULE 2: Implement & Manage Storage
Mirrors learning path: *AZ-104: Implement and manage storage in Azure*.
**Exam weight: 15–20%**
**Exam-Sim:** 6 questions · 9 min — coverage: redundancy selection (1), blob tiers + lifecycle (2), SAS vs access keys vs RBAC (2), Azure Files identity-based access (1)

### Lesson 1: Storage Accounts & Redundancy
- Storage account kinds: Standard general-purpose v2 vs Premium (block blobs / file shares / page blobs)
- Redundancy: LRS (3 copies, 1 DC) / ZRS (3 AZs) / GRS & GZRS (paired region, RA- variants) — durability vs cost
- Which redundancy survives what: rack failure, zone outage, region outage; customer-initiated failover
- Endpoints: `<account>.blob.core.windows.net` naming, custom domains
- Storage account encryption: Microsoft-managed keys vs customer-managed keys in Key Vault, infrastructure encryption
- Object replication for block blobs: async copy between accounts, requires versioning + change feed
**Quiz:** Scenario — data must survive a complete region outage AND allow read access from the secondary at all times; pick redundancy (distractors: LRS, ZRS, GRS without RA)
**Diagram:** png · storage-redundancy-map — LRS/ZRS in primary region vs GRS/GZRS async replication to paired region, with RA read endpoint

### Lesson 2: Azure Blob Storage
- Blob types: block (objects), append (logs), page (disks) — when each applies
- Containers and the flat namespace; public access levels (and the account-level disable switch)
- Access tiers: Hot / Cool / Cold / Archive — minimum retention days, rehydration from Archive (Standard vs High priority)
- Lifecycle management policies: tier-down and delete rules on last-modified/created, rule filters
- Data protection: blob versioning vs snapshots, soft delete for blobs and containers
**Quiz:** Scenario — compliance logs read monthly for 90 days, then kept 7 years untouched, lowest cost; pick the tier + lifecycle design (distractors: Hot forever, Cool only, manual scripts)
**Diagram:** mermaid · flowchart — blob lifecycle: Hot → Cool → Cold → Archive with min-days annotations and rehydrate path back

### Lesson 3: Storage Security & Access Control
- Access keys: two keys for rotation, why they're root-level credentials, Key Vault rotation
- SAS types: account SAS vs service SAS vs user delegation SAS (Entra-signed, blob-only) — permissions, expiry, IP ranges
- Stored access policies: server-side revocation for service SAS — the exam's revocation answer
- Storage firewall: default deny, allowed VNets/IPs, trusted Microsoft services exception
- Entra ID (RBAC) authorization for blobs/queues: Storage Blob Data Reader/Contributor; when to prefer over SAS
**Quiz:** Scenario — a partner got a 6-month service SAS that must be revoked TODAY without breaking other clients; pick the mechanism (distractors: regenerate both keys, delete container, firewall rule)
**Diagram:** png · private-endpoint-storage — VNet with private endpoint to storage account (private DNS zone) vs service endpoint path vs public endpoint blocked by firewall

### Lesson 4: Azure Files & File Sync
- Azure Files: SMB and NFS shares; Standard vs Premium tiers; quota and large file shares
- Identity-based access for Azure Files: Entra Kerberos for hybrid identities, AD DS auth, share-level RBAC + NTFS ACLs
- Snapshots and soft delete for file shares
- Azure File Sync: storage sync service → sync group → server endpoint; cloud tiering with volume free space policy
- Mapping a drive: port 445 gotcha, storage account key vs identity auth
**Quiz:** Scenario — branch office file server is full; users need full namespace locally with cold files in the cloud; pick the solution (distractors: blob + AzCopy, bigger disk, NFS share mount)
**Diagram:** mermaid · flowchart — File Sync topology: Azure file share ↔ sync group ↔ on-prem server endpoints with cloud tiering

### Lesson 5: Data Management Tools — AzCopy & Storage Explorer
- AzCopy: `azcopy copy` and `azcopy sync`, auth via Entra login vs SAS, resume support
- AzCopy sync semantics: --delete-destination, last-modified comparison
- Azure Storage Explorer: managing blobs/files/queues/tables visually, attaching with SAS or account key
- Choosing the transfer approach: portal upload vs AzCopy vs Storage Explorer vs Data Box (awareness)
**Quiz:** Scenario — nightly one-way mirror of an on-prem folder to a blob container, deleted files must disappear in the cloud too; pick command + flags (distractors: azcopy copy, robocopy, Storage Explorer manual)
**Diagram:** none

### LAB 07: Manage Azure Storage
**Objective:** Configure a storage account end-to-end: redundancy, tiers, SAS, lifecycle, AzCopy
**Est-Time:** 25 min
**Scenario:** Stand up the storage platform for a department: secure blob container, a delegated-access file drop, and automatic cost tiering
**Steps:**
1. Portal: create storage account `az104stor<unique>` — Standard GPv2, ZRS, East US
2. Create container `data` (private access); upload a sample file
3. Generate a read-only service SAS on the file with a 1-hour expiry; test in a private browser window
4. Add a lifecycle rule: move blobs to Cool after 30 days, delete after 365
5. Upload a folder with AzCopy from Cloud Shell
**CLI:**
   az storage account create --name az104stor$RANDOM --resource-group az104-stor-rg --location eastus --sku Standard_ZRS --kind StorageV2
   azcopy copy "./labdata" "https://<account>.blob.core.windows.net/data?<SAS>" --recursive
**Expected-Output:** AzCopy summary line: `Number of Transfers Completed: <n>` with 0 failed
**Validate:** `az storage blob list --container-name data --account-name <account> --auth-mode login --query "length(@)"` matches the uploaded count
**Cleanup:** `az group delete --name az104-stor-rg --yes --no-wait`

---

## MODULE 3: Deploy & Manage Azure Compute Resources
Mirrors learning path: *AZ-104: Deploy and manage Azure compute resources*.
**Exam weight: 20–25%**
**Exam-Sim:** 8 questions · 12 min — coverage: ARM/Bicep interpretation + deployment (2), VM disks/encryption/move (2), availability + VMSS (1), App Service plans/slots/TLS (2), containers ACR/ACI/Container Apps (1)

### Lesson 1: Automating Deployment with ARM & Bicep
- Interpret an ARM template / Bicep file: resources, dependsOn, parameters with defaults, outputs
- Modify existing templates: add a resource, parameterize a hard-coded value
- Deploy: `az deployment group create`, `New-AzResourceGroupDeployment`, portal Template specs
- Export deployment → ARM template; `az bicep decompile` to convert JSON to Bicep
- What-if preview before deploying — catching destructive changes
**Quiz:** Scenario — given a Bicep snippet with a parameterized VM size and a hard-coded admin username, pick the modification that lets each environment vary the username (distractors: variable, output, dependsOn)
**Diagram:** none

### Lesson 2: Azure Virtual Machines
- VM families and sizes (B, D, E, F, etc.); resizing — when a restart/deallocation is required
- Managed disk types: Standard HDD / Standard SSD / Premium SSD / Ultra — IOPS and SLA implications
- Disk encryption options: SSE with PMK/CMK, Azure Disk Encryption (BitLocker/dm-crypt), encryption at host — exam distinctions
- Move a VM to another resource group, subscription, or region (Resource Mover / snapshot for region)
- VM extensions, boot diagnostics, run command
**Quiz:** Scenario — security mandates that ALL disk data including temp/cache disks is encrypted with platform keys end-to-end; pick the feature (distractors: ADE, SSE alone, double encryption at rest)
**Diagram:** none

### Lesson 3: VM Availability & Scale
- Availability sets: fault domains vs update domains; 99.95% SLA
- Availability zones: zonal deployment, 99.99% SLA, zone-redundant services
- Virtual Machine Scale Sets: Uniform vs Flexible orchestration; instance count limits
- Autoscale rules: metric-based (CPU > 70% → +1) and schedule-based; scale-in protection
- Choosing: single VM + premium SSD SLA vs availability set vs zones vs VMSS
**Quiz:** Scenario — a stateless web tier must survive a datacenter (zone) outage AND scale from 2 to 10 instances on CPU; pick the deployment (distractors: availability set, two standalone zonal VMs, App Service mention)
**Diagram:** png · vm-availability-options — side-by-side: availability set (FD/UD) vs availability zones vs VMSS across zones with load balancer

### Lesson 4: App Service Plans & Scaling
- App Service plan tiers: Free/Shared, Basic, Standard, Premium v3, Isolated — features per tier (slots, autoscale, VNet)
- Plan = compute boundary: all apps in a plan share instances; scale up (tier) vs scale out (instances)
- Autoscale for plans: rules + limits, Standard and above; Premium per-app scaling awareness
- Cost levers: consolidating apps per plan, scaling down off-hours
**Quiz:** Scenario — an app needs deployment slots and autoscale at the lowest cost tier; pick the plan (distractors: Free, Basic, Premium v3 when Standard suffices)
**Diagram:** none

### Lesson 5: Configuring App Service
- Deployment slots: swap with warm-up, slot-sticky (deployment slot settings) vs swapped settings, auto-swap
- Map an existing custom DNS name: CNAME vs A record + TXT verification, domain verification ID
- Certificates and TLS: App Service managed certificate (free), Key Vault certs, SNI vs IP SSL bindings, minimum TLS version
- Backup for App Service: requirements (Standard+), what's included, partial backups, restore
- Networking settings: access restrictions, VNet integration (outbound), private endpoints (inbound), hybrid connections
**Quiz:** Scenario — production web app must be reachable ONLY through a private IP from the corporate VNet, including stopping public access; pick the configuration (distractors: VNet integration alone, access restriction allow-list only, service endpoint)
**Diagram:** png · appservice-slots — App Service plan with production + staging slots, swap arrow, slot-sticky settings annotation, traffic % routing

### Lesson 6: Containers — ACR, ACI & Container Apps
- Azure Container Registry: Basic/Standard/Premium tiers (geo-replication = Premium), `az acr build`, ACR Tasks
- Authentication to ACR: admin account vs Entra service principal vs managed identity
- Azure Container Instances: container groups, multi-container sidecars, restart policies, vCPU/memory sizing
- Azure Container Apps: built on AKS, revisions, ingress, scale-to-zero with KEDA triggers, Dapr awareness
- Sizing & scaling comparison: ACI (fixed per group) vs Container Apps (autoscaling 0→N) — and the ACI vs Container Apps vs AKS decision
**Quiz:** Scenario — an event-driven worker should scale to zero between queue bursts with minimal ops; pick the service (distractors: ACI, AKS, VMSS)
**Diagram:** png · container-pipeline — dev pushes image → ACR build/tasks → deploy targets: ACI (fixed) and Container Apps (KEDA autoscale 0..N)

### LAB 03b: Deploy with ARM Templates & Bicep
**Objective:** Deploy and modify infrastructure as code, then export and convert
**Est-Time:** 20 min
**Scenario:** Standardize disk deployments: parameterize a template, deploy via CLI, convert the result to Bicep
**Steps:**
1. Portal: deploy a managed disk, then `Export template` from the deployment blade
2. Edit the exported template: parameterize the disk name and size
3. Redeploy the edited template with new parameter values via CLI
4. Decompile the ARM JSON to Bicep and review the syntax difference
5. Deploy the Bicep file with a third disk name
**CLI:**
   az deployment group create --resource-group az104-iac-rg --template-file ./azuredeploy.json --parameters diskName=az104-disk2 diskSizeGb=64
   az bicep decompile --file ./azuredeploy.json
**Expected-Output:** Deployment JSON `"provisioningState": "Succeeded"`; decompile writes `azuredeploy.bicep`
**Validate:** `az disk list --resource-group az104-iac-rg --query "[].name"` lists all deployed disks
**Cleanup:** `az group delete --name az104-iac-rg --yes --no-wait`

### LAB 08: Manage Virtual Machines
**Objective:** Deploy zone-resilient VMs, resize, add a data disk, and scale with VMSS
**Est-Time:** 30 min
**Scenario:** Build the compute tier for a line-of-business app: zonal VM with data disk, then a scale set that autoscales on CPU
**Steps:**
1. Portal: create VM `az104-vm1` in availability zone 1 (Standard_B2s, no public inbound ports)
2. Resize the VM to Standard_B2ms and note the restart
3. Add and initialize a 32 GiB data disk
4. Create a VMSS `az104-vmss1` across zones 1–3 with a load balancer, 2 instances
5. Add a CPU autoscale rule: scale out at 70%, max 4 instances
**CLI:**
   az vm create --resource-group az104-vm-rg --name az104-vm1 --image Ubuntu2204 --size Standard_B2s --zone 1 --admin-username azureuser --generate-ssh-keys --public-ip-address ""
   az vmss create --resource-group az104-vm-rg --name az104-vmss1 --image Ubuntu2204 --zones 1 2 3 --instance-count 2 --orchestration-mode Flexible --admin-username azureuser --generate-ssh-keys
**Expected-Output:** VM JSON with `"zones": ["1"]`; VMSS JSON with `"provisioningState": "Succeeded"`
**Validate:** `az vmss list-instances --resource-group az104-vm-rg --name az104-vmss1 --query "length(@)"` returns 2
**Cleanup:** `az group delete --name az104-vm-rg --yes --no-wait`

### LAB 09a: Implement Web Apps
**Objective:** Deploy a web app with a staging slot, swap, and autoscale
**Est-Time:** 25 min
**Scenario:** Zero-downtime releases for a customer-facing site: stage the new version, validate, swap to production
**Steps:**
1. Portal: create App Service plan (Standard S1) + web app `az104-web<unique>`
2. Add a deployment slot `staging`
3. Deploy sample code to the staging slot
4. Mark one app setting as a deployment slot setting (sticky) and observe it not swapping
5. Swap staging → production; verify the new version serves
6. Add an autoscale rule: scale out at 70% CPU, instance limits 1–3
**CLI:**
   az webapp deployment slot create --name az104-web1 --resource-group az104-web-rg --slot staging
   az webapp deployment slot swap --name az104-web1 --resource-group az104-web-rg --slot staging --target-slot production
**Expected-Output:** Swap completes with no error; production URL serves the staged content
**Validate:** `az webapp show --name az104-web1 --resource-group az104-web-rg --query state` returns "Running"
**Cleanup:** `az group delete --name az104-web-rg --yes --no-wait`

### LAB 09b: Azure Container Instances
**Objective:** Build an image into ACR and run it as a container group
**Est-Time:** 20 min
**Scenario:** Package a utility container and run it on demand without managing any VM
**Steps:**
1. Create an Azure Container Registry (Basic)
2. Build and push a sample image with `az acr build` (no local Docker needed)
3. Deploy the image to Azure Container Instances with 1 vCPU / 1.5 GiB, public DNS label
4. Browse to the FQDN and confirm the app responds
**CLI:**
   az acr create --resource-group az104-cont-rg --name az104acr$RANDOM --sku Basic --admin-enabled true
   az acr build --registry <acrName> --image sampleapp:v1 https://github.com/Azure-Samples/acr-build-helloworld-node.git
   az container create --resource-group az104-cont-rg --name az104-aci1 --image <acrName>.azurecr.io/sampleapp:v1 --cpu 1 --memory 1.5 --registry-username <user> --registry-password <pass> --dns-name-label az104aci$RANDOM --ports 80
**Expected-Output:** `az container create` JSON with `"provisioningState": "Succeeded"` and an `ipAddress.fqdn`
**Validate:** `az container show --resource-group az104-cont-rg --name az104-aci1 --query instanceView.state` returns "Running"
**Cleanup:** `az group delete --name az104-cont-rg --yes --no-wait`

### LAB 09c: Azure Container Apps
**Objective:** Deploy a Container App with HTTP ingress and scale rules
**Est-Time:** 20 min
**Scenario:** Run the same image as a scale-to-zero microservice with revision-based releases
**Steps:**
1. Create a Container Apps environment
2. Deploy a container app from a public sample image with external ingress on port 80
3. Set scale rule: min 0, max 3 replicas on HTTP concurrency
4. Update the image to create a second revision; split traffic 50/50
**CLI:**
   az containerapp env create --name az104-cae --resource-group az104-ca-rg --location eastus
   az containerapp create --name az104-app1 --resource-group az104-ca-rg --environment az104-cae --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest --target-port 80 --ingress external --min-replicas 0 --max-replicas 3
**Expected-Output:** JSON containing `properties.configuration.ingress.fqdn`
**Validate:** `curl -s -o /dev/null -w "%{http_code}" https://<fqdn>` returns 200
**Cleanup:** `az group delete --name az104-ca-rg --yes --no-wait`

---

## MODULE 4: Implement & Manage Virtual Networking
Mirrors learning path: *AZ-104: Configure and manage virtual networks for Azure administrators*.
**Exam weight: 15–20%**
**Exam-Sim:** 7 questions · 11 min — coverage: VNet/subnet/IP planning (1), NSG effective rules (2), DNS zones (1), peering + UDR routing (1), Bastion/service/private endpoints (1), LB vs App Gateway (1)

### Lesson 1: Virtual Networks, Subnets & IP Addressing
- VNet address space planning: RFC1918 CIDR, non-overlapping ranges for future peering
- Subnets: Azure reserves 5 IPs per subnet; subnet delegation; gateway/Bastion subnet naming requirements
- Public IP addresses: Basic vs Standard SKU (zones, default-deny), static vs dynamic allocation
- Public IP prefixes; outbound connectivity options awareness (NAT Gateway)
- Troubleshoot connectivity: IP conflicts, exhausted subnets, wrong SKU pairings (Standard LB needs Standard PIP)
**Quiz:** Scenario — a /27 subnet keeps failing to fit 30 VMs; explain why and pick the fix (distractors: NSG, DHCP settings, peering)
**Diagram:** none

### Lesson 2: Network Security Groups & ASGs
- NSG anatomy: priority 100–4096, lower wins, first match stops processing; default rules
- NSG associations: subnet vs NIC — both evaluated (inbound: subnet then NIC)
- Application security groups: grouping VMs by role, ASG-to-ASG rules instead of IP lists
- Evaluate effective security rules: Network Watcher / NIC effective rules blade
- Classic gotchas: intra-subnet traffic is NOT filtered by default rules; AllowVNetInBound includes peered VNets
**Quiz:** Scenario — web VMs must accept 443 from the internet, app VMs only 8080 from web VMs, no IP-based rules allowed; pick the design (distractors: per-NIC NSGs with IPs, one permissive NSG, Azure Firewall)
**Diagram:** mermaid · flowchart — inbound NSG evaluation order: internet → subnet NSG → NIC NSG → VM, with deny/allow branches

### Lesson 3: Azure DNS & Name Resolution
- Public DNS zones: delegation with NS records at the registrar, record sets (A, CNAME, MX, TXT), alias records
- Private DNS zones: VNet links, auto-registration of VM records
- Azure-provided DNS (168.63.129.16) vs custom DNS servers vs private zones — resolution decision
- Split-brain DNS scenario: same zone name public + private
**Quiz:** Scenario — VMs in two peered VNets must resolve each other by hostname automatically, no servers to manage; pick the solution (distractors: public zone, custom DNS VM, hosts files)
**Diagram:** none

### Lesson 4: VNet Peering & Routing
- VNet peering: regional + global, non-transitive nature, allow forwarded traffic / gateway transit options
- System routes; effective routes per NIC
- User-defined routes: route tables, next-hop types (Virtual appliance, VNet gateway, Internet, None)
- Forcing traffic through an NVA/firewall in a hub: UDR 0.0.0.0/0 → firewall private IP
- Troubleshoot connectivity: Network Watcher connection troubleshoot, next-hop test
**Quiz:** Scenario — spoke1 and spoke2 are each peered to a hub but can't reach each other; explain why and pick the fix (distractors: NSG, DNS, re-create peering)
**Diagram:** png · hub-spoke-topology — hub VNet (firewall, Bastion, VPN gateway) with two peered spokes, UDRs forcing spoke→spoke via firewall

### Lesson 5: Secure VNet Access — Bastion, Service & Private Endpoints
- Azure Bastion: browser-based RDP/SSH over 443, AzureBastionSubnet, Basic vs Standard SKU features
- Service endpoints: subnet identity to PaaS over Azure backbone — service stays on public IP, firewall by VNet
- Private endpoints: a NIC with a private IP for the PaaS resource + private DNS zone requirement
- Service endpoint vs private endpoint decision: cost, on-prem reachability, data exfiltration protection
**Quiz:** Scenario — on-premises clients over VPN must reach a storage account by private IP with public access disabled; pick the feature (distractors: service endpoint, firewall allow rule, peering)
**Diagram:** none

### Lesson 6: Load Balancing — Azure LB & Application Gateway
- Azure Load Balancer (L4): public vs internal, Basic vs Standard SKU, backend pools, health probes, LB rules vs NAT rules
- Session persistence and the five-tuple hash; HA ports for NVAs
- Application Gateway (L7): listeners, routing rules, path-based routing, backend pools, WAF awareness
- Troubleshoot load balancing: probe failures (NSG blocking probe IP 168.63.129.16), unhealthy backend symptoms
- Decision: LB (any TCP/UDP, cheapest) vs App Gateway (HTTP routing, TLS offload, WAF) — Front Door/Traffic Manager are no longer in the AZ-104 skills list (awareness only)
**Quiz:** Scenario — route /api/* and /images/* to different VM pools with TLS termination; pick the service (distractors: internal LB, public LB + NAT, Traffic Manager)
**Diagram:** png · lb-multitier — public LB → web tier subnet (NSG), internal LB → app tier subnet (NSG), health probes annotated

### LAB 04: Implement Virtual Networking
**Objective:** Build a VNet with secured subnets, ASG-based rules, and a private DNS zone
**Est-Time:** 25 min
**Scenario:** Foundation network for a two-tier app: web and app subnets, role-based NSG rules, internal name resolution
**Steps:**
1. Portal: create VNet `az104-vnet1` 10.60.0.0/16 with subnets `web` 10.60.1.0/24 and `app` 10.60.2.0/24
2. Create ASGs `asg-web` and `asg-app`
3. Create NSG `nsg-web`: allow 443 from Internet to asg-web; associate to the web subnet
4. Create NSG `nsg-app`: allow 8080 from asg-web to asg-app, deny other VNet inbound; associate to app subnet
5. Create private DNS zone `corp.internal`, link to the VNet with auto-registration
**CLI:**
   az network vnet create --resource-group az104-net-rg --name az104-vnet1 --address-prefix 10.60.0.0/16 --subnet-name web --subnet-prefix 10.60.1.0/24
   az network private-dns zone create --resource-group az104-net-rg --name corp.internal
   az network private-dns link vnet create --resource-group az104-net-rg --zone-name corp.internal --name vnet1-link --virtual-network az104-vnet1 --registration-enabled true
**Expected-Output:** Each create returns `"provisioningState": "Succeeded"`
**Validate:** `az network nsg rule list --nsg-name nsg-web --resource-group az104-net-rg --output table` shows the 443 allow rule
**Cleanup:** `az group delete --name az104-net-rg --yes --no-wait`

### LAB 05: Implement Intersite Connectivity
**Objective:** Peer VNets and verify routing with effective routes
**Est-Time:** 20 min
**Scenario:** Connect the app VNet to a management VNet and prove traffic flows by checking effective routes
**Steps:**
1. Create a second VNet `az104-vnet2` 10.62.0.0/16 with one subnet and a test VM in each VNet (no public IPs)
2. Create bidirectional peering between vnet1 and vnet2
3. Review peering state = Connected on both sides
4. Inspect effective routes on the VM NIC — note the VNetPeering route
5. Test connectivity with Network Watcher connection troubleshoot
**CLI:**
   az network vnet peering create --name vnet1-to-vnet2 --resource-group az104-net-rg --vnet-name az104-vnet1 --remote-vnet az104-vnet2 --allow-vnet-access
   az network nic show-effective-route-table --resource-group az104-net-rg --name <vm1-nic> --output table
**Expected-Output:** Route table includes a `VNetPeering` source route for 10.62.0.0/16
**Validate:** Network Watcher connection troubleshoot VM1 → VM2 private IP reports `Reachable`
**Cleanup:** Delete both peerings, the second VNet, and the test VMs (or delete the whole RG in LAB 04 cleanup)

### LAB 06: Implement Traffic Management
**Objective:** Stand up an internal load balancer and an Application Gateway with path-based routing
**Est-Time:** 30 min
**Scenario:** Distribute intranet traffic across two app VMs, then route /images/* and /video/* paths to different pools through App Gateway
**Steps:**
1. Deploy two small VMs with a web server in the app subnet
2. Create internal Standard Load Balancer `az104-ilb` with frontend 10.60.2.100, backend pool = both VMs
3. Add health probe (TCP 80) and LB rule (80 → 80)
4. Create subnet `appgw` 10.60.3.0/24 and an Application Gateway (Standard_v2) with path-based rule: /images/* → pool1, /video/* → pool2
5. Test both paths from a jump VM
**CLI:**
   az network lb create --resource-group az104-net-rg --name az104-ilb --sku Standard --vnet-name az104-vnet1 --subnet app --frontend-ip-name fe1 --private-ip-address 10.60.2.100 --backend-pool-name bepool
   az network lb probe create --resource-group az104-net-rg --lb-name az104-ilb --name probe80 --protocol Tcp --port 80
**Expected-Output:** LB JSON with the static private frontend IP; probe `"provisioningState": "Succeeded"`
**Validate:** `curl http://10.60.2.100` from the jump VM alternates between both backend hostnames
**Cleanup:** `az group delete --name az104-net-rg --yes --no-wait`

---

## MODULE 5: Monitor & Maintain Azure Resources
Mirrors learning path: *AZ-104: Monitor and back up Azure resources*.
**Exam weight: 10–15%**
**Exam-Sim:** 5 questions · 8 min — coverage: metrics vs logs + diagnostic settings (1), alerts/action groups/processing rules (2), Recovery Services vs Backup vault (1), ASR failover (1)

### Lesson 1: Azure Monitor — Metrics & Logs
- Azure Monitor data platform: metrics (numeric, near-real-time) vs logs (KQL, rich queries)
- Interpret metrics: metrics explorer, aggregations, splitting by dimension
- Diagnostic settings: routing resource logs/metrics to Log Analytics, storage, Event Hubs — per-resource requirement
- Log Analytics workspace design: access control, retention settings, regions
- Activity log: control-plane audit trail, 90-day retention, export via diagnostic settings
**Quiz:** Scenario — NSG flow decisions and storage account transactions must be queryable together for 180 days; pick the configuration (distractors: metrics retention, activity log alone, per-resource portal views)
**Diagram:** png · monitor-data-flow — resources/agents → metrics + logs → Log Analytics workspace → alerts → action group → email/SMS/webhook/automation

### Lesson 2: Alerts & Incident Response
- Alert rule anatomy: scope + condition (signal) + action group; alert states and severity
- Alert types: metric (near-real-time), log search (scheduled KQL), activity log (service health, resource events)
- Action groups: notifications (email/SMS/push/voice) and actions (runbook, function, webhook, ITSM)
- Alert processing rules: suppress during maintenance windows, add action groups at scale — the post-firing layer
- Stateful (auto-resolve) vs stateless alerts
**Quiz:** Scenario — suppress all VM alerts every Saturday 02:00–06:00 maintenance without editing 40 alert rules; pick the feature (distractors: disable rules, modify action group, Logic App)
**Diagram:** none

### Lesson 3: KQL & Azure Monitor Insights
- KQL essentials for admins: `where`, `summarize`, `count`, `top`, `project`, time ranges
- Common admin queries: Heartbeat gaps, Perf CPU, event search
- Azure Monitor Insights: VM insights (performance + dependency map), storage insights, network insights
- Workbooks: parameterized dashboards over workspace data
**Quiz:** Scenario — complete the KQL to find the 5 VMs with highest average CPU over 24h (distractors: wrong summarize/order combination, metrics explorer, where-only query)
**Diagram:** none

### Lesson 4: Network Watcher & Connection Monitor
- Network Watcher tools: IP flow verify, next hop, NSG diagnostics, effective security rules, topology
- Packet capture on VMs; VPN troubleshoot
- Connection monitor: continuous source→destination reachability tests with latency trends
- Flow logs: NSG flow logs / VNet flow logs into storage + traffic analytics
**Quiz:** Scenario — intermittent latency from an app VM to a SQL endpoint must be tracked continuously with alerting; pick the tool (distractors: IP flow verify, one-off connection troubleshoot, packet capture)
**Diagram:** none

### Lesson 5: Azure Backup
- Recovery Services vault vs Backup vault — which workloads each protects (IaaS VM/SQL-in-VM/Files vs blobs/disks/PostgreSQL) — mandatory exam distinction
- Backup policies: schedule + retention (GFS); enhanced policy for hourly/Trusted Launch
- VM backup and restore: full VM restore, disk restore, file-level recovery mounting
- Soft delete for backups; security features (immutability, MUA awareness)
- Configure and interpret backup reports and alerts (needs Log Analytics + diagnostic settings)
**Quiz:** Scenario — protect Azure VMs AND Azure Files with one vault, plus managed-disk snapshots and blob protection elsewhere; pick which vault type protects what (distractors: single vault for all, Backup vault for VMs)
**Diagram:** png · backup-asr-flow — Recovery Services vault: backup policy path (VM → restore points) and ASR replication path (region A VM → region B failover)

### Lesson 6: Azure Site Recovery
- ASR for Azure VMs: replicate region-to-region; RPO vs RTO definitions
- Enable replication: cache storage account, target region resources, replication policy
- Test failover (isolated VNet, zero production impact) vs planned/unplanned failover vs failback
- Recovery plans: ordered multi-VM failover with scripts
- Backup vs ASR decision: point-in-time restore vs business continuity
**Quiz:** Scenario — prove DR readiness quarterly without touching production workloads; pick the operation (distractors: unplanned failover, restore from backup, redeploy)
**Diagram:** none

### LAB 10: Implement Data Protection
**Objective:** Back up a VM, restore a file, and enable ASR replication
**Est-Time:** 25 min
**Scenario:** Meet the new BC/DR policy: daily VM backups with 30-day retention and cross-region replication for the critical app VM
**Steps:**
1. Portal: create a Recovery Services vault `az104-rsv` (note: separate RG recommended)
2. Create a backup policy: daily 02:00, retain 30 days; enable backup for the lab VM
3. Run an on-demand backup; watch the job complete
4. Perform file-level recovery: mount the recovery point and copy one file
5. Enable Site Recovery replication for the VM to a secondary region; review replication health
**CLI:**
   az backup vault create --resource-group az104-bcdr-rg --name az104-rsv --location eastus
   az backup protection enable-for-vm --resource-group az104-bcdr-rg --vault-name az104-rsv --vm az104-vm1 --policy-name DefaultPolicy
   az backup job list --resource-group az104-bcdr-rg --vault-name az104-rsv --output table
**Expected-Output:** Job list shows a Backup job with Status `Completed` (or InProgress initially)
**Validate:** `az backup item list --resource-group az104-bcdr-rg --vault-name az104-rsv --query "[0].properties.protectionState"` returns "Protected" (IRPending immediately after enable)
**Cleanup:** Disable protection with data deletion, disable replication, then delete the vault and RG (vault deletion fails while items are protected)

### LAB 11: Implement Monitoring
**Objective:** Wire up diagnostic settings, a KQL log alert, an action group, and an alert processing rule
**Est-Time:** 25 min
**Scenario:** Ops needs an email when any lab VM CPU exceeds 80%, suppressed during the Sunday maintenance window, with logs queryable in one workspace
**Steps:**
1. Create Log Analytics workspace `az104-law`
2. Enable VM insights / diagnostic settings on the lab VM targeting the workspace
3. Create an action group `ag-ops` with an email notification
4. Create a metric alert: CPU > 80% for 5 minutes → ag-ops
5. Create an alert processing rule that suppresses notifications Sundays 01:00–05:00
6. Query the workspace: top processes / heartbeat KQL
**CLI:**
   az monitor log-analytics workspace create --resource-group az104-mon-rg --workspace-name az104-law
   az monitor action-group create --resource-group az104-mon-rg --name ag-ops --short-name agops --email-receiver name=ops email=ops@example.com
   az monitor metrics alert create --name cpu80 --resource-group az104-mon-rg --scopes <vm-resource-id> --condition "avg Percentage CPU > 80" --window-size 5m --action ag-ops
**Expected-Output:** Each create returns `"provisioningState": "Succeeded"`; alert rule shows `"enabled": true`
**Validate:** `az monitor metrics alert show --name cpu80 --resource-group az104-mon-rg --query criteria` shows the 80% CPU condition
**Cleanup:** `az group delete --name az104-mon-rg --yes --no-wait`

---

## MODULE 6: Exam Preparation & Review
Consolidation module — no new exam content. The final exam simulator is weight-proportional across all five domains.
**Exam-Sim:** 20 questions · 30 min — coverage: identities & governance (5), storage (3), compute (5), networking (4), monitoring & backup (3) — mirror the real domain weighting

### Lesson 1: Exam Strategy & Format
- Exam logistics: ~40–60 questions, 100 minutes, 700/1000 to pass, no penalty for guessing
- Question types: multiple choice, multiple response, drag-and-drop, hot area, case studies, command completion
- Case study technique: read the questions first, then mine the scenario tabs
- Domain prioritization by weight: identities + compute are half the exam
- Renewal: free online assessment yearly on Microsoft Learn
**Quiz:** Scenario — time-boxing strategy question: 8 minutes left, a case study and 5 standalone questions remain; pick the order (distractors: case study first, skip all, random)
**Diagram:** mermaid · pie — AZ-104 domain weighting pie chart (use midpoints: identities 22, storage 17, compute 22, networking 17, monitoring 12)

### Lesson 2: Decision Matrices — Rapid Review
- Redundancy: LRS / ZRS / GRS / GZRS / RA-GZRS — failure domains each survives
- VM resilience: availability set vs zone vs VMSS — SLA ladder 99.95 / 99.99
- Load balancing: Azure LB (L4) vs Application Gateway (L7 + WAF) — Front Door/Traffic Manager off-exam awareness
- Storage access: access key vs account SAS vs service SAS + stored access policy vs user delegation SAS vs RBAC
- Connectivity to PaaS: public + firewall vs service endpoint vs private endpoint
- Vaults: Recovery Services (VMs, SQL-in-VM, Files) vs Backup vault (blobs, disks, PostgreSQL)
- Retired from the skills list — know they exist, don't deep-study: ExpressRoute, Virtual WAN, Front Door, custom RBAC roles, Blueprints (deprecated)
**Quiz:** Scenario — matrix question: pick the ONE row that is wrong in a service-selection table (distractors are plausible matrix rows)
**Diagram:** mermaid · flowchart — load-balancing decision tree: HTTP? path routing? WAF? → App Gateway; else internal/public LB

### Lesson 3: Architecture Walkthroughs
- Walkthrough 1 — multi-tier web app: VMSS web tier behind App Gateway, internal LB to app tier, zone resilience, NSGs per subnet
- Walkthrough 2 — hub-and-spoke governance: management groups, Policy at MG scope, hub firewall + Bastion, spoke workloads
- Walkthrough 3 — monitoring & BC/DR: diagnostic settings → Log Analytics, alerts + processing rules, RSV backups + ASR to paired region
- For each: trace a user request / an audit requirement / a failure through the diagram
**Quiz:** Scenario — given the multi-tier architecture, identify the single point of failure (distractors: components that are actually zone-redundant)
**Diagram:** png · multitier-reference — full reference architecture: App Gateway (WAF) → VMSS web tier across zones → internal LB → app tier → storage + monitoring + backup, NSGs and private endpoints annotated
