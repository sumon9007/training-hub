#!/usr/bin/env python3
"""Generate AZ-104 lab HTML pages → courses/az104/labs/lab-{id}.html"""

import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent
OUT = ROOT / "courses" / "az104" / "labs"
OUT.mkdir(parents=True, exist_ok=True)

# ── Colour palette per node type ──────────────────────────────────────────────
NODE_C = {
    "identity": ("#001835", "#0078D4", "#60BAFF"),
    "network":  ("#001526", "#0063B1", "#4DC3FF"),
    "compute":  ("#1A0A2E", "#7B2FBE", "#C08AFF"),
    "storage":  ("#002020", "#00B7C3", "#00D4E0"),
    "govern":   ("#00180E", "#107C10", "#40C040"),
    "monitor":  ("#180B22", "#5C2E91", "#C08AFF"),
    "app":      ("#001827", "#0062AD", "#40A8FF"),
    "backup":   ("#0A1A0A", "#107C10", "#40C040"),
    "default":  ("#0d1926", "#334155", "#94A3B8"),
}

GROUP_C = {
    "identity": "#0078D4", "network": "#0063B1", "compute": "#7B2FBE",
    "storage":  "#00B7C3", "govern":  "#107C10",  "monitor": "#5C2E91",
    "app":      "#0062AD", "backup":  "#107C10",  "default": "#334155",
}


def diagram(nodes, edges, groups=None, w=520, h=300):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'style="background:#080e18;border-radius:12px;display:block;font-family:system-ui,sans-serif">',
        '<defs><marker id="ah" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">'
        '<path d="M0,1 L0,6 L6,3.5 z" fill="#475569"/></marker></defs>',
    ]

    # Groups behind nodes
    for g in (groups or []):
        col = GROUP_C.get(g.get("type", "default"), "#334155")
        parts.append(
            f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="10" '
            f'fill="{col}0a" stroke="{col}35" stroke-width="1" stroke-dasharray="5,3"/>'
        )
        parts.append(
            f'<text x="{g["x"]+10}" y="{g["y"]+15}" fill="{col}90" '
            f'font-size="9" font-weight="700" letter-spacing="0.08em">{g["label"].upper()}</text>'
        )

    # Node position lookup
    np_ = {n["id"]: n for n in nodes}

    # Edges
    for e in edges:
        fn, tn = np_[e["from"]], np_[e["to"]]
        fw, fh = fn.get("w", 120), fn.get("h", 44)
        tw, th = tn.get("w", 120), tn.get("h", 44)
        x1, y1 = fn["x"] + fw // 2, fn["y"] + fh // 2
        x2, y2 = tn["x"] + tw // 2, tn["y"] + th // 2
        dash = ' stroke-dasharray="5,3"' if e.get("dashed") else ""
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#475569" stroke-width="1.5" marker-end="url(#ah)"{dash}/>'
        )
        lbl = e.get("label", "")
        if lbl:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2 - 5
            parts.append(
                f'<text x="{mx}" y="{my}" fill="#64748B" font-size="9" text-anchor="middle">{lbl}</text>'
            )

    # Nodes
    for n in nodes:
        x, y, nw, nh = n["x"], n["y"], n.get("w", 120), n.get("h", 44)
        bg, border, fg = NODE_C.get(n.get("type", "default"), NODE_C["default"])
        label, sub = n["label"], n.get("sub", "")
        parts.append(
            f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="7" '
            f'fill="{bg}" stroke="{border}" stroke-width="1.5"/>'
        )
        ty = y + nh // 2 + (-4 if sub else 4)
        parts.append(
            f'<text x="{x+nw//2}" y="{ty}" fill="{fg}" font-size="11" '
            f'font-weight="600" text-anchor="middle">{label}</text>'
        )
        if sub:
            parts.append(
                f'<text x="{x+nw//2}" y="{y+nh//2+12}" fill="#64748B" '
                f'font-size="9" text-anchor="middle">{sub}</text>'
            )

    parts.append("</svg>")
    return "".join(parts)


# ── Per-lab accent colours (hex, r,g,b string) ────────────────────────────────
ACCENT_MAP = {
    "lab-01":  ("#38BDF8", "56,189,248"),    # sky
    "lab-02a": ("#34D399", "52,211,153"),    # emerald
    "lab-02b": ("#2DD4BF", "45,212,191"),    # teal
    "lab-03a": ("#60A5FA", "96,165,250"),    # blue
    "lab-03b": ("#818CF8", "129,140,248"),   # indigo
    "lab-03c": ("#A78BFA", "167,139,250"),   # violet
    "lab-03d": ("#C084FC", "192,132,252"),   # purple
    "lab-04":  ("#22D3EE", "34,211,238"),    # cyan
    "lab-05":  ("#FCD34D", "252,211,77"),    # amber
    "lab-06":  ("#FB923C", "251,146,60"),    # orange
    "lab-07":  ("#FACC15", "250,204,21"),    # yellow
    "lab-08":  ("#A3E635", "163,230,53"),    # lime
    "lab-09a": ("#FB7185", "251,113,133"),   # rose
    "lab-09b": ("#E879F9", "232,121,249"),   # fuchsia
    "lab-09c": ("#F472B6", "244,114,182"),   # pink
    "lab-10":  ("#F87171", "248,113,113"),   # red
    "lab-11":  ("#4ADE80", "74,222,128"),    # green
}

# ── Lab data ───────────────────────────────────────────────────────────────────
# Each step: (title, type, description_html, [commands])
# type: "portal" | "cli" | "ps"

