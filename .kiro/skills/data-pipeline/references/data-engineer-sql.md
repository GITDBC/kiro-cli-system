# SQL & Relational Database Knowledge

## Database fundamentals

- **Relational databases** store structured data in tables (rows/columns) with ACID
  guarantees: Atomicity, Consistency, Isolation, Durability
- **NoSQL databases** store unstructured data (documents, key-value, graphs) — better
  horizontal scalability but weaker consistency guarantees
- Relational databases scale vertically (bigger hardware); NoSQL scales horizontally
  (more nodes). NewSQL aims to combine both
- Use Entity Relationship Diagrams (ERD) to map table relationships. Distinguish fact
  tables (events, transactions) from dimension tables (context, attributes)

## SQL query patterns for data pipelines

When writing or reviewing SQL in pipeline contexts:

- Follow correct clause order:
  `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT`
- Use `IS NOT NULL` to filter missing data; impute NULLs with category averages via
  subqueries when appropriate
- Use CTEs (`WITH ... AS`) over nested subqueries for readability and reuse
- Use `CASE WHEN` for conditional classification in gold-layer aggregations
- Use window functions (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`) for deduplication and
  time-series analysis
- Prefer `LEFT JOIN` when the left table must retain all rows regardless of matches

## Aggregation patterns

- `SUM()`, `COUNT()`, `AVG()`, `MIN()`, `MAX()` for basic metrics
- `GROUP BY` to aggregate by dimension; `HAVING` to filter aggregated results
- `COUNT(DISTINCT col)` for cardinality checks in data quality validation
- Always alias computed columns for clarity: `AVG(salary) AS avg_salary`

## Schema design for pipelines

- Use appropriate types: `INT`, `VARCHAR(n)`, `TEXT`, `BOOLEAN`, `TIMESTAMP`,
  `NUMERIC(precision, scale)`
- Define primary keys and foreign key relationships for referential integrity
- Use `ALTER TABLE` for schema evolution; prefer additive changes (new columns) over
  destructive ones (drop columns)
- Use `COPY ... FROM ... CSV HEADER` for bulk data loading (PostgreSQL)

## Performance considerations

- Avoid `LIKE '%pattern%'` (leading wildcard) — forces full table scan
- Use `BETWEEN` for range queries instead of chained `>=` and `<=`
- Use `IN (...)` for set membership instead of chained `OR` conditions
- Index columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses

## Database Schema Design

### Design methodology

Follow a progressive refinement approach:

1. **Requirements** — Identify entities, relationships, access patterns, and volumetrics
2. **Conceptual model** — ERD with entities and relationships only (no types, no keys)
3. **Logical model** — Add attributes, primary keys, foreign keys, cardinality
4. **Physical model** — Data types, indexes, partitioning, engine-specific optimizations

### Normalization guidance

- Normalize to 3NF by default — it prevents update anomalies and keeps writes clean
- Denormalization is acceptable for read-heavy gold layers, reporting tables, and
  materialized views where join cost outweighs storage cost
- Document every intentional denormalization with the reason and the query pattern it
  serves

### Index strategy

| Index Type      | When to Use                                          |
| --------------- | ---------------------------------------------------- |
| Covering index  | Query can be satisfied entirely from the index       |
| Composite index | Multi-column filters or sorts (leftmost prefix rule) |
| Partial index   | Filtering on a subset of rows (e.g., active records) |

- Index columns that appear in `WHERE`, `JOIN`, `ORDER BY`
- Avoid over-indexing — each index adds write overhead and storage cost

### Migration patterns

- Prefer **additive-only** changes: new columns, new tables, new indexes
- All migrations should be **backward-compatible** — old code must work during rollout
- For breaking changes, use the **expand-contract pattern**:
  1. Expand: add new column/table alongside the old one
  2. Migrate: backfill data, switch writers to new schema
  3. Contract: remove old column/table after all readers migrate
- This enables zero-downtime deployments

### Schema review checklist

- [ ] Naming: `snake_case`, consistent pluralization, no reserved words
- [ ] Data types: smallest type that fits, `TIMESTAMP WITH TIME ZONE` for times
- [ ] Constraints: `NOT NULL` where applicable, `CHECK` for value ranges
- [ ] Primary keys: defined on every table
- [ ] Foreign keys: referential integrity enforced, `ON DELETE` behavior specified
- [ ] Indexes: covering access patterns, no redundant indexes
- [ ] Defaults: sensible defaults for optional columns

### Output format

Deliver schema work as a **Schema Design Document** with these sections:

1. **ERD** — Mermaid `erDiagram` showing entities and relationships
2. **Table Definitions** — DDL with types, constraints, and comments
3. **Index Strategy** — Index definitions with rationale per index
4. **Migration Plan** — Ordered migration scripts with rollback steps
5. **Data Contracts** — Expected schema, ownership, SLA, consumers
