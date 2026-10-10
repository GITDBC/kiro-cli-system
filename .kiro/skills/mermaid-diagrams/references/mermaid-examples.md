# Mermaid Worked Examples

One renderable example per diagram type. Load the entry for the type being written; the
syntax rules, the type-selection table and the per-type legends stay in `SKILL.md` and
apply to every example here.

Every example below satisfies the critical syntax rules: alphanumeric node IDs, plain
label text, spaces around arrows, no custom styling.

## Flowchart

```mermaid
flowchart TD
    Client[Client App] --> Gateway[API Gateway]
    Gateway --> AuthSvc[Auth Service]
    Gateway --> DataSvc[Data Service]
    DataSvc --> DB[(PostgreSQL)]
    AuthSvc --> Cache[(Redis)]
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: POST /login
    S->>DB: Query user
    DB-->>S: User record
    S-->>C: 200 JWT token
```

## ER Diagram

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "is in"
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: start
    Processing --> Done: success
    Processing --> Error: failure
    Error --> Idle: retry
    Done --> [*]
```

## Class Diagram

```mermaid
classDiagram
    class BaseConfig {
        +str name
        +int timeout
    }
    class ETLPipeline {
        +BaseConfig config
        +run() DataFrame
    }
    BaseConfig <|-- ETLPipeline
```
