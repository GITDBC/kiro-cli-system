# Security Engineer — Technical Patterns

Reference patterns for the security-engineer agent. Load when performing threat
modeling, secure code review, or setting up security pipelines.

## Threat Model Document Template

```markdown
# Threat Model: [Application Name]

## System Overview

- **Architecture**: [Monolith/Microservices/Serverless]
- **Data Classification**: [PII, financial, health, public]
- **Trust Boundaries**: [User → API → Service → Database]

## STRIDE Analysis

| Threat            | Component      | Risk | Mitigation                         |
| ----------------- | -------------- | ---- | ---------------------------------- |
| Spoofing          | Auth endpoint  | High | MFA + token binding                |
| Tampering         | API requests   | High | HMAC signatures + input validation |
| Repudiation       | User actions   | Med  | Immutable audit logging            |
| Info Disclosure   | Error messages | Med  | Generic error responses            |
| Denial of Service | Public API     | High | Rate limiting + WAF                |
| Elevation of Priv | Admin panel    | Crit | RBAC + session isolation           |
```

## Secure API Endpoint Pattern

```python
import logging
import re

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)
app = FastAPI()
security = HTTPBearer()


class UserInput(BaseModel):
    """
    Validated user input with strict constraints.

    Attributes:
        username: Alphanumeric username (3-30 chars).
        email: Valid email address.
    """

    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., max_length=254)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username contains only safe characters.

        Args:
            v: Raw username value.

        Returns:
            Validated username string.
        """

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username contains invalid characters.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Validate email format.

        Args:
            v: Raw email value.

        Returns:
            Validated email string.
        """

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email format.")
        return v


@app.post("/api/users")
async def create_user(
    user: UserInput,
    token: str = Depends(security),
) -> dict[str, str]:
    """
    Create a new user with validated input.

    Args:
        user: Validated user input.
        token: Bearer authentication token.

    Returns:
        Creation status with username.
    """

    logger.info("[INFO] User created: %s.", user.username)
    return {"status": "created", "username": user.username}
```

## CI/CD Security Pipeline — Additional Scan Stages

The base Build → Lint → Test → SonarQube pipeline (Jenkins declarative and GitLab CI
forms) lives in `cicd-pipeline-design/references/cicd-automation-patterns.md` — load
that file first for the complete, runnable pipeline. The fragments below are the three
security-specific stages this skill inserts between `Test` and `SonarQube`; they are not
a standalone pipeline.

### Jenkins — insert after `stage('Test')`, before `stage('SonarQube')`

```groovy
stage('SAST') {
    steps {
        sh 'semgrep --config=p/owasp-top-ten --config=p/cwe-top-25 src/'
    }
}

stage('Dependency Scan') {
    steps {
        sh 'pip-audit --strict'
    }
}

stage('Secrets Scan') {
    steps {
        sh 'gitleaks detect --source=. --verbose'
    }
}
```

### GitLab CI — insert a `security` stage after `test`, before `quality`

```yaml
# Add "security" between "test" and "quality" in the owner's `stages:` list.
sast:
  stage: security
  script:
    - semgrep --config=p/owasp-top-ten --config=p/cwe-top-25 src/
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == "main"

dependency-scan:
  stage: security
  script:
    - pip-audit --strict
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == "main"

secrets-scan:
  stage: security
  script:
    - gitleaks detect --source=. --verbose
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == "main"
```
