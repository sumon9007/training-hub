#!/usr/bin/env python3
"""
Training Hub — Azure-icon diagram renderer

Renders a JSON diagram spec into a PNG with official Azure icons using the
`diagrams` library (Graphviz under the hood). The spec is produced by the LLM
pipeline (see generate.py) but is deterministic to render, hand-editable, and
cached on disk next to its PNG.

Spec format:
{
  "title": "Hub-and-Spoke Network Topology",
  "direction": "LR",
  "clusters": [
    {"label": "Hub VNet", "nodes": [
        {"id": "fw", "service": "firewall", "label": "Azure Firewall"}
    ]}
  ],
  "nodes": [{"id": "user", "service": "users", "label": "Admins"}],
  "edges": [{"from": "user", "to": "fw", "label": "Bastion"}]
}

Standalone usage:
  .venv/bin/python src/generator/diagram_render.py --spec spec.json --out out.png
"""

import argparse
import json
import sys
from pathlib import Path

# Dark-theme rendering attributes — match src/theme/training.css palette
GRAPH_ATTR = {
    "rankdir": "LR",
    "splines": "ortho",
    "nodesep": "0.5",
    "ranksep": "0.7",
    "pad": "0.4",
    "bgcolor": "transparent",
    "fontcolor": "#E2E8F0",
    "fontname": "Helvetica",
    "fontsize": "16",
}
NODE_ATTR = {
    "fontcolor": "#E2E8F0",
    "fontname": "Helvetica",
    "fontsize": "11",
}
EDGE_ATTR = {
    "color": "#64748B",
    "fontcolor": "#94A3B8",
    "fontname": "Helvetica",
    "fontsize": "10",
    "penwidth": "1.4",
}
CLUSTER_ATTR = {
    "bgcolor": "#0F172A",
    "pencolor": "#334155",
    "fontcolor": "#7DD3FC",
    "fontname": "Helvetica",
    "fontsize": "12",
    "style": "rounded",
    "margin": "14",
    "labeljust": "l",
}


def _build_service_map():
    """Whitelisted service keys → diagrams node classes (AZ-104 scope)."""
    from diagrams.azure import compute, storage, network, networking, identity, security
    from diagrams.azure import monitor, managementgovernance as mg, general, databases, web, other, devops
    from diagrams.azure.azurestack import Capacity as OnPremServer

    return {
        # Compute
        "vm": compute.VM,
        "vm_windows": compute.VMWindows,
        "vm_linux": compute.VMLinux,
        "vmss": compute.VMScaleSets,
        "availability_set": compute.AvailabilitySets,
        "disk": compute.Disks,
        "disk_snapshot": compute.DiskSnapshots,
        "app_service": web.AppServices,
        "app_service_plan": web.AppServicePlans,
        "function_app": compute.FunctionApps,
        "aks": compute.AKS,
        "aci": compute.ContainerInstances,
        "container_apps": compute.ContainerApps,
        "acr": compute.ContainerRegistries,
        # Storage
        "storage_account": storage.StorageAccounts,
        "blob": storage.BlobStorage,
        "files": storage.AzureFileshares,
        "queue": storage.QueuesStorage,
        "table": storage.TableStorage,
        "file_sync": storage.StorageSyncServices,
        "storage_explorer": storage.StorageExplorer,
        "archive": storage.ArchiveStorage,
        # Networking
        "vnet": network.VirtualNetworks,
        "subnet": networking.Subnet,
        "nsg": networking.NetworkSecurityGroups,
        "asg": network.ApplicationSecurityGroups,
        "firewall": networking.Firewalls,
        "bastion": networking.Bastions,
        "load_balancer": networking.LoadBalancers,
        "app_gateway": networking.ApplicationGateways,
        "front_door": networking.FrontDoorAndCDNProfiles,
        "traffic_manager": networking.TrafficManagerProfiles,
        "vpn_gateway": network.VirtualNetworkGateways,
        "local_gateway": network.LocalNetworkGateways,
        "dns": networking.DNSZones,
        "private_dns": network.DNSPrivateZones,
        "private_endpoint": network.PrivateEndpoint,
        "service_endpoint": network.ServiceEndpointPolicies,
        "public_ip": networking.PublicIpAddresses,
        "route_table": networking.RouteTables,
        "nat": networking.Nat,
        "nic": networking.NetworkInterfaces,
        "network_watcher": monitor.NetworkWatcher,
        # Identity & governance
        "entra_id": identity.AzureActiveDirectory,
        "users": identity.Users,
        "groups": identity.Groups,
        "managed_identity": identity.ManagedIdentities,
        "conditional_access": identity.ConditionalAccess,
        "key_vault": security.KeyVaults,
        "policy": mg.Policy,
        "management_group": general.ManagementGroups,
        "subscription": general.Subscriptions,
        "resource_group": general.Resourcegroups,
        "cost_management": general.CostManagement,
        "advisor": mg.Advisor,
        # Monitoring & backup
        "monitor": monitor.Monitor,
        "log_analytics": monitor.LogAnalyticsWorkspaces,
        "metrics": monitor.Metrics,
        "logs": monitor.Logs,
        "alerts": mg.Alerts,
        "app_insights": monitor.ApplicationInsights,
        "workbooks": monitor.AzureWorkbooks,
        "autoscale": monitor.AutoScale,
        "recovery_vault": mg.RecoveryServicesVaults,
        "backup_vault": other.BackupVault,
        # Data & tools
        "sql": databases.SQLDatabase,
        "cosmos": databases.AzureCosmosDb,
        "arm_template": general.Templates,
        "cloud_shell": other.AzureCloudShell,
        "powershell": general.Powershell,
        "devops": devops.AzureDevops,
        # Context
        "internet": general.GlobeSuccess,
        "on_premises": OnPremServer,
        "generic": general.Resource,
    }