LABS = [
    {
        "id": "01", "slug": "lab-01",
        "title": "Manage Azure AD Identities",
        "subtitle": "Create and manage users, groups, and bulk operations in Microsoft Entra ID",
        "duration": "30 min", "difficulty": "Beginner", "diff_color": "blue",
        "module": "Module 1 — Manage Identities and Governance",
        "objectives": [
            "Create and configure Microsoft Entra ID user accounts",
            "Create security and Microsoft 365 groups",
            "Perform bulk user operations via CSV upload",
            "Manage group membership and review audit logs",
        ],
        "prereqs": [
            "Azure subscription with <strong>Global Administrator</strong> or <strong>User Administrator</strong> role",
            "Browser access to <a href='https://portal.azure.com' class='text-indigo-600 hover:underline' target='_blank'>portal.azure.com</a>",
        ],
        "steps": [
            ("Navigate to Microsoft Entra ID", "portal",
             "From the Azure Portal home, search for <strong>Microsoft Entra ID</strong> in the top search bar and select it.",
             []),
            ("Create a user account", "portal",
             "Select <strong>Users → New user → Create new user</strong>. Set the UPN to <code>az104-user1</code>, display name to <em>AZ104 User1</em>, and assign a temporary password.",
             []),
            ("Create a second user", "portal",
             "Return to <strong>Users → New user → Create new user</strong>. Set UPN to <code>az104-user2</code>, display name to <em>AZ104 User2</em>, assign a temporary password, and check <em>Must change password at next sign-in</em>. Click <strong>Create</strong>.",
             []),
            ("Create a security group", "portal",
             "Go to <strong>Groups → New group</strong>. Set type to <em>Security</em>, name to <em>AZ104-Lab-Group</em>, membership type to <em>Assigned</em>. Add both users as members, then click <strong>Create</strong>.",
             []),
            ("Bulk invite guest users", "portal",
             "Under <strong>Users → Bulk operations → Bulk invite</strong>, download the CSV template. Add two guest email addresses, upload the file, and click <strong>Submit</strong>. Monitor the bulk operation results.",
             []),
            ("Review audit logs", "portal",
             "Navigate to <strong>Microsoft Entra ID → Monitoring → Audit logs</strong>. Filter by <em>Category: UserManagement</em> to see all creation events from this lab.",
             []),
        ],
        "validation": [
            "Both users appear in <strong>Entra ID → Users</strong> with correct UPNs.",
            "<em>AZ104-Lab-Group</em> lists two assigned members.",
            "Bulk invite operation shows <em>Success</em> in the Bulk operation results panel.",
            "Audit log shows <em>Add user</em> and <em>Add group</em> entries.",
        ],
        "cleanup": [
            "# Delete lab users",
            'DOMAIN=$(az account show --query tenantDefaultDomain -o tsv)',
            'az ad user delete --id "az104-user1@${DOMAIN}"',
            'az ad user delete --id "az104-user2@${DOMAIN}"',
            "# Delete the group (portal: Groups → AZ104-Lab-Group → Delete)",
        ],
        "d_nodes": [
            {"id":"tenant","label":"Entra ID","sub":"Tenant","x":195,"y":15,"w":130,"h":50,"type":"identity"},
            {"id":"u1","label":"User 1","sub":"Member","x":55,"y":115,"w":110,"h":44,"type":"identity"},
            {"id":"u2","label":"User 2","sub":"Member","x":200,"y":115,"w":110,"h":44,"type":"identity"},
            {"id":"guest","label":"Guest User","sub":"B2B Invite","x":345,"y":115,"w":120,"h":44,"type":"identity"},
            {"id":"sg","label":"Security Group","sub":"Assigned","x":75,"y":220,"w":130,"h":44,"type":"identity"},
            {"id":"dg","label":"Dynamic Group","sub":"Query-based","x":295,"y":220,"w":140,"h":44,"type":"identity"},
        ],
        "d_edges": [
            {"from":"tenant","to":"u1"},{"from":"tenant","to":"u2"},{"from":"tenant","to":"guest"},
            {"from":"u1","to":"sg"},{"from":"u2","to":"sg"},{"from":"tenant","to":"dg","dashed":True},
        ],
        "d_groups": [
            {"label":"Users","x":35,"y":95,"w":460,"h":80,"type":"identity"},
            {"label":"Groups","x":55,"y":200,"w":400,"h":75,"type":"identity"},
        ],
    },
    {
        "id": "02a", "slug": "lab-02a",
        "title": "Subscriptions &amp; RBAC",
        "subtitle": "Manage Azure subscriptions and implement role-based access control",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 2 — Manage Identities and Governance",
        "objectives": [
            "Understand management group and subscription hierarchy",
            "Create a custom RBAC role with scoped permissions",
            "Assign built-in RBAC roles at subscription and resource group scope",
            "Audit role assignments with the Activity Log",
        ],
        "prereqs": [
            "Azure subscription with <strong>Owner</strong> role",
            "At least one resource group (create one named <em>az104-rg1</em> if needed)",
        ],
        "steps": [
            ("Review the Management Group hierarchy", "portal",
             "Search for <strong>Management groups</strong> in the portal. Expand the root to see subscriptions beneath it. Note the tenant root group ID.",
             []),
            ("Inspect your subscription", "portal",
             "Search for <strong>Subscriptions</strong> in the portal and open your subscription. Review the Overview blade — note the Subscription ID, Display Name, and Status shown in the essentials panel.",
             []),
            ("Assign a built-in role at resource group scope", "portal",
             "Open <strong>az104-rg1 → Access control (IAM) → + Add → Add role assignment</strong>. Search for <em>Reader</em>, click <strong>Next</strong>. Under Members click <strong>+ Select members</strong>, search for <em>AZ104 User1</em> and select them. Click <strong>Review + assign</strong>.",
             []),
            ("Create a custom RBAC role", "portal",
             "In your subscription, go to <strong>Access control (IAM) → Roles → + Create</strong>. Choose <em>Start from scratch</em>. Name it <em>VM Operator</em>. Under <strong>Permissions → + Add permissions</strong>, search for and add <code>Microsoft.Compute/virtualMachines/read</code> and <code>Microsoft.Compute/virtualMachines/restart/action</code>. Set assignable scope to your subscription. Click <strong>Review + create → Create</strong>.",
             []),
            ("Review role assignments", "portal",
             "Go to <strong>Subscriptions → [your sub] → Access control (IAM) → Role assignments</strong>. Confirm the Reader assignment appears for AZ104 User1.",
             []),
            ("Audit with Activity Log", "portal",
             "Under the subscription, open <strong>Activity log</strong>. Filter by <em>Operation: Create role assignment</em> to see the assignment history.",
             []),
        ],
        "validation": [
            "Reader role assignment appears on <em>az104-rg1</em> IAM blade.",
            '<em>VM Operator</em> custom role listed under <strong>Roles</strong> in IAM → Roles.',
            "Activity log shows role assignment create event.",
        ],
        "cleanup": [
            "# Remove the role assignment",
            'az role assignment delete --assignee "${USER_ID}" --role "Reader" \\',
            '  --resource-group az104-rg1',
            "# Remove custom role",
            'az role definition delete --name "VM Operator"',
        ],
        "d_nodes": [
            {"id":"mg","label":"Management Group","sub":"Root Tenant","x":175,"y":15,"w":170,"h":50,"type":"govern"},
            {"id":"sub","label":"Subscription","sub":"Pay-As-You-Go","x":190,"y":115,"w":140,"h":44,"type":"govern"},
            {"id":"rg","label":"Resource Group","sub":"az104-rg1","x":60,"y":215,"w":140,"h":44,"type":"govern"},
            {"id":"rbac","label":"Role Assignment","sub":"IAM","x":310,"y":115,"w":130,"h":44,"type":"identity"},
            {"id":"owner","label":"Owner","x":235,"y":215,"w":90,"h":36,"type":"identity"},
            {"id":"reader","label":"Reader","x":340,"y":215,"w":90,"h":36,"type":"identity"},
            {"id":"custom","label":"VM Operator","sub":"Custom","x":440,"y":215,"w":75,"h":36,"type":"identity"},
        ],
        "d_edges": [
            {"from":"mg","to":"sub"},{"from":"sub","to":"rg"},{"from":"sub","to":"rbac"},
            {"from":"rbac","to":"owner"},{"from":"rbac","to":"reader"},{"from":"rbac","to":"custom"},
        ],
        "d_groups": [],
    },
    {
        "id": "02b", "slug": "lab-02b",
        "title": "Governance via Azure Policy",
        "subtitle": "Create and assign policies, manage compliance, and configure resource locks",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 2 — Manage Identities and Governance",
        "objectives": [
            "Create and assign a built-in Azure Policy definition",
            "Create a policy initiative (set) from multiple definitions",
            "Evaluate compliance state and trigger an on-demand scan",
            "Apply resource locks to prevent accidental deletion",
        ],
        "prereqs": [
            "Azure subscription with <strong>Owner</strong> or <strong>Policy Contributor</strong> role",
            "Resource group <em>az104-rg1</em> in East US",
        ],
        "steps": [
            ("Explore built-in policy definitions", "portal",
             "Search for <strong>Policy</strong> in the portal. Go to <strong>Definitions</strong> and filter by category <em>Compute</em>. Review <em>Allowed virtual machine size SKUs</em>.",
             []),
            ("Assign the allowed SKUs policy", "portal",
             "In <strong>Policy → Assignments → + Assign policy</strong>, click the scope selector and choose <em>az104-rg1</em>. Search for <em>Allowed virtual machine size SKUs</em> and select it. Click <strong>Next → Parameters</strong>. Enter <code>Standard_B1s</code>, <code>Standard_B2s</code>, <code>Standard_B4ms</code> as allowed SKUs. Click <strong>Review + create → Create</strong>.",
             []),
            ("Create a policy initiative", "portal",
             "In <strong>Policy → Definitions → + Initiative definition</strong>, create an initiative named <em>AZ104-Governance</em> and add the <em>Allowed locations</em> and <em>Require a tag on resources</em> definitions.",
             []),
            ("Trigger a compliance scan", "portal",
             "In <strong>Policy → Compliance</strong>, click the <strong>Re-evaluate Compliance</strong> button in the toolbar. Wait 2–3 minutes and refresh. The dashboard updates to show the current compliance state of <em>az104-rg1</em>.",
             []),
            ("Apply a resource lock", "portal",
             "Open <strong>az104-rg1 → Settings → Locks → + Add</strong>. Set Name to <em>DoNotDelete</em>, Lock type to <em>Delete</em>. Click <strong>OK</strong>. The lock now prevents deletion until it is removed.",
             []),
            ("Verify policy enforcement", "portal",
             "Try to create a VM with size <em>Standard_D4s_v3</em> in <em>az104-rg1</em>. The deployment should fail with a policy violation error.",
             []),
        ],
        "validation": [
            "<em>AllowedVMSKUs</em> assignment appears on the resource group IAM/Policy blade.",
            "Compliance scan shows the policy assignment in <em>Compliant</em> or <em>Non-compliant</em> state.",
            "Resource lock <em>DoNotDelete</em> appears under <strong>Settings → Locks</strong> on the resource group.",
            "Deploying a disallowed VM SKU returns <em>RequestDisallowedByPolicy</em> error.",
        ],
        "cleanup": [
            "# Remove the lock first (required before deleting resources)",
            'az lock delete --name "DoNotDelete" --resource-group az104-rg1',
            "# Remove the policy assignment",
            'az policy assignment delete --name "AllowedVMSKUs" --resource-group az104-rg1',
        ],
        "d_nodes": [
            {"id":"pd","label":"Policy Definition","sub":"Built-in","x":50,"y":40,"w":135,"h":44,"type":"govern"},
            {"id":"init","label":"Policy Initiative","sub":"Custom Set","x":330,"y":40,"w":135,"h":44,"type":"govern"},
            {"id":"assign","label":"Assignment","sub":"RG Scope","x":190,"y":140,"w":140,"h":44,"type":"govern"},
            {"id":"sub","label":"Subscription","sub":"Scope","x":50,"y":220,"w":130,"h":44,"type":"govern"},
            {"id":"comp","label":"Compliance","sub":"Dashboard","x":330,"y":220,"w":130,"h":44,"type":"govern"},
            {"id":"lock","label":"Resource Lock","sub":"CanNotDelete","x":190,"y":220,"w":140,"h":44,"type":"backup"},
        ],
        "d_edges": [
            {"from":"pd","to":"assign"},{"from":"init","to":"assign"},
            {"from":"assign","to":"sub"},{"from":"assign","to":"comp"},{"from":"assign","to":"lock"},
        ],
        "d_groups": [],
    },
    {
        "id": "03a", "slug": "lab-03a",
        "title": "Resources via Azure Portal",
        "subtitle": "Create resource groups and manage resources using the Azure Portal",
        "duration": "20 min", "difficulty": "Beginner", "diff_color": "blue",
        "module": "Module 3 — Manage Azure Resources",
        "objectives": [
            "Create and configure Azure resource groups",
            "Deploy a storage account using the portal",
            "Move resources between resource groups",
            "Apply and manage resource tags",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role or higher",
            "Browser access to <a href='https://portal.azure.com' class='text-indigo-600 hover:underline' target='_blank'>portal.azure.com</a>",
        ],
        "steps": [
            ("Create a resource group", "portal",
             "Click <strong>+ Create a resource</strong>, search for <em>Resource group</em>, and create <em>az104-rg1</em> in <em>East US</em>.",
             []),
            ("Deploy a storage account", "portal",
             "Search for <strong>Storage accounts</strong>, click <strong>+ Create</strong>. Select <em>az104-rg1</em>, name the account (e.g. <em>az104store[unique]</em>), region <em>East US</em>, redundancy <em>LRS</em>. Click <strong>Review + Create → Create</strong>.",
             []),
            ("Tag the resource group", "portal",
             "Open <em>az104-rg1</em>, click <strong>Tags</strong> in the sidebar. Add tags: <code>Environment: Lab</code> and <code>Project: AZ104</code>. Save.",
             []),
            ("Move the storage account to a new RG", "portal",
             "Open the storage account, click <strong>Overview → Move → Move to another resource group</strong>. Create a new group <em>az104-rg2</em> during the move wizard.",
             []),
            ("Verify the move", "portal",
             "Navigate to <em>az104-rg2</em> and confirm the storage account is listed. Check that tags were preserved.",
             []),
        ],
        "validation": [
            "Both <em>az104-rg1</em> and <em>az104-rg2</em> exist in East US.",
            "Storage account appears in <em>az104-rg2</em> after the move.",
            "Resource group <em>az104-rg1</em> shows <em>Environment: Lab</em> tag.",
        ],
        "cleanup": [
            "# Delete both resource groups (this deletes all resources inside)",
            "az group delete --name az104-rg1 --yes --no-wait",
            "az group delete --name az104-rg2 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"portal","label":"Azure Portal","sub":"Browser","x":190,"y":20,"w":140,"h":50,"type":"default"},
            {"id":"rg1","label":"Resource Group","sub":"az104-rg1","x":70,"y":130,"w":140,"h":44,"type":"govern"},
            {"id":"rg2","label":"Resource Group","sub":"az104-rg2","x":310,"y":130,"w":140,"h":44,"type":"govern"},
            {"id":"sa","label":"Storage Account","sub":"LRS","x":190,"y":230,"w":140,"h":44,"type":"storage"},
        ],
        "d_edges": [
            {"from":"portal","to":"rg1"},{"from":"portal","to":"rg2"},
            {"from":"rg1","to":"sa"},{"from":"sa","to":"rg2","label":"Move"},
        ],
        "d_groups": [],
    },
    {
        "id": "03b", "slug": "lab-03b",
        "title": "Resources via ARM Templates",
        "subtitle": "Deploy and manage Azure resources using ARM JSON templates",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 3 — Manage Azure Resources",
        "objectives": [
            "Export an ARM template from an existing resource",
            "Modify template parameters for a new deployment",
            "Deploy resources from an ARM template via portal and CLI",
            "Understand template schema structure and linked templates",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg1</em> (or create it during the lab)",
        ],
        "steps": [
            ("Create a resource to export", "portal",
             "Create a simple storage account named <em>az104armtest[unique]</em> in <em>az104-rg1</em> via the portal.",
             []),
            ("Export the ARM template", "portal",
             "Open the storage account, click <strong>Export template</strong> in the sidebar. Review the JSON structure — note <code>parameters</code>, <code>variables</code>, and <code>resources</code> sections. Click <strong>Download</strong>.",
             []),
            ("Modify the template", "portal",
             "Open the downloaded <code>template.json</code> in a text editor. In the <code>parameters</code> section, update the <code>storageAccountName</code> default value to a unique name such as <em>az104arm2[5-digit-suffix]</em>. Save the file.",
             []),
            ("Deploy via Custom Template", "portal",
             "In the portal, search for <strong>Deploy a custom template</strong>. Click <strong>Build your own template in the editor</strong>, then <strong>Load file</strong> and select your modified <code>template.json</code>. Click <strong>Save</strong>, fill in <em>az104-rg1</em> as the resource group and review parameters. Click <strong>Review + create → Create</strong>.",
             []),
            ("Monitor the deployment", "portal",
             "In <em>az104-rg1</em>, click <strong>Deployments</strong>. Select <em>arm-lab-deployment</em> to see the deployment timeline, operations, and outputs.",
             []),
            ("Use a Quickstart template", "portal",
             "Navigate to <strong>Deploy a custom template</strong> in the portal. Click <em>Load a GitHub quickstart template</em>, search for <em>101-storage-account-create</em>, and deploy it to <em>az104-rg1</em>.",
             []),
        ],
        "validation": [
            "Two storage accounts exist in <em>az104-rg1</em>.",
            "Deployment <em>arm-lab-deployment</em> shows <em>Succeeded</em> in the Deployments blade.",
        ],
        "cleanup": [
            "az group delete --name az104-rg1 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"tmpl","label":"ARM Template","sub":"JSON","x":50,"y":30,"w":130,"h":50,"type":"default"},
            {"id":"param","label":"Parameters","sub":".json file","x":220,"y":30,"w":120,"h":50,"type":"default"},
            {"id":"arm","label":"ARM Engine","sub":"Azure Resource Mgr","x":165,"y":140,"w":170,"h":50,"type":"govern"},
            {"id":"rg","label":"Resource Group","sub":"az104-rg1","x":80,"y":240,"w":140,"h":44,"type":"govern"},
            {"id":"sa","label":"Storage Account","sub":"Deployed","x":300,"y":240,"w":140,"h":44,"type":"storage"},
        ],
        "d_edges": [
            {"from":"tmpl","to":"arm"},{"from":"param","to":"arm"},
            {"from":"arm","to":"rg"},{"from":"arm","to":"sa"},
        ],
        "d_groups": [],
    },
    {
        "id": "03c", "slug": "lab-03c",
        "title": "Resources via PowerShell",
        "subtitle": "Manage Azure resources using Azure PowerShell and Cloud Shell",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 3 — Manage Azure Resources",
        "objectives": [
            "Open and configure Azure Cloud Shell with PowerShell",
            "Create and manage resource groups with Az PowerShell module",
            "Deploy a managed disk using PowerShell",
            "Create a simple ARM deployment from a PowerShell template",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Storage account for Cloud Shell (created automatically on first use)",
        ],
        "steps": [
            ("Open Cloud Shell (PowerShell)", "portal",
             "Click the <strong>Cloud Shell</strong> icon (>_) in the portal toolbar. If prompted, select <strong>PowerShell</strong> and complete the storage setup wizard. The shell opens in an integrated terminal at the bottom of the portal.",
             []),
            ("Create a resource group", "portal",
             "Search for <strong>Resource groups → + Create</strong>. Set Subscription to your subscription, Resource group name to <em>az104-rg1</em>, Region to <em>East US</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Deploy a managed disk", "portal",
             "Search for <strong>Disks → + Create</strong>. Set Resource group to <em>az104-rg1</em>, Disk name to <em>az104-disk1</em>, Region to <em>East US</em>. Under Disk SKU choose <em>Standard SSD (locally-redundant)</em>, Size <em>32 GiB</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Resize the disk", "portal",
             "Open <em>az104-disk1</em> in the portal. Click <strong>Size + performance</strong> in the sidebar. Change the disk size to <em>64 GiB</em> (disk must be unattached). Click <strong>Save</strong> and confirm the updated size in Overview.",
             []),
            ("List resources in the resource group", "portal",
             "Open <em>az104-rg1 → Overview</em>. All resources are listed with their Name, Type, and Location. Use the <strong>Filter by name</strong> box to search within the group.",
             []),
            ("Clean up resources", "portal",
             "Open <em>az104-rg1 → Overview → Delete resource group</em>. Type the resource group name to confirm deletion. Click <strong>Delete</strong> — all resources inside are removed.",
             []),
        ],
        "validation": [
            "Cloud Shell opens in PowerShell mode and <code>Get-AzContext</code> returns your subscription.",
            "Managed disk <em>az104-disk1</em> is visible in <em>az104-rg1</em> via the portal.",
            "After resize, disk shows 64 GiB in the portal.",
        ],
        "cleanup": [
            'Remove-AzResourceGroup -Name "az104-rg1" -Force',
        ],
        "d_nodes": [
            {"id":"shell","label":"Cloud Shell","sub":"PowerShell","x":50,"y":30,"w":130,"h":50,"type":"default"},
            {"id":"az","label":"Az Module","sub":"PowerShell","x":260,"y":30,"w":130,"h":50,"type":"default"},
            {"id":"arm","label":"Azure Resource Mgr","sub":"ARM","x":165,"y":140,"w":170,"h":50,"type":"govern"},
            {"id":"rg","label":"Resource Group","sub":"az104-rg1","x":80,"y":240,"w":140,"h":44,"type":"govern"},
            {"id":"disk","label":"Managed Disk","sub":"StandardSSD_LRS","x":295,"y":240,"w":145,"h":44,"type":"compute"},
        ],
        "d_edges": [
            {"from":"shell","to":"az"},{"from":"az","to":"arm"},
            {"from":"arm","to":"rg"},{"from":"arm","to":"disk"},
        ],
        "d_groups": [],
    },
    {
        "id": "03d", "slug": "lab-03d",
        "title": "Resources via Azure CLI",
        "subtitle": "Use the Azure CLI in Cloud Shell to deploy and manage resources",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 3 — Manage Azure Resources",
        "objectives": [
            "Open Azure Cloud Shell in Bash mode",
            "Create and configure a resource group with Azure CLI",
            "Deploy a managed disk using az disk commands",
            "Query resource properties with JMESPath expressions",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Cloud Shell initialized (creates a small storage account automatically)",
        ],
        "steps": [
            ("Open Cloud Shell (Bash)", "portal",
             "Click the <strong>Cloud Shell</strong> icon (>_) in the portal toolbar. Select <strong>Bash</strong> when prompted. If first time, create a storage account for Cloud Shell persistence.",
             []),
            ("Create a resource group", "portal",
             "Search for <strong>Resource groups → + Create</strong>. Enter name <em>az104-rg1</em>, region <em>East US</em>. Click <strong>Tags</strong> and add <code>Environment: Lab</code> and <code>Project: AZ104</code>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Create a managed disk", "portal",
             "Search for <strong>Disks → + Create</strong>. Set Resource group to <em>az104-rg1</em>, name to <em>az104-disk1</em>, region to <em>East US</em>, SKU to <em>Standard SSD (locally-redundant)</em>, size <em>32 GiB</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("View disk properties", "portal",
             "Open <em>az104-disk1 → Overview</em>. Note the Disk state, Disk size, and SKU in the essentials panel. Click <strong>Properties</strong> in the sidebar for additional metadata including Disk ID and creation time.",
             []),
            ("Update the disk size", "portal",
             "In <em>az104-disk1</em>, click <strong>Size + performance</strong>. Change size to <em>64 GiB</em> (disk must be unattached). Click <strong>Save</strong> and confirm the new size in Overview.",
             []),
            ("List all resources in the RG", "portal",
             "Navigate to <em>az104-rg1 → Overview</em>. The resource list shows all resources with their Name, Type, and Location. Use the <strong>Filter by name</strong> box to search within the group.",
             []),
        ],
        "validation": [
            "<code>az group show --name az104-rg1</code> returns <em>Succeeded</em> provisioning state.",
            "Disk <em>az104-disk1</em> shows <em>Unattached</em> state and 64 GiB after resize.",
            "Resource list shows at least one disk in <em>az104-rg1</em>.",
        ],
        "cleanup": [
            "az group delete --name az104-rg1 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"shell","label":"Cloud Shell","sub":"Bash","x":50,"y":30,"w":130,"h":50,"type":"default"},
            {"id":"cli","label":"Azure CLI","sub":"az commands","x":265,"y":30,"w":130,"h":50,"type":"default"},
            {"id":"arm","label":"Azure Resource Mgr","sub":"REST API","x":165,"y":135,"w":170,"h":50,"type":"govern"},
            {"id":"rg","label":"Resource Group","sub":"az104-rg1  East US","x":60,"y":235,"w":155,"h":44,"type":"govern"},
            {"id":"disk","label":"Managed Disk","sub":"StandardSSD 64GiB","x":295,"y":235,"w":155,"h":44,"type":"compute"},
        ],
        "d_edges": [
            {"from":"shell","to":"cli"},{"from":"cli","to":"arm"},
            {"from":"arm","to":"rg"},{"from":"arm","to":"disk"},
        ],
        "d_groups": [],
    },
    {
        "id": "04", "slug": "lab-04",
        "title": "Implement Virtual Networking",
        "subtitle": "Create VNets, subnets, NSGs, and configure Azure DNS settings",
        "duration": "40 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 4 — Configure and Manage Virtual Networks",
        "objectives": [
            "Create a virtual network with multiple subnets",
            "Create and associate a Network Security Group",
            "Configure NSG inbound and outbound security rules",
            "Configure Azure private DNS and link it to a VNet",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg4</em> in East US",
        ],
        "steps": [
            ("Create a virtual network", "portal",
             "Search for <strong>Virtual networks → + Create</strong>. Set Resource group <em>az104-rg4</em>, Name <em>az104-vnet1</em>, Region <em>East US</em>. Under <strong>IP Addresses</strong>, set address space to <code>10.40.0.0/16</code>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Add subnets", "portal",
             "Open <em>az104-vnet1 → Subnets → + Subnet</em>. Add <em>subnet0</em> with address range <code>10.40.0.0/24</code>. Click <strong>Save</strong>. Add another subnet <em>subnet1</em> with <code>10.40.1.0/24</code>. Click <strong>Save</strong>.",
             []),
            ("Create an NSG and rules", "portal",
             "Search for <strong>Network security groups → + Create</strong>. Set Resource group <em>az104-rg4</em>, Name <em>az104-nsg1</em>, Region <em>East US</em>. After creation, open <strong>az104-nsg1 → Inbound security rules → + Add</strong>. Set Destination port <code>3389</code>, Protocol <em>TCP</em>, Action <em>Allow</em>, Priority <code>100</code>, Name <em>AllowRDP</em>. Click <strong>Add</strong>.",
             []),
            ("Associate the NSG to subnet0", "portal",
             "Open <em>az104-nsg1 → Subnets → + Associate</em>. Select Virtual network <em>az104-vnet1</em> and Subnet <em>subnet0</em>. Click <strong>OK</strong>.",
             []),
            ("Create an Azure DNS private zone", "portal",
             "Search for <strong>Private DNS zones → + Create</strong>. Set Resource group <em>az104-rg4</em>, Name <code>private.contoso.com</code>. After creation, click <strong>+ Virtual network link → + Add</strong>. Enter link name <em>az104-vnet1-link</em>, select VNet <em>az104-vnet1</em>, enable <strong>Auto registration</strong>. Click <strong>OK</strong>.",
             []),
            ("Verify the configuration", "portal",
             "Open <em>az104-vnet1</em> in the portal. Confirm subnets, check <strong>Connected devices</strong>, and open <strong>DNS servers</strong> to see the private zone link.",
             []),
        ],
        "validation": [
            "VNet <em>az104-vnet1</em> has two subnets (10.40.0.0/24 and 10.40.1.0/24).",
            "NSG <em>az104-nsg1</em> is associated with <em>subnet0</em>.",
            "Private DNS zone <em>private.contoso.com</em> is linked to <em>az104-vnet1</em> with auto-registration.",
        ],
        "cleanup": [
            "az group delete --name az104-rg4 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"vnet","label":"VNet","sub":"10.40.0.0/16","x":175,"y":20,"w":170,"h":50,"type":"network"},
            {"id":"sub0","label":"subnet0","sub":"10.40.0.0/24  Public","x":60,"y":130,"w":155,"h":44,"type":"network"},
            {"id":"sub1","label":"subnet1","sub":"10.40.1.0/24  Private","x":305,"y":130,"w":155,"h":44,"type":"network"},
            {"id":"nsg","label":"NSG","sub":"AllowRDP / DenyAll","x":60,"y":230,"w":155,"h":44,"type":"network"},
            {"id":"dns","label":"Private DNS","sub":"private.contoso.com","x":305,"y":230,"w":155,"h":44,"type":"network"},
        ],
        "d_edges": [
            {"from":"vnet","to":"sub0"},{"from":"vnet","to":"sub1"},
            {"from":"nsg","to":"sub0","label":"Associated"},{"from":"vnet","to":"dns"},
        ],
        "d_groups": [],
    },
    {
        "id": "05", "slug": "lab-05",
        "title": "Intersite Connectivity",
        "subtitle": "Configure VNet peering and test connectivity between virtual networks",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 5 — Intersite Connectivity",
        "objectives": [
            "Create two virtual networks with non-overlapping address spaces",
            "Configure bidirectional VNet peering",
            "Deploy test VMs in each VNet",
            "Validate cross-VNet connectivity with ping and traceroute",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg5</em> in East US",
        ],
        "steps": [
            ("Create two virtual networks", "portal",
             "Create two VNets (repeat for each). First: Name <em>az104-vnet1</em>, address space <code>10.51.0.0/22</code>, add subnet <em>subnet0</em> <code>10.51.0.0/24</code>. Second: Name <em>az104-vnet2</em>, address space <code>10.52.0.0/22</code>, add subnet <em>subnet0</em> <code>10.52.0.0/24</code>. Both in Resource group <em>az104-rg5</em>, Region <em>East US</em>.",
             []),
            ("Create VNet peering (both directions)", "portal",
             "Open <em>az104-vnet1 → Peerings → + Add</em>. Set peering link name (this VNet) <em>vnet1-to-vnet2</em>, Remote VNet <em>az104-vnet2</em>, peering link name (remote) <em>vnet2-to-vnet1</em>. Enable <strong>Allow virtual network access</strong> on both sides. Click <strong>Add</strong> — Azure creates both directions simultaneously.",
             []),
            ("Deploy test VMs", "portal",
             "Deploy a small VM (<em>Standard_B1s</em>) in each VNet subnet. Use Linux (Ubuntu 22.04) with SSH public key auth. Note both private IP addresses.",
             []),
            ("Test connectivity via serial console", "portal",
             "Open the VM in VNet1 via <strong>Serial console</strong> (or SSH). Ping the private IP of the VM in VNet2.",
             [
                 "# On VM1 (10.51.0.x):",
                 "ping 10.52.0.4 -c 4",
                 "traceroute 10.52.0.4",
             ]),
            ("Verify peering state", "portal",
             "Open <em>az104-vnet1 → Peerings</em>. The peering <em>vnet1-to-vnet2</em> should show <strong>Connected</strong>. Open <em>az104-vnet2 → Peerings</em> to confirm the reverse link <em>vnet2-to-vnet1</em> is also <strong>Connected</strong>.",
             []),
        ],
        "validation": [
            "Both peerings show <em>Connected</em> state.",
            "Ping from VM1 to VM2's private IP succeeds with &lt;1ms latency.",
            "Traceroute shows direct path (1 hop) between peered VNets.",
        ],
        "cleanup": [
            "az group delete --name az104-rg5 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"vnet1","label":"VNet 1","sub":"10.51.0.0/22","x":50,"y":30,"w":150,"h":50,"type":"network"},
            {"id":"vnet2","label":"VNet 2","sub":"10.52.0.0/22","x":320,"y":30,"w":150,"h":50,"type":"network"},
            {"id":"peer","label":"VNet Peering","sub":"Bidirectional","x":180,"y":30,"w":160,"h":50,"type":"network"},
            {"id":"vm1","label":"VM1","sub":"10.51.0.4","x":60,"y":180,"w":130,"h":44,"type":"compute"},
            {"id":"sub1","label":"subnet0","sub":"10.51.0.0/24","x":60,"y":115,"w":130,"h":44,"type":"network"},
            {"id":"vm2","label":"VM2","sub":"10.52.0.4","x":330,"y":180,"w":130,"h":44,"type":"compute"},
            {"id":"sub2","label":"subnet0","sub":"10.52.0.0/24","x":330,"y":115,"w":130,"h":44,"type":"network"},
        ],
        "d_edges": [
            {"from":"vnet1","to":"peer"},{"from":"peer","to":"vnet2"},
            {"from":"vnet1","to":"sub1"},{"from":"sub1","to":"vm1"},
            {"from":"vnet2","to":"sub2"},{"from":"sub2","to":"vm2"},
            {"from":"vm1","to":"vm2","label":"ping / traceroute"},
        ],
        "d_groups": [],
    },
    {
        "id": "06", "slug": "lab-06",
        "title": "Traffic Management",
        "subtitle": "Deploy and configure Azure Load Balancer and Application Gateway",
        "duration": "45 min", "difficulty": "Advanced", "diff_color": "red",
        "module": "Module 6 — Network Traffic Management",
        "objectives": [
            "Deploy an internal and public Azure Load Balancer (Layer 4)",
            "Configure a backend pool, health probe, and load-balancing rule",
            "Deploy an Application Gateway (Layer 7) with path-based routing",
            "Test failover by stopping a backend VM",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg6</em> with a VNet (10.60.0.0/16) and at least two backend VMs",
        ],
        "steps": [
            ("Create a public Load Balancer", "portal",
             "Search for <strong>Load balancers → + Create</strong>. Set SKU <em>Standard</em>, Type <em>Public</em>, Resource group <em>az104-rg6</em>, Name <em>az104-lb1</em>, Region <em>East US</em>. Under <strong>Frontend IP</strong>, add <em>FrontendIP</em> with a new public IP <em>az104-lb1-pip</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Add a health probe", "portal",
             "Open <em>az104-lb1 → Health probes → + Add</em>. Set Name <em>HTTPProbe</em>, Protocol <em>HTTP</em>, Port <code>80</code>, Path <code>/</code>, Interval <em>5 s</em>. Click <strong>Add</strong>.",
             []),
            ("Add a load-balancing rule", "portal",
             "Open <em>az104-lb1 → Load balancing rules → + Add</em>. Set Name <em>HTTPRule</em>, Frontend IP <em>FrontendIP</em>, Protocol <em>TCP</em>, Port <code>80</code>, Backend port <code>80</code>, Backend pool <em>BackendPool</em>, Health probe <em>HTTPProbe</em>. Click <strong>Add</strong>.",
             []),
            ("Add backend VMs to the pool", "portal",
             "Open the load balancer in the portal. Go to <strong>Backend pools → BackendPool → + Add</strong>. Select both VM NICs in <em>az104-rg6</em>.",
             []),
            ("Deploy an Application Gateway", "portal",
             "Search for <strong>Application Gateway</strong> and create one with: Tier <em>Standard V2</em>, VNet <em>az104-vnet</em>, Frontend IP public, Backend pools for <em>/api/*</em> and <em>/web/*</em> path-based routing.",
             []),
            ("Test failover", "portal",
             "Stop one backend VM. Refresh the load balancer public IP in a browser — traffic should continue serving from the remaining healthy backend. Check the probe status in the LB monitoring blade.",
             []),
        ],
        "validation": [
            "Load balancer frontend IP is reachable on port 80 and distributes traffic.",
            "After stopping one VM, the health probe shows it as <em>Unhealthy</em> and the LB routes traffic to the remaining VM.",
            "Application Gateway path-based routing sends <em>/api/*</em> to the correct backend pool.",
        ],
        "cleanup": [
            "az group delete --name az104-rg6 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"inet","label":"Internet","sub":"Public Traffic","x":185,"y":15,"w":150,"h":44,"type":"default"},
            {"id":"agw","label":"App Gateway","sub":"Layer 7  WAF","x":60,"y":115,"w":150,"h":50,"type":"network"},
            {"id":"lb","label":"Load Balancer","sub":"Layer 4  Standard","x":310,"y":115,"w":150,"h":50,"type":"network"},
            {"id":"vm1","label":"VM Backend 1","sub":"10.60.1.4","x":60,"y":225,"w":135,"h":44,"type":"compute"},
            {"id":"vm2","label":"VM Backend 2","sub":"10.60.1.5","x":325,"y":225,"w":135,"h":44,"type":"compute"},
        ],
        "d_edges": [
            {"from":"inet","to":"agw","label":"HTTP/S"},
            {"from":"inet","to":"lb","label":"TCP"},
            {"from":"agw","to":"vm1"},{"from":"agw","to":"vm2"},
            {"from":"lb","to":"vm1"},{"from":"lb","to":"vm2"},
        ],
        "d_groups": [],
    },
    {
        "id": "07", "slug": "lab-07",
        "title": "Manage Azure Storage",
        "subtitle": "Create storage accounts, configure access and replication, and use AzCopy",
        "duration": "40 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 7 — Manage Azure Storage",
        "objectives": [
            "Create a storage account with specific redundancy settings",
            "Configure blob containers and set access tiers",
            "Generate a Shared Access Signature (SAS) token",
            "Transfer data using AzCopy and manage lifecycle policies",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> + <strong>Storage Blob Data Owner</strong> role",
            "Resource group <em>az104-rg7</em> in East US",
            "AzCopy CLI (available in Cloud Shell)",
        ],
        "steps": [
            ("Create a storage account", "portal",
             "Search for <strong>Storage accounts → + Create</strong>. Set Resource group <em>az104-rg7</em>, name (unique, e.g. <em>az104storage[random]</em>), Region <em>East US</em>, Performance <em>Standard</em>, Redundancy <em>Geo-redundant storage (GRS)</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Create a blob container and upload a file", "portal",
             "Open your storage account → <strong>Containers → + Container</strong>. Name it <em>az104-container</em>, Access level <em>Private</em>. Click <strong>Create</strong>. Open the container, click <strong>Upload</strong>, select a local file (e.g. a test .txt file). Click <strong>Upload</strong>.",
             []),
            ("Generate a SAS token", "portal",
             "Open <em>az104-container</em>, click your uploaded blob. Click <strong>Generate SAS</strong> in the blade. Set Permissions to <em>Read</em>, set expiry 1 hour from now. Click <strong>Generate SAS token and URL</strong>. Copy the Blob SAS URL and open it in a browser.",
             []),
            ("Upload additional files with Storage Explorer", "portal",
             "In the storage account, click <strong>Storage browser (preview)</strong> in the sidebar. Navigate to <em>Blob containers → az104-container</em>. Click <strong>Upload</strong> to drag-and-drop additional files directly into the container.",
             []),
            ("Configure a lifecycle policy", "portal",
             "In the storage account portal, go to <strong>Data management → Lifecycle management → Add rule</strong>. Create a rule to move blobs to <em>Cool</em> tier after 30 days and delete after 90 days.",
             []),
            ("Change replication type", "portal",
             "In the storage account, click <strong>Configuration</strong> and change replication from <em>GRS</em> to <em>LRS</em>. Note the availability impact.",
             []),
        ],
        "validation": [
            "Storage account exists with GRS → LRS replication change recorded.",
            "Blob <em>testfile.txt</em> is accessible via the SAS URL in a browser.",
            "AzCopy sync shows transferred files in the container listing.",
            "Lifecycle policy appears in <strong>Lifecycle management</strong> with correct tiers.",
        ],
        "cleanup": [
            "az group delete --name az104-rg7 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"sa","label":"Storage Account","sub":"Standard_GRS","x":170,"y":20,"w":180,"h":50,"type":"storage"},
            {"id":"blob","label":"Blob Storage","sub":"az104-container","x":50,"y":130,"w":130,"h":44,"type":"storage"},
            {"id":"file","label":"File Shares","sub":"SMB/NFS","x":200,"y":130,"w":120,"h":44,"type":"storage"},
            {"id":"table","label":"Tables","sub":"NoSQL","x":340,"y":130,"w":110,"h":44,"type":"storage"},
            {"id":"azcopy","label":"AzCopy","sub":"CLI Transfer","x":50,"y":225,"w":120,"h":44,"type":"default"},
            {"id":"sas","label":"SAS Token","sub":"Read-only","x":190,"y":225,"w":140,"h":44,"type":"default"},
            {"id":"lc","label":"Lifecycle Policy","sub":"Cool / Archive","x":350,"y":225,"w":130,"h":44,"type":"default"},
        ],
        "d_edges": [
            {"from":"sa","to":"blob"},{"from":"sa","to":"file"},{"from":"sa","to":"table"},
            {"from":"azcopy","to":"blob"},{"from":"sas","to":"blob"},{"from":"lc","to":"blob"},
        ],
        "d_groups": [
            {"label":"Services","x":30,"y":110,"w":440,"h":75,"type":"storage"},
        ],
    },
    {
        "id": "08", "slug": "lab-08",
        "title": "Manage Virtual Machines",
        "subtitle": "Deploy VMs, configure scale sets, and manage VM extensions",
        "duration": "45 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 8 — Manage Virtual Machines",
        "objectives": [
            "Deploy an Azure Virtual Machine with managed disks",
            "Configure VM auto-shutdown and disk snapshots",
            "Deploy a Virtual Machine Scale Set (VMSS) with autoscale",
            "Install the Custom Script Extension to configure VMs",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg8</em> with a VNet and subnet",
            "SSH key pair (generate with <code>ssh-keygen -t rsa -b 4096</code>)",
        ],
        "steps": [
            ("Deploy a VM", "portal",
             "Search for <strong>Virtual machines → + Create → Azure virtual machine</strong>. Set Resource group <em>az104-rg8</em>, VM name <em>az104-vm1</em>, Region <em>East US</em>, Image <em>Ubuntu Server 22.04 LTS</em>, Size <em>Standard_B2s</em>, Authentication type <em>SSH public key</em>, generate a new key pair. Click <strong>Review + create → Create</strong>.",
             []),
            ("Configure auto-shutdown", "portal",
             "Open <em>az104-vm1</em> in the portal. Go to <strong>Operations → Auto-shutdown</strong>. Enable it and set a time (e.g. 23:00 UTC). Add a notification email.",
             []),
            ("Snapshot a managed disk", "portal",
             "Open <em>az104-vm1 → Disks</em>. Click the OS disk name. In the disk blade, click <strong>+ Create snapshot</strong>. Set Name <em>az104-vm1-snap</em>, Resource group <em>az104-rg8</em>, Snapshot type <em>Full</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Deploy a VM Scale Set", "portal",
             "Search for <strong>Virtual machine scale sets → + Create</strong>. Set Resource group <em>az104-rg8</em>, name <em>az104-vmss1</em>, Region <em>East US</em>, Image <em>Ubuntu Server 22.04 LTS</em>, Size <em>Standard_B2s</em>, Initial instance count <em>2</em>, Upgrade policy <em>Automatic</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Install Custom Script Extension", "portal",
             "Open <em>az104-vmss1 → Extensions + applications → + Add</em>. Select <strong>Custom Script for Linux</strong>. In Settings, set Command to: <code>apt-get install -y nginx &amp;&amp; systemctl start nginx</code>. Click <strong>Save</strong>.",
             []),
            ("Configure autoscale rules", "portal",
             "Open <em>az104-vmss1</em> → <strong>Scaling</strong>. Add a scale-out rule (CPU &gt; 75% for 5 min → add 1 instance) and a scale-in rule (CPU &lt; 25% for 5 min → remove 1 instance).",
             []),
        ],
        "validation": [
            "VM <em>az104-vm1</em> is running and accessible via SSH.",
            "Snapshot <em>az104-vm1-snap</em> appears in the Disks blade.",
            "VMSS has 2 instances and shows <em>Succeeded</em> provisioning state.",
            "Nginx responds on each VMSS instance public IP.",
        ],
        "cleanup": [
            "az group delete --name az104-rg8 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"vmss","label":"VM Scale Set","sub":"az104-vmss1","x":175,"y":20,"w":170,"h":50,"type":"compute"},
            {"id":"vm1","label":"VM Instance 1","sub":"Standard_B2s","x":55,"y":130,"w":140,"h":44,"type":"compute"},
            {"id":"vm2","label":"VM Instance 2","sub":"Standard_B2s","x":210,"y":130,"w":140,"h":44,"type":"compute"},
            {"id":"vm3","label":"VM Instance 3","sub":"Auto-scaled","x":365,"y":130,"w":140,"h":44,"type":"compute"},
            {"id":"ext","label":"Custom Script Ext","sub":"Install nginx","x":60,"y":230,"w":150,"h":44,"type":"default"},
            {"id":"autoscale","label":"Autoscale","sub":"CPU-based rules","x":300,"y":230,"w":150,"h":44,"type":"default"},
        ],
        "d_edges": [
            {"from":"vmss","to":"vm1"},{"from":"vmss","to":"vm2"},{"from":"vmss","to":"vm3","dashed":True},
            {"from":"ext","to":"vm1"},{"from":"ext","to":"vm2"},
            {"from":"autoscale","to":"vmss"},
        ],
        "d_groups": [
            {"label":"Scale Set Instances","x":30,"y":110,"w":500,"h":75,"type":"compute"},
        ],
    },
    {
        "id": "09a", "slug": "lab-09a",
        "title": "Implement Web Apps",
        "subtitle": "Create Azure App Service web apps and configure deployment slots",
        "duration": "30 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 9 — PaaS Compute Options",
        "objectives": [
            "Create an App Service Plan and deploy a web application",
            "Configure deployment slots (staging and production)",
            "Deploy a web app using ZIP deploy and swap slots",
            "Configure autoscale and custom domain settings",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg9a</em>",
            "Azure CLI with the <code>webapp</code> extension",
        ],
        "steps": [
            ("Create an App Service Plan", "portal",
             "Search for <strong>App Service plans → + Create</strong>. Set Resource group <em>az104-rg9a</em>, Name <em>az104-plan1</em>, OS <em>Linux</em>, Region <em>East US</em>, Pricing tier <em>Standard S1</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Create a web app", "portal",
             "Search for <strong>App Services → + Create → Web App</strong>. Set Resource group <em>az104-rg9a</em>, Name (unique, e.g. <em>az104-webapp-[suffix]</em>), Publish <em>Code</em>, Runtime <em>Node 20 LTS</em>, OS <em>Linux</em>, Region <em>East US</em>, App Service Plan <em>az104-plan1</em>. Click <strong>Review + create → Create</strong>. Note the URL in the overview.",
             []),
            ("Create a staging deployment slot", "portal",
             "Open your web app → <strong>Deployment slots → + Add Slot</strong>. Enter name <em>staging</em>, leave <em>Don't clone settings</em> selected. Click <strong>Add</strong>.",
             []),
            ("Deploy to the staging slot", "portal",
             "Open the staging slot → <strong>Deployment Center → Settings</strong>. Choose <em>External Git</em> or use <strong>Advanced Tools (Kudu) → Zip Deploy</strong>. Upload a zip containing a simple <code>index.html</code> file to deploy your test content to staging.",
             []),
            ("Swap staging to production", "portal",
             "Return to the main web app blade. Click <strong>Deployment slots → Swap</strong>. Set Source <em>staging</em>, Target <em>production</em>. Review configuration changes, then click <strong>Swap</strong>.",
             []),
            ("Configure autoscale", "portal",
             "Open the App Service Plan in the portal. Go to <strong>Scale out (App Service plan)</strong> and add a CPU-based autoscale rule.",
             []),
        ],
        "validation": [
            "Web app is accessible at <code>https://&lt;app-name&gt;.azurewebsites.net</code>.",
            "Staging slot returns a different version than production before swap.",
            "After swap, production URL shows the staging content.",
        ],
        "cleanup": [
            "az group delete --name az104-rg9a --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"plan","label":"App Service Plan","sub":"Standard S1","x":165,"y":20,"w":190,"h":50,"type":"app"},
            {"id":"app","label":"Web App","sub":"Node.js 20 LTS","x":165,"y":115,"w":190,"h":50,"type":"app"},
            {"id":"prod","label":"Production Slot","sub":"/","x":55,"y":215,"w":145,"h":44,"type":"app"},
            {"id":"staging","label":"Staging Slot","sub":"/staging","x":325,"y":215,"w":145,"h":44,"type":"app"},
        ],
        "d_edges": [
            {"from":"plan","to":"app"},
            {"from":"app","to":"prod"},{"from":"app","to":"staging"},
            {"from":"staging","to":"prod","label":"Swap"},
        ],
        "d_groups": [],
    },
    {
        "id": "09b", "slug": "lab-09b",
        "title": "Azure Container Instances",
        "subtitle": "Deploy containerized workloads using Azure Container Instances",
        "duration": "20 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 9 — PaaS Compute Options",
        "objectives": [
            "Deploy a container from a public Docker image using ACI",
            "Configure environment variables and resource limits",
            "Inspect container logs and resource utilization",
            "Deploy a multi-container group using a YAML definition",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Resource group <em>az104-rg9b</em>",
        ],
        "steps": [
            ("Deploy a container instance", "portal",
             "Search for <strong>Container Instances → + Create</strong>. Set Resource group <em>az104-rg9b</em>, container name <em>az104-aci1</em>, image source <em>Other registry</em>, Image <em>nginx:latest</em>, OS <em>Linux</em>. Under <strong>Networking</strong>, set DNS label (e.g. <em>az104aci[random]</em>), open port <code>80</code>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Get the public IP and test", "portal",
             "Open <em>az104-aci1 → Overview</em>. Note the <strong>IP address</strong> and <strong>FQDN</strong> in the essentials panel. Open the FQDN in a browser — you should see the nginx welcome page.",
             []),
            ("View container logs", "portal",
             "In <em>az104-aci1</em>, click <strong>Containers</strong> in the sidebar. Select the container name, then click the <strong>Logs</strong> tab to view stdout/stderr output.",
             []),
            ("Deploy a multi-container group", "portal",
             "Search for <strong>Container Instances → + Create</strong>. On the <strong>Advanced</strong> tab, select <em>YAML</em> as the deployment option. Paste or upload a container group YAML that defines a <em>web</em> container (nginx:alpine, port 80) and a <em>sidecar</em> container (busybox). Review and create.",
             []),
            ("Monitor with Azure Monitor", "portal",
             "Open <em>az104-aci1</em> in the portal. Click <strong>Monitoring → Metrics</strong> to view CPU and memory utilization charts.",
             []),
        ],
        "validation": [
            "ACI container returns nginx welcome page on port 80.",
            "Container logs show HTTP request entries after the curl test.",
            "Multi-container group shows both <em>web</em> and <em>sidecar</em> containers running.",
        ],
        "cleanup": [
            "az container delete --name az104-aci1 --resource-group az104-rg9b --yes",
            "az container delete --name az104-aci-group --resource-group az104-rg9b --yes",
        ],
        "d_nodes": [
            {"id":"acr","label":"Container Registry","sub":"Public / ACR","x":165,"y":20,"w":190,"h":50,"type":"compute"},
            {"id":"img","label":"nginx:latest","sub":"Docker Image","x":165,"y":115,"w":190,"h":50,"type":"compute"},
            {"id":"aci","label":"Container Instance","sub":"az104-aci1","x":80,"y":215,"w":160,"h":44,"type":"compute"},
            {"id":"grp","label":"Container Group","sub":"web + sidecar","x":280,"y":215,"w":160,"h":44,"type":"compute"},
        ],
        "d_edges": [
            {"from":"acr","to":"img"},{"from":"img","to":"aci"},{"from":"img","to":"grp"},
        ],
        "d_groups": [],
    },
    {
        "id": "09c", "slug": "lab-09c",
        "title": "Azure Kubernetes Service",
        "subtitle": "Create an AKS cluster, deploy applications, and scale workloads",
        "duration": "40 min", "difficulty": "Advanced", "diff_color": "red",
        "module": "Module 9 — PaaS Compute Options",
        "objectives": [
            "Create an AKS cluster with Azure CNI networking",
            "Deploy an application using kubectl and a YAML manifest",
            "Expose the application with a Kubernetes LoadBalancer service",
            "Scale the deployment and configure Horizontal Pod Autoscaler",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "Azure CLI with <code>aks-preview</code> extension",
            "kubectl installed or use Cloud Shell (it's pre-installed)",
        ],
        "steps": [
            ("Create an AKS cluster", "portal",
             "Search for <strong>Kubernetes services → + Create → Create a Kubernetes cluster</strong>. Set Resource group <em>az104-rg9c</em>, cluster name <em>az104-aks1</em>, Region <em>East US</em>, Node size <em>Standard_B2s</em>, Node count <em>2</em>, Network plugin <em>Azure CNI</em>. Enable <strong>Managed identity</strong>. Click <strong>Review + create → Create</strong> (takes 4–6 min).",
             []),
            ("Get cluster credentials", "portal",
             "Open <em>az104-aks1 → Overview</em>. Click <strong>Connect</strong> to see the credentials command. In <strong>Cloud Shell</strong>, run the displayed <code>az aks get-credentials</code> command, then run <code>kubectl get nodes</code> to verify all nodes show <em>Ready</em>.",
             []),
            ("Deploy an application", "portal",
             "In Cloud Shell, run: <code>kubectl create deployment az104-nginx --image=nginx:latest --replicas=2</code> followed by <code>kubectl get pods -o wide</code> to see pods scheduled across nodes.",
             []),
            ("Expose via LoadBalancer service", "portal",
             "In Cloud Shell, run: <code>kubectl expose deployment az104-nginx --type=LoadBalancer --port=80</code> then <code>kubectl get svc az104-nginx --watch</code> to wait for an external IP (2–3 min). Open the IP in a browser to verify nginx responds.",
             []),
            ("Scale the deployment", "portal",
             "In <em>az104-aks1 → Workloads</em>, find the <em>az104-nginx</em> deployment. In Cloud Shell run: <code>kubectl scale deployment az104-nginx --replicas=4</code> and <code>kubectl autoscale deployment az104-nginx --cpu-percent=50 --min=2 --max=10</code> to configure HPA.",
             []),
            ("Monitor with Azure Monitor for containers", "portal",
             "In the portal, open <em>az104-aks1</em> → <strong>Insights</strong>. Explore the Cluster, Nodes, and Pods views. Review container CPU and memory metrics.",
             []),
        ],
        "validation": [
            "All cluster nodes show <em>Ready</em> status in <code>kubectl get nodes</code>.",
            "nginx deployment has 4 running pods.",
            "LoadBalancer service has an external IP and returns nginx page.",
            "HPA is configured and monitoring the deployment.",
        ],
        "cleanup": [
            "kubectl delete deployment az104-nginx",
            "kubectl delete svc az104-nginx",
            "az aks delete --name az104-aks1 --resource-group az104-rg9c --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"aks","label":"AKS Cluster","sub":"az104-aks1","x":170,"y":15,"w":180,"h":55,"type":"compute"},
            {"id":"cp","label":"Control Plane","sub":"Managed by Azure","x":50,"y":125,"w":150,"h":44,"type":"default"},
            {"id":"pool","label":"Node Pool","sub":"2× Standard_B2s","x":330,"y":125,"w":150,"h":44,"type":"compute"},
            {"id":"pod1","label":"Pod: nginx","sub":"replica 1","x":50,"y":225,"w":120,"h":40,"type":"compute"},
            {"id":"pod2","label":"Pod: nginx","sub":"replica 2","x":195,"y":225,"w":120,"h":40,"type":"compute"},
            {"id":"svc","label":"LB Service","sub":"External IP","x":340,"y":225,"w":130,"h":40,"type":"network"},
        ],
        "d_edges": [
            {"from":"aks","to":"cp"},{"from":"aks","to":"pool"},
            {"from":"pool","to":"pod1"},{"from":"pool","to":"pod2"},
            {"from":"svc","to":"pod1"},{"from":"svc","to":"pod2"},
        ],
        "d_groups": [],
    },
    {
        "id": "10", "slug": "lab-10",
        "title": "Implement Data Protection",
        "subtitle": "Configure Azure Backup and Azure Site Recovery for virtual machines",
        "duration": "45 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 10 — Data Protection",
        "objectives": [
            "Create a Recovery Services Vault and configure backup policies",
            "Enable Azure Backup for a virtual machine",
            "Perform an on-demand backup and validate the restore point",
            "Configure Azure Site Recovery replication to a secondary region",
        ],
        "prereqs": [
            "Azure subscription with <strong>Contributor</strong> role",
            "A running VM in resource group <em>az104-rg10</em> (East US)",
        ],
        "steps": [
            ("Create a Recovery Services Vault", "portal",
             "Search for <strong>Recovery Services vaults → + Create</strong>. Set Resource group <em>az104-rg10</em>, Vault name <em>az104-rsv1</em>, Region <em>East US</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Enable backup for the VM", "portal",
             "Open <em>az104-rsv1 → Backup</em>. Set Workload location <em>Azure</em>, Workload type <em>Virtual machine</em>. Click <strong>Backup</strong>. Under <strong>Backup policy</strong>, select <em>DefaultPolicy</em>. Click <strong>+ Add</strong> and select <em>az104-vm1</em>. Click <strong>Enable Backup</strong>.",
             []),
            ("Trigger an on-demand backup", "portal",
             "In <em>az104-rsv1 → Backup items → Azure Virtual Machine</em>, click <em>az104-vm1</em>. Click <strong>Backup now</strong>, set retention to <em>December 31, 2026</em>. Click <strong>OK</strong> to start the immediate backup.",
             []),
            ("Monitor backup job status", "portal",
             "In <em>az104-rsv1 → Backup jobs</em>, the in-progress job appears with status <em>InProgress</em>. Click the job to see details — data transferred, time elapsed. Refresh until it shows <strong>Completed</strong>.",
             []),
            ("Configure Site Recovery replication", "portal",
             "In the Recovery Services Vault, click <strong>Site Recovery → Replicate</strong>. Choose Source region <em>East US</em> → Target region <em>West US 2</em>. Select your VM and accept default replication settings.",
             []),
            ("Verify recovery points", "portal",
             "In the vault, go to <strong>Backup items → Azure Virtual Machine</strong>. Select <em>az104-vm1</em> to see recovery points and retention dates.",
             []),
        ],
        "validation": [
            "Backup job completes with <em>Completed</em> status.",
            "Recovery point is visible under the VM's backup item.",
            "Site Recovery shows the VM with <em>Replication health: Healthy</em> after initial sync.",
        ],
        "cleanup": [
            "# Stop replication before deleting",
            "# Portal: Site Recovery → Replicated items → Disable Replication",
            "# Then delete the resource group:",
            "az group delete --name az104-rg10 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"rsv","label":"Recovery Svcs Vault","sub":"az104-rsv1","x":155,"y":20,"w":210,"h":55,"type":"backup"},
            {"id":"bp","label":"Backup Policy","sub":"Daily  30-day retention","x":45,"y":130,"w":175,"h":44,"type":"backup"},
            {"id":"sr","label":"Site Recovery","sub":"Cross-region","x":300,"y":130,"w":175,"h":44,"type":"backup"},
            {"id":"vm","label":"VM","sub":"East US","x":45,"y":230,"w":130,"h":44,"type":"compute"},
            {"id":"rp","label":"Restore Point","sub":"Recovery Point","x":200,"y":230,"w":130,"h":44,"type":"backup"},
            {"id":"vm2","label":"VM Replica","sub":"West US 2","x":360,"y":230,"w":130,"h":44,"type":"compute"},
        ],
        "d_edges": [
            {"from":"rsv","to":"bp"},{"from":"rsv","to":"sr"},
            {"from":"bp","to":"vm"},{"from":"bp","to":"rp"},
            {"from":"sr","to":"vm"},{"from":"sr","to":"vm2","label":"Replicate"},
        ],
        "d_groups": [],
    },
    {
        "id": "11", "slug": "lab-11",
        "title": "Implement Monitoring",
        "subtitle": "Configure Azure Monitor, Log Analytics, and Application Insights",
        "duration": "45 min", "difficulty": "Intermediate", "diff_color": "yellow",
        "module": "Module 11 — Monitoring",
        "objectives": [
            "Create a Log Analytics workspace and connect resources",
            "Configure diagnostic settings to stream logs and metrics",
            "Create Azure Monitor alert rules with action groups",
            "Enable Application Insights on a web app and review telemetry",
        ],
        "prereqs": [
            "Azure subscription with <strong>Monitoring Contributor</strong> role",
            "A running VM and a web app in resource group <em>az104-rg11</em>",
        ],
        "steps": [
            ("Create a Log Analytics workspace", "portal",
             "Search for <strong>Log Analytics workspaces → + Create</strong>. Set Resource group <em>az104-rg11</em>, Name <em>az104-law1</em>, Region <em>East US</em>. Click <strong>Review + create → Create</strong>.",
             []),
            ("Configure VM diagnostic settings", "portal",
             "Open your VM → <strong>Monitoring → Diagnostic settings</strong>. Click <strong>+ Add diagnostic setting</strong>. Select all metric categories and send to <em>az104-law1</em>.",
             []),
            ("Enable VM Insights", "portal",
             "Open <em>az104-vm1</em> → <strong>Monitoring → Insights → Enable</strong>. Select workspace <em>az104-law1</em> and click <strong>Enable</strong>. The Dependency agent and Log Analytics agent will be installed automatically.",
             []),
            ("Create an alert rule", "portal",
             "Search for <strong>Monitor → Alerts → + Create → Alert rule</strong>. Set Scope to <em>az104-vm1</em>. Under Condition, select signal <em>Percentage CPU</em>, operator <em>Greater than</em>, threshold <em>80</em>, aggregation granularity <em>5 minutes</em>. Create an Action group for email notification. Name the rule <em>High-CPU-Alert</em> and click <strong>Review + create → Create</strong>.",
             []),
            ("Enable Application Insights", "portal",
             "Open your web app → <strong>Monitoring → Application Insights → Turn on Application Insights</strong>. Link to a new App Insights resource. Enable and save.",
             []),
            ("Run a Log Analytics query", "portal",
             "Open <em>az104-law1</em> → <strong>Logs</strong>. Run a KQL query to view VM performance:",
             [
                 "// VM CPU over last hour",
                 "Perf",
                 "| where TimeGenerated > ago(1h)",
                 "| where ObjectName == 'Processor'",
                 "| where CounterName == '% Processor Time'",
                 "| summarize avg(CounterValue) by Computer, bin(TimeGenerated, 5m)",
                 "| render timechart",
             ]),
        ],
        "validation": [
            "Log Analytics workspace shows ingested data (Heartbeat table) from the VM.",
            "Alert rule <em>High-CPU-Alert</em> appears in Azure Monitor → Alerts → Alert rules.",
            "Application Insights live metrics and dependency map load for the web app.",
            "KQL query returns results for Processor performance.",
        ],
        "cleanup": [
            "az monitor metrics alert delete --name 'High-CPU-Alert' --resource-group az104-rg11",
            "az group delete --name az104-rg11 --yes --no-wait",
        ],
        "d_nodes": [
            {"id":"mon","label":"Azure Monitor","sub":"Unified Monitoring","x":165,"y":15,"w":190,"h":55,"type":"monitor"},
            {"id":"law","label":"Log Analytics","sub":"az104-law1","x":50,"y":125,"w":155,"h":44,"type":"monitor"},
            {"id":"ai","label":"App Insights","sub":"Telemetry","x":330,"y":125,"w":155,"h":44,"type":"monitor"},
            {"id":"alert","label":"Alert Rules","sub":"CPU &gt; 80%","x":50,"y":225,"w":140,"h":44,"type":"monitor"},
            {"id":"dash","label":"Dashboard","sub":"Workbooks","x":215,"y":225,"w":140,"h":44,"type":"monitor"},
            {"id":"act","label":"Action Group","sub":"Email / SMS","x":375,"y":225,"w":130,"h":44,"type":"default"},
        ],
        "d_edges": [
            {"from":"mon","to":"law"},{"from":"mon","to":"ai"},
            {"from":"law","to":"alert"},{"from":"law","to":"dash"},
            {"from":"alert","to":"act"},
        ],
        "d_groups": [
            {"label":"Azure Monitor","x":30,"y":105,"w":460,"h":75,"type":"monitor"},
        ],
    },
]


