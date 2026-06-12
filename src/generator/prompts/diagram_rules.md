# Mermaid Diagram Rules for Training Slides

## Scope

Mermaid is for simple flows, sequences, decision trees, evaluation orders, comparisons,
and pie charts. Key architecture topology slides (multi-service Azure layouts) are
rendered as PNG images with official Azure icons by the pipeline — you will be told in
the user prompt when that applies; in that case emit NO diagram slide at all and never
attempt icon-style architecture in Mermaid.

## Supported Diagram Types

### Architecture / Flow
```
graph TB
    A[Service A] --> B[Service B]
    B --> C[(Database)]
    B --> D[Queue]
```

### Request / Response Sequence
```
sequenceDiagram
    participant C as Client
    participant AG as API Gateway
    participant S as Service
    C->>AG: Request
    AG->>S: Forward
    S-->>AG: Response
    AG-->>C: Result
```

### Decision / Process Flow
```
flowchart LR
    A([Start]) --> B{Condition?}
    B -->|Yes| C[Action A]
    B -->|No| D[Action B]
    C --> E([End])
    D --> E
```

### State / Comparison
```
graph LR
    subgraph IaaS
        VM[Virtual Machine]
        OS[Your OS]
    end
    subgraph PaaS
        App[Your App]
        Runtime[Managed Runtime]
    end
```

## Azure-Specific Templates (use these as starting points)

### Geography → Region → Availability Zone topology
```
graph TB
    subgraph Geo ["🌍 Geography: United States"]
        subgraph EastUS ["Region: East US"]
            AZ1["AZ 1"] --- AZ2["AZ 2"] --- AZ3["AZ 3"]
        end
    end
    User["👤 User"] -->|"low latency"| EastUS
    style Geo fill:#0B1120,stroke:#1E293B,color:#E2E8F0
    style EastUS fill:#0F172A,stroke:#0078D4,color:#E2E8F0
    style AZ1 fill:#0078D4,color:#fff,stroke:none
    style AZ2 fill:#0078D4,color:#fff,stroke:none
    style AZ3 fill:#0078D4,color:#fff,stroke:none
```

### Azure management hierarchy
```
graph TB
    MG["Management Group"] --> Sub1["Subscription: Prod"]
    MG --> Sub2["Subscription: Dev"]
    Sub1 --> RG1["Resource Group: web"]
    Sub1 --> RG2["Resource Group: data"]
    RG1 --> R1["App Service"]
    RG2 --> R2["Azure SQL"]
    style MG fill:#0078D4,color:#fff,stroke:none
    style Sub1 fill:#065F46,color:#6EE7B7,stroke:none
    style Sub2 fill:#065F46,color:#6EE7B7,stroke:none
    style RG1 fill:#78350F,color:#FDE68A,stroke:none
    style RG2 fill:#78350F,color:#FDE68A,stroke:none
```

### Shared-responsibility layer stack (IaaS vs PaaS vs SaaS)
```
graph TB
    subgraph IaaS ["IaaS — Azure VM"]
        I1["Apps & Data — You"]
        I2["OS & Runtime — You"]
        I3["Virtualisation — Microsoft"]
    end
    subgraph PaaS ["PaaS — App Service"]
        P1["Apps & Data — You"]
        P2["OS & Runtime — Microsoft"]
    end
    subgraph SaaS ["SaaS — Microsoft 365"]
        S1["Data config — You"]
        S2["Everything else — Microsoft"]
    end
    style I1 fill:#0078D4,color:#fff,stroke:none
    style I2 fill:#0078D4,color:#fff,stroke:none
    style P1 fill:#0078D4,color:#fff,stroke:none
    style S1 fill:#0078D4,color:#fff,stroke:none
    style I3 fill:#065F46,color:#6EE7B7,stroke:none
    style P2 fill:#065F46,color:#6EE7B7,stroke:none
    style S2 fill:#065F46,color:#6EE7B7,stroke:none
```

## Style Tokens

| Token | Value |
|---|---|
| Azure blue fill | `fill:#0078D4,color:#fff,stroke:none` |
| Dark card | `fill:#0F172A,stroke:#1E293B,color:#E2E8F0` |
| Success green | `fill:#065F46,color:#6EE7B7,stroke:none` |
| Warning amber | `fill:#78350F,color:#FDE68A,stroke:none` |
| Neutral | `fill:#1E293B,color:#94A3B8,stroke:#334155` |

## Rules

1. Max 12 nodes per diagram — split complex ones across two slides
2. Node IDs: alphanumeric only, no spaces or special chars
3. Node labels: wrap in `"..."` if they contain spaces or special chars
4. Avoid `()` in node IDs — use alphanumeric IDs with display labels
5. Subgraph titles must be simple strings (no quotes needed unless spaces)
6. Use `-->` for solid arrows, `-.->` for dashed, `==>` for thick
7. Always test that the Mermaid syntax is valid before outputting