def service_keys() -> list[str]:
    """Whitelist keys, for embedding in the LLM spec-extraction prompt."""
    return sorted(_build_service_map().keys())


def render_spec(spec: dict, out_path: Path) -> tuple[int, int]:
    """Render a diagram spec to PNG. Returns (width, height) when PIL is available, else (0, 0)."""
    from diagrams import Cluster, Diagram, Edge

    service_map = _build_service_map()
    generic = service_map["generic"]
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    graph_attr = {**GRAPH_ATTR, "rankdir": spec.get("direction", "LR")}
    nodes: dict[str, object] = {}

    def make_node(n: dict):
        cls = service_map.get(n.get("service", ""), generic)
        nodes[n["id"]] = cls(n.get("label", n["id"]))

    # `diagrams` appends .png itself — pass the path without the suffix
    with Diagram(
        spec.get("title", ""),
        filename=str(out_path.with_suffix("")),
        outformat="png",
        show=False,
        graph_attr=graph_attr,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        for cluster in spec.get("clusters", []):
            with Cluster(cluster.get("label", ""), graph_attr=CLUSTER_ATTR):
                for n in cluster.get("nodes", []):
                    make_node(n)
        for n in spec.get("nodes", []):
            make_node(n)
        for e in spec.get("edges", []):
            src, dst = nodes.get(e.get("from")), nodes.get(e.get("to"))
            if src is None or dst is None:
                continue
            label = e.get("label", "")
            src >> Edge(label=label) >> dst if label else src >> dst

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"diagram render produced no output: {out_path}")

    try:
        from PIL import Image
        with Image.open(out_path) as img:
            return img.size
    except ImportError:
        return (0, 0)


def main():
    parser = argparse.ArgumentParser(description="Render an Azure-icon diagram spec to PNG")
    parser.add_argument("--spec", required=True, help="Path to the spec JSON file")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    w, h = render_spec(spec, Path(args.out))
    dims = f" ({w}x{h})" if w else ""
    print(f"✓ rendered {args.out}{dims}")
    if w and h and h > w:
        print("  ⚠ diagram is portrait — consider direction=LR or fewer ranks", file=sys.stderr)


if __name__ == "__main__":
    main()