# ── HTML Template ──────────────────────────────────────────────────────────────

DIFF_STYLE = {
    "Beginner":     ("bg-blue-500/10 text-blue-300 border border-blue-500/25",    "🔵"),
    "Intermediate": ("bg-amber-500/10 text-amber-300 border border-amber-500/25", "🟡"),
    "Advanced":     ("bg-red-500/10 text-red-300 border border-red-500/25",       "🔴"),
}

STEP_TYPE_LABEL = {
    "portal": ("Portal",     "bg-blue-500/10 text-blue-300 border border-blue-500/25"),
    "cli":    ("CLI",        "bg-emerald-500/10 text-emerald-300 border border-emerald-500/25"),
    "ps":     ("PowerShell", "bg-indigo-500/10 text-indigo-300 border border-indigo-500/25"),
}


def build_step(i, step):
    title, stype, desc, cmds = step
    label, badge_cls = STEP_TYPE_LABEL.get(stype, ("Portal", STEP_TYPE_LABEL["portal"][1]))

    code_block = ""
    if cmds:
        lines = "\n".join(cmds)
        code_block = f'''
        <div class="relative mt-3 group/code">
          <button onclick="copyCode(this)" title="Copy"
            class="copy-btn absolute top-2 right-2 opacity-0 group-hover/code:opacity-100 transition-opacity px-2 py-1 text-xs rounded text-slate-400" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14)">
            Copy
          </button>
          <pre class="code-block overflow-x-auto"><code>{lines}</code></pre>
        </div>'''

    desc_html = f'<p class="text-sm text-slate-400 mt-1">{desc}</p>' if desc else ""

    return f'''
      <div class="step-card flex gap-4">
        <div class="shrink-0">
          <div class="w-8 h-8 rounded-full ac-step-num flex items-center justify-center text-xs font-bold">{i}</div>
        </div>
        <div class="flex-1 min-w-0 pb-6 border-b border-white/5 last:border-0">
          <div class="flex items-center gap-2 flex-wrap">
            <h3 class="font-semibold text-sm text-slate-100">{title}</h3>
            <span class="text-xs px-2 py-0.5 rounded-full font-medium {badge_cls}">{label}</span>
          </div>
          {desc_html}{code_block}
        </div>
      </div>'''


