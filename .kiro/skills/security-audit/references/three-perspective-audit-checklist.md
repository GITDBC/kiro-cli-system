# Security Audit Playbook

## Audit Scope Definition

Before starting, confirm:

- [ ] Target: which services/modules/repos are in scope
- [ ] Depth: surface scan vs deep dive
- [ ] Compliance: which frameworks apply (OWASP, SOC2, GDPR, PCI-DSS)
- [ ] Access: what credentials/environments are available for testing

## Three-Perspective Analysis

### Perspective 1: Attacker (Offensive)

Think like an attacker. For each entry point:

1. **Enumerate attack surface**
   - Public endpoints (APIs, web forms, file uploads)
   - Authentication flows (login, password reset, MFA)
   - Authorization boundaries (role escalation, IDOR)
   - Data inputs (injection points, deserialization)

2. **OWASP Top 10 checklist**
   - A01: Broken Access Control — Can users access other users' data?
   - A02: Cryptographic Failures — Are secrets exposed? Weak algorithms?
   - A03: Injection — SQL, NoSQL, OS command, LDAP injection vectors?
   - A04: Insecure Design — Business logic flaws? Race conditions?
   - A05: Security Misconfiguration — Default creds? Verbose errors? CORS?
   - A06: Vulnerable Components — Known CVEs in dependencies?
   - A07: Auth Failures — Weak passwords? Brute force protection?
   - A08: Data Integrity — Unsigned updates? Deserialization?
   - A09: Logging Failures — Are security events logged? Tamper-proof?
   - A10: SSRF — Can the server be tricked into making internal requests?

3. **Prioritize by exploitability**
   - How easy is it to exploit? (automated tool vs manual expert)
   - What's the impact? (data breach, RCE, DoS)
   - Is it exposed to the internet or internal only?

### Perspective 2: Defender (Defensive)

Evaluate existing controls:

1. **Authentication & Authorization**
   - Token validation (JWT signature, expiry, audience)
   - Session management (timeout, rotation, invalidation)
   - RBAC/ABAC implementation correctness
   - MFA enforcement for sensitive operations

2. **Data Protection**
   - Encryption at rest (database, file storage, backups)
   - Encryption in transit (TLS version, certificate pinning)
   - PII handling (masking, retention, deletion)
   - Secret management (vault, rotation, no hardcoded secrets)

3. **Infrastructure Security**
   - Network segmentation (VPC, security groups, firewalls)
   - Container security (base images, privilege escalation)
   - CI/CD pipeline security (signed artifacts, SAST/DAST)
   - Dependency management (automated CVE scanning)

### Perspective 3: Compliance

Map findings to compliance requirements:

| Finding   | OWASP | SOC2  | GDPR   | Severity                 |
| --------- | ----- | ----- | ------ | ------------------------ |
| [finding] | A0X   | CC6.1 | Art.32 | Critical/High/Medium/Low |

## Severity Scoring

Use CVSS-like scoring adapted for application security:

| Severity | Criteria                                        | SLA to fix |
| -------- | ----------------------------------------------- | ---------- |
| Critical | RCE, auth bypass, data breach possible          | 24 hours   |
| High     | Privilege escalation, significant data exposure | 7 days     |
| Medium   | Information disclosure, limited impact          | 30 days    |
| Low      | Best practice violation, defense-in-depth       | 90 days    |

## Finding Report Format

For each finding:

```markdown
### [FINDING-ID]: [Title]

**Severity**: Critical / High / Medium / Low **Category**: OWASP A0X — [Name]
**Location**: `path/to/file:line` or endpoint `POST /api/resource` **Confidence**: HIGH
(direct code, configuration, or dependency evidence cited) / MEDIUM (inferred, needs
manual confirmation)

**Description**: What the vulnerability is and why it matters.

**Evidence**: Code snippet, request/response, or configuration showing the issue.

**Impact**: What an attacker could achieve by exploiting this.

**Remediation**:

1. [Specific fix with code example]
2. [Additional hardening]

**Verification**: How to confirm the fix works.
```

## Quick Wins Checklist

These are common issues that are easy to fix:

- [ ] Remove verbose error messages in production (stack traces, SQL errors)
- [ ] Add rate limiting to authentication endpoints
- [ ] Enable security headers (CSP, HSTS, X-Frame-Options)
- [ ] Remove unused endpoints and debug routes
- [ ] Update dependencies with known CVEs
- [ ] Ensure all API endpoints require authentication (unless explicitly public)
- [ ] Add input validation on all user-supplied data
- [ ] Enable audit logging for admin actions
