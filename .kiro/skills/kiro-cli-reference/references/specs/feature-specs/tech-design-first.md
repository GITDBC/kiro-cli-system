> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Design-First Workflow

> Start with technical design and system architecture, then derive feasible requirements

The Design-First workflow starts with a technical design or system architecture and derives feasible requirements from it.

## When to Use

This workflow is ideal when:

- **Rapid prototyping** - You know the tech stack and want to explore what's possible
- **Technical constraints** - System must meet strict non-functional requirements (latency, throughput, uptime, compliance)
- **Existing designs** - You have architecture diagrams or design documents to port into Kiro
- **Feasibility exploration** - You want to understand what requirements are achievable given a design
- **Strong opinions** - You have specific architectural preferences or constraints

## Workflow Steps

### 1. Create Feature Spec

From the Kiro panel or command palette, create a new Feature Spec. When prompted, select **Design-First** workflow.

### 2. Choose Detail Level

Select the level of architectural detail you want to provide:

#### High Level Design
Full architecture including:
- System architecture diagram
- Component descriptions and interactions
- Technical approach and patterns
- Non-functional properties (performance, scalability, security)

**Best for:** Complex systems, team collaboration, thorough documentation

#### Low Level Design
Focused on implementation details:
- Algorithmic pseudocode
- Interface definitions and contracts
- Key data structures
- Non-functional properties

**Best for:** Rapid prototyping, quick feasibility checks, solo development

### 3. Design Phase

Kiro generates a `design.md` document based on your prompt and chosen detail level.

**What's included:**
- System components and their responsibilities
- Data flow and interactions
- Technology stack and frameworks
- API contracts and interfaces
- Non-functional considerations

**Your role:**
- Review the architecture for accuracy
- Iterate on the design by providing feedback
- Explore alternative approaches if needed
- Confirm when the architecture meets your needs

**Tip:** The design document opens in preview mode by default for better readability. Click "Edit" to make changes.

### 4. Requirements Phase

Once you confirm the architecture, Kiro derives requirements that are feasible given the technical design.

**What's generated:**
- User stories aligned with architectural capabilities
- System behaviors in EARS format
- Functional requirements scoped to the design
- Edge cases and error handling

**Key benefit:** Requirements are guaranteed to be technically feasible since they're derived from a validated architecture.

**Your role:**
- Review requirements for completeness
- Add any missing user-facing behaviors
- Confirm requirements match your expectations

### 5. Tasks Phase

Identical to Requirements-First workflow - Kiro generates executable implementation tasks.

### 6. Implementation

Execute tasks individually or run all tasks to implement the feature.

## Best Practices

### Start with Clear Technical Constraints

Be explicit about:
- Required technologies or services
- Performance requirements (latency, throughput)
- Scalability needs
- Compliance or security requirements
- Integration points with existing systems

**Example prompt:**
```
Create an MCP server for querying our Redshift data lake. Must use FastAPI 
and mcp-python. Target: <100ms query latency for 95th percentile. 
No UI components needed - pure API server.
```

### Iterate on Architecture Before Requirements

The power of Design-First is exploring technical designs. Take time to:
- Try different architectural approaches
- Evaluate trade-offs (latency vs. cost, complexity vs. maintainability)
- Validate non-functional requirements are achievable
- Get the design right before locking in requirements

### Use High Level Design for Team Projects

If multiple people will work on the implementation, choose High Level Design for better documentation and shared understanding.

### Use Low Level Design for Rapid Validation

When you want to quickly check if an idea is feasible, Low Level Design gets you to validation faster with implementation details.

### Upload Existing Designs

If you have architecture diagrams from draw.io, Lucidchart, or hand-drawn sketches:
1. Export as PNG or upload photos
2. Include in your initial prompt
3. Kiro will incorporate the visual design into the architecture document

## Common Patterns

### Pattern 1: Porting External Designs

**Scenario:** You have a design document from another tool or meeting notes.

**Approach:**
1. Copy the design content or upload diagrams
2. Select Design-First workflow
3. Choose High Level Design
4. Let Kiro formalize the design into design.md
5. Derive requirements from the formalized design

### Pattern 2: Exploring Technical Feasibility

**Scenario:** You want to know if a feature is possible with specific constraints.

**Approach:**
1. Describe the technical constraints and rough architecture
2. Select Design-First workflow
3. Choose Low Level Design for faster iteration
4. Review generated requirements to see what's feasible
5. Iterate on architecture if requirements don't match expectations

### Pattern 3: Prototyping with Known Stack

**Scenario:** Customer specifies exact services (Lambda, S3, DynamoDB) and you need to prototype quickly.

**Approach:**
1. Describe the tech stack and high-level flow
2. Select Design-First workflow
3. Generate architecture with specified services
4. Derive requirements showing what the system can do
5. Execute tasks to build the prototype

### Pattern 4: Meeting Strict Non-Functional Requirements

**Scenario:** System must meet specific latency, throughput, or compliance requirements.

**Approach:**
1. Define non-functional requirements in initial prompt
2. Select Design-First workflow
3. Choose High Level Design to document compliance approach
4. Validate architecture meets all constraints
5. Derive requirements that are achievable within constraints

## Troubleshooting

### Requirements Don't Match Expectations

If generated requirements don't align with what you want:
1. Go back and iterate on the architecture
2. Add more detail about intended capabilities
3. Clarify non-functional requirements
4. Regenerate requirements from updated architecture

### Architecture Too Generic

If the architecture lacks specificity:
1. Provide more technical details in your prompt
2. Specify exact frameworks, libraries, or services
3. Include performance numbers and constraints
4. Choose High Level Design for more depth

### Need to Change Design After Requirements

If you need to modify the design after requirements are generated:
1. Edit the design.md document
2. Ask Kiro to validate requirements against updated architecture
3. Regenerate requirements if needed
4. This is expected - iteration is part of the process

## Example Prompts

### High Level Design

```
Design a real-time notification system using AWS services. Must support:
- 100k concurrent WebSocket connections
- <50ms message delivery latency
- Message persistence for offline users
- Integration with existing user authentication service

Use API Gateway WebSocket, Lambda, DynamoDB, and SQS. Include 
architecture diagram showing component interactions and data flow.
```

### Low Level Design

```
Build a rate limiter middleware for our Express API. Requirements:
- Token bucket algorithm
- Per-user and per-IP limits
- Redis for distributed state
- Configurable limits per endpoint

Show pseudocode for the core algorithm and interface definitions.
```

## Benefits of Design-First

1. **Produces feasible requirements** - Requirements are derived from validated technical design
2. **Avoids reconciliation frustration** - No need to update requirements when exploring designs
3. **Saves time and credits** - Fewer iterations between requirements and design
4. **Explores technical options** - Try different technical approaches before committing
5. **Validates constraints early** - Ensure non-functional requirements are achievable