def render_lab(lab, prev_lab, next_lab, img_path, accent_hex="#818CF8", accent_rgb="129,140,248"):
    lab_id = lab["id"]
    title = lab["title"]
    subtitle = lab["subtitle"]
    duration = lab["duration"]
    difficulty = lab["difficulty"]
    diff_cls, diff_emoji = DIFF_STYLE.get(difficulty, ("bg-slate-700 text-slate-300", "⚪"))
    module = lab["module"]

    objectives_html = "".join(
        f'<li class="flex items-start gap-2 text-sm text-slate-300"><span class="ac-text mt-0.5">✓</span>{o}</li>'
        for o in lab["objectives"]
    )
    prereqs_html = "".join(
        f'<li class="text-sm text-slate-400 flex items-start gap-2"><span class="text-slate-500 mt-0.5">•</span>{p}</li>'
        for p in lab["prereqs"]
    )
    steps_html = "".join(build_step(i + 1, s) for i, s in enumerate(lab["steps"]))
    validation_html = "".join(
        f'<li class="flex items-start gap-2 text-sm text-slate-300"><span class="text-green-400 mt-0.5">✓</span><span>{v}</span></li>'
        for v in lab["validation"]
    )
    cleanup_lines = "\n".join(lab["cleanup"])
    cleanup_html = f'''
          <div class="relative group/code">
            <button onclick="copyCode(this)" title="Copy"
              class="copy-btn absolute top-2 right-2 opacity-0 group-hover/code:opacity-100 transition-opacity px-2 py-1 text-xs rounded text-slate-400" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14)">
              Copy
            </button>
            <pre class="code-block overflow-x-auto"><code>{cleanup_lines}</code></pre>
          </div>'''

    prev_link = (
        f'<a href="{prev_lab["slug"]}.html" '
        f'class="flex items-center gap-2 text-sm text-slate-400 ac-link">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>'
        f'Lab {prev_lab["id"]}: {prev_lab["title"]}</a>'
        if prev_lab else '<div></div>'
    )
    next_link = (
        f'<a href="{next_lab["slug"]}.html" '
        f'class="flex items-center gap-2 text-sm text-slate-400 ac-link">'
        f'Lab {next_lab["id"]}: {next_lab["title"]}'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>'
        f'</a>'
        if next_lab else '<div></div>'
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Lab {lab_id} — {title} | BD Cloud Academy</title>
  <link rel="icon" type="image/svg+xml" href="/src/brand/logo/favicon.svg"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {{ --ac: {accent_hex}; --ac-rgb: {accent_rgb}; }}
    body {{ font-family: 'Inter', sans-serif; background: #040B18; }}
    /* Glass surfaces */
    .glass-nav {{
      background: linear-gradient(180deg, rgba(4,11,24,0.95) 0%, rgba(4,11,24,0.90) 100%);
      backdrop-filter: blur(20px) saturate(160%);
      -webkit-backdrop-filter: blur(20px) saturate(160%);
    }}
    .glass-panel {{
      background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.03) 100%);
      backdrop-filter: blur(20px) saturate(160%);
      -webkit-backdrop-filter: blur(20px) saturate(160%);
      border: 1px solid rgba(255,255,255,0.11);
      box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.16), inset 0 -1px 0 rgba(0,0,0,0.24), 0 8px 24px rgba(0,0,0,0.36);
    }}
    /* Accent helpers */
    .ac-text {{ color: var(--ac); }}
    .ac-badge {{
      background: rgba(var(--ac-rgb), 0.12);
      border: 1px solid rgba(var(--ac-rgb), 0.28);
      color: var(--ac);
    }}
    .ac-step-num {{
      background: rgba(var(--ac-rgb), 0.10);
      border: 1px solid rgba(var(--ac-rgb), 0.28);
      color: var(--ac);
    }}
    .ac-link {{ transition: color 0.2s; }}
    .ac-link:hover {{ color: var(--ac); }}
    .ac-border-hover:hover {{ border-color: rgba(var(--ac-rgb), 0.42); }}
    /* Code */
    .code-block {{
      background: rgba(4,8,18,0.80);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 8px;
      padding: 1rem 1.2rem;
      font-family: 'Cascadia Code','Fira Code','JetBrains Mono',monospace;
      font-size: 0.8rem;
      line-height: 1.6;
      color: #93c5fd;
      white-space: pre;
    }}
    .copy-btn {{ cursor: pointer; }}
    .copy-btn.copied {{ color: #34d399; }}
    .step-card + .step-card {{ margin-top: 1rem; }}
  </style>
</head>
<body class="text-slate-200 min-h-screen">

  <!-- NAV -->
  <nav class="sticky top-0 z-50 glass-nav border-b border-white/8">
    <div class="max-w-6xl mx-auto px-6 py-3 flex items-center gap-3 text-sm">
      <a href="../../../index.html#labs" class="flex items-center gap-1.5 text-slate-400 ac-link font-medium">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
        BD Cloud Academy
      </a>
      <span class="text-slate-600">/</span>
      <a href="../../../index.html#labs" class="text-slate-400 ac-link">AZ-104 Labs</a>
      <span class="text-slate-600">/</span>
      <span class="text-slate-100 font-semibold">Lab {lab_id}</span>
      <!-- User chip (right-aligned) -->
      <div class="ml-auto flex items-center gap-3">
        <span id="lab-user" class="hidden text-slate-400 font-medium max-w-[180px] truncate"></span>
        <a href="/.auth/logout?post_logout_redirect_uri=/login.html" id="lab-signout" class="hidden text-xs text-slate-500 hover:text-red-400 transition-colors">Sign out</a>
        <a href="/login.html" id="lab-login" class="hidden text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors">Sign in</a>
      </div>
    </div>
  </nav>
  <script>
    fetch('/.auth/me').then(r=>r.json()).then(d=>{{
      const p=d.clientPrincipal;
      if(p){{
        const u=document.getElementById('lab-user');u.textContent=p.userDetails;u.classList.remove('hidden');
        document.getElementById('lab-signout').classList.remove('hidden');
      }} else {{
        document.getElementById('lab-login').classList.remove('hidden');
      }}
    }}).catch(()=>{{}});
  </script>

  <!-- HEADER -->
  <header class="glass-nav border-b border-white/8">
    <div class="max-w-6xl mx-auto px-6 py-8">
      <div class="flex items-start justify-between gap-6 flex-wrap">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2.5 flex-wrap mb-3">
            <span class="text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full ac-badge">Lab {lab_id}</span>
            <span class="text-xs font-semibold px-3 py-1 rounded-full {diff_cls}">{diff_emoji} {difficulty}</span>
            <span class="text-xs text-slate-500 flex items-center gap-1">⏱ {duration}</span>
          </div>
          <h1 class="text-2xl font-bold text-slate-100 mb-1.5">{title}</h1>
          <p class="text-slate-400 text-sm mb-3">{subtitle}</p>
          <p class="text-xs text-slate-500 font-medium uppercase tracking-wider">{module}</p>
        </div>
        <!-- Objectives summary -->
        <div class="glass-panel rounded-xl p-4 min-w-72 max-w-sm">
          <h2 class="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3">Lab Objectives</h2>
          <ul class="space-y-1.5">{objectives_html}</ul>
        </div>
      </div>
    </div>
  </header>

  <!-- MAIN -->
  <main class="max-w-5xl mx-auto px-6 py-10">
    <div class="space-y-10">

      <!-- Prerequisites -->
      <div class="glass-panel rounded-xl p-5">
        <h2 class="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Prerequisites
        </h2>
        <ul class="space-y-2">{prereqs_html}</ul>
      </div>

      <!-- Steps + Diagram + Validation + Cleanup -->
      <div>
        <!-- Steps heading -->
        <h2 class="text-base font-bold text-slate-100 mb-6 flex items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ac-text"><path d="M14.5 10c-.83 0-1.5-.67-1.5-1.5v-5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5z"/><path d="M20.5 10H19V8.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/><path d="M9.5 14c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5S8 21.33 8 20.5v-5c0-.83.67-1.5 1.5-1.5z"/><path d="M3.5 14H5v1.5c0 .83-.67 1.5-1.5 1.5S2 16.33 2 15.5 2.67 14 3.5 14z"/><path d="M14 14.5c0-.83.67-1.5 1.5-1.5h5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-5c-.83 0-1.5-.67-1.5-1.5z"/><path d="M15.5 19H14v1.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5-.67-1.5-1.5-1.5z"/><path d="M10 9.5C10 8.67 9.33 8 8.5 8h-5C2.67 8 2 8.67 2 9.5S2.67 11 3.5 11h5c.83 0 1.5-.67 1.5-1.5z"/><path d="M8.5 5H10V3.5C10 2.67 9.33 2 8.5 2S7 2.67 7 3.5 7.67 5 8.5 5z"/></svg>
          Lab Steps
        </h2>

        <!-- Architecture Diagram — centred inline with steps -->
        <div class="glass-panel rounded-2xl overflow-hidden mb-8">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-white/8">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ac-text"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            <span class="text-xs font-bold uppercase tracking-widest text-slate-500">Architecture Diagram</span>
          </div>
          <div class="flex justify-center p-6 bg-[#030810]">
            <img src="../assets/diagrams/labs/{img_path}" alt="{title} Architecture Diagram"
                 class="rounded-xl object-contain"
                 style="max-height:520px; width:100%; max-width:860px;" loading="lazy"/>
          </div>
        </div>

        <!-- Step cards -->
        <div class="space-y-0 mb-10">{steps_html}</div>

        <!-- Validation -->
        <div class="bg-green-500/5 border border-green-500/20 rounded-xl p-5 mb-6">
          <h2 class="text-sm font-bold text-green-400 mb-3 flex items-center gap-2">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Validation Checklist
          </h2>
          <ul class="space-y-2">{validation_html}</ul>
        </div>

        <!-- Cleanup -->
        <div class="bg-red-500/5 border border-red-500/20 rounded-xl p-5">
          <h2 class="text-sm font-bold text-red-400 mb-3 flex items-center gap-2">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
            Cleanup Resources
          </h2>
          <p class="text-xs text-slate-500 mb-3">Run after the lab to avoid ongoing charges.</p>
          {cleanup_html}
        </div>
      </div>

      <!-- Back to lab list -->
      <div class="flex justify-center">
        <a href="../../../index.html#labs"
          class="flex items-center gap-2 px-5 py-2.5 text-sm text-slate-400 ac-link ac-border-hover glass-panel rounded-xl transition-colors">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          All AZ-104 Labs
        </a>
      </div>

    </div>
  </main>

  <!-- FOOTER NAV -->
  <footer class="glass-nav border-t border-white/8 mt-10">
    <div class="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
      {prev_link}
      <span class="text-xs text-slate-500">Lab {lab_id} of {len(LABS)}</span>
      {next_link}
    </div>
  </footer>

  <script>
    function copyCode(btn) {{
      const pre = btn.nextElementSibling;
      const text = pre.textContent;
      navigator.clipboard.writeText(text).then(() => {{
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 2000);
      }});
    }}
  </script>
</body>
</html>'''


def main():
    for i, lab in enumerate(LABS):
        prev_lab = LABS[i - 1] if i > 0 else None
        next_lab = LABS[i + 1] if i < len(LABS) - 1 else None
        accent_hex, accent_rgb = ACCENT_MAP.get(lab["slug"], ("#818CF8", "129,140,248"))

        img_filename = f'{lab["slug"]}.png'
        html = render_lab(lab, prev_lab, next_lab, img_filename, accent_hex, accent_rgb)

        out_path = OUT / f'{lab["slug"]}.html'
        out_path.write_text(html, encoding="utf-8")
        print(f"  ✓  {out_path.name}")

    print(f"\nGenerated {len(LABS)} lab pages in {OUT}")


if __name__ == "__main__":
    main()
