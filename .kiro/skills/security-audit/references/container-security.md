# Container Security

This file is the reference that the security-audit skill loads when the audit target
includes container images, Dockerfiles, or container runtime configuration. It supplies
the checks for perspective C (configuration and dependencies) defined in
`three-perspective-audit-checklist.md`.

## Checklist index

| Check ID                       | Topic                        | Check statement                                                                                                              | Severity guidance                                                                                            | Audit evidence                                                                                                                                                                |
| ------------------------------ | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| sca-static-analysis            | Supply chain and build       | Application code and its libraries are analysed statically for vulnerabilities.                                              | Medium: flaws are found before release, but rarely exploitable alone (not stated upstream).                  | CI job running a SAST or software composition analysis tool, with recorded results.                                                                                           |
| image-trusted-base             | Supply chain and build       | Base images come from official or verified publishers.                                                                       | High: an untrusted base can carry malware or backdoors (not stated upstream).                                | `FROM` lines name official or verified images; no unknown namespaces.                                                                                                         |
| image-minimal-base             | Supply chain and build       | Images are built on a minimal base such as Alpine, scratch or distroless.                                                    | Medium: fewer packages and tools reduce exposure (not stated upstream).                                      | `FROM` names a minimal image; the package inventory of the image is short.                                                                                                    |
| image-small-single-process     | Supply chain and build       | Each image runs one application, stays small and has few layers.                                                             | Low: reduces attack surface without being exploitable alone (not stated upstream).                           | One entrypoint process per image; size and layer count reviewed.                                                                                                              |
| image-multistage-build         | Supply chain and build       | Multi-stage builds ship only runtime binaries and dependencies.                                                              | Low: removes build tools and intermediate files (not stated upstream).                                       | Several `FROM` stages; the final stage has no compiler, package manager or source tree.                                                                                       |
| dockerfile-lint                | Supply chain and build       | Dockerfiles are linted statically to detect misconfigurations.                                                               | Medium: common misconfigurations are cheap to catch early (not stated upstream).                             | Lint step in CI (for example Hadolint) with a passing result.                                                                                                                 |
| image-immutable-tag            | Supply chain and build       | Images are referenced by immutable identifiers, not mutable tags such as `latest` or `staging`.                              | Medium: a mutable tag can change deployed content silently (not stated upstream).                            | No `:latest` or untagged references in Dockerfiles, Compose files or manifests; digests or versions used.                                                                     |
| image-metadata-labels          | Supply chain and build       | Images carry metadata labels for licence, source, authors and project relation.                                              | Low: traceability, with no direct exploit path (not stated upstream).                                        | `LABEL` instructions present; `docker inspect` shows the labels.                                                                                                              |
| image-no-embedded-secrets      | Supply chain and build       | Images contain no passwords, tokens, keys or connection strings.                                                             | Critical: anyone with image access can read embedded credentials (not stated upstream).                      | Image layers and build arguments hold no secret values; no secret files copied in.                                                                                            |
| image-secret-scan              | Supply chain and build       | Images are scanned for sensitive data before they are pushed to a registry, locally or in CI.                                | High: detects leaks before distribution (not stated upstream).                                               | CI step with a secret scanner (such as Gitleaks or GitGuardian Shield) and zero findings.                                                                                     |
| image-cve-scan                 | Supply chain and build       | Images are scanned for known common vulnerabilities and exposures (CVE).                                                     | High: known vulnerabilities are routinely exploited; the level depends on CVSS scores (not stated upstream). | Scanner report (such as Trivy, Clair, Anchore or Dagda) with a failure threshold configured.                                                                                  |
| image-signing                  | Supply chain and build       | Images are signed and signatures are verified before use.                                                                    | High: unsigned images can be tampered with or substituted (not stated upstream).                             | Signing step in CI; `DOCKER_CONTENT_TRUST=1` or equivalent verification at deploy; failed verification blocks deployment.                                                     |
| container-nonroot-user         | Identity and privileges      | Container processes run as a non-root user with least privilege.                                                             | High: root inside a container eases escape to the host (not stated upstream).                                | `USER` instruction names a non-zero user; `docker inspect --format '{{.Config.User}}' <image>` returns it.                                                                    |
| container-dedicated-uid        | Identity and privileges      | The image has a dedicated user and group with a UID above 10,000, and setuid and setgid bits are removed.                    | Medium: limits privilege inside the image (not stated upstream).                                             | UID in `/etc/passwd` is above 10,000; `find` for files with the setuid or setgid bit returns nothing.                                                                         |
| container-not-privileged       | Identity and privileges      | Containers do not run in privileged mode.                                                                                    | Critical: a privileged container gives root-equivalent control of the host (not stated upstream).            | `HostConfig.Privileged` is `false`; manifests contain no privileged flag.                                                                                                     |
| container-capabilities-minimal | Identity and privileges      | Only the Linux capabilities the workload needs are granted, and CAP_SYS_MODULE, CAP_SYS_TIME and CAP_SYS_PTRACE are dropped. | High: capabilities permit kernel-level actions (not stated upstream).                                        | `CapAdd` and `CapDrop` in `docker inspect`; run commands or manifests drop all and add back only what is needed.                                                              |
| registry-rbac                  | Registry                     | Access to the registry for push and pull is restricted by role-based access control.                                         | High: an open registry allows image replacement (not stated upstream).                                       | Registry policies (IAM, Harbor project roles or equivalent) name roles; no anonymous push.                                                                                    |
| registry-private-network       | Registry                     | The registry is private and sits behind a firewall.                                                                          | Medium: reduces tampering exposure (not stated upstream).                                                    | Registry endpoint is internal; network rules block public access.                                                                                                             |
| runtime-secure-config          | Container runtime and Docker | The container runtime is configured securely, because defaults are not secure.                                               | High: insecure defaults apply to every container (not stated upstream).                                      | Daemon configuration reviewed against a benchmark such as the CIS Docker Benchmark.                                                                                           |
| runtime-api-restricted         | Container runtime and Docker | Access to the runtime daemon and its API is restricted.                                                                      | Critical: API access gives control over all containers and often the host (not stated upstream).             | Socket permissions and listening addresses (for example `ss -ltnp`) show local, restricted access.                                                                            |
| runtime-rootless               | Container runtime and Docker | The runtime runs in rootless mode where the environment supports it.                                                         | High: limits the damage from a daemon compromise (not stated upstream).                                      | `docker info` reports rootless mode; the active context is rootless.                                                                                                          |
| docker-api-port-exposure       | Container runtime and Docker | Docker API ports are not exposed on the network without protection.                                                          | Critical: attackers have used exposed daemon ports to run malware (not stated upstream).                     | `ss -ltnp` shows no listener on 2375 or 2376 that is open to the network.                                                                                                     |
| docker-tls-daemon              | Container runtime and Docker | Remote client-to-daemon traffic uses TLS, and the daemon is never exposed over unencrypted sockets or HTTP.                  | Critical: unauthenticated remote access equals root control (not stated upstream).                           | TLS verification is enabled; no unencrypted `tcp://` endpoint in the daemon configuration.                                                                                    |
| docker-socket-not-mounted      | Container runtime and Docker | The Docker socket is not mounted into containers, particularly in untrusted environments.                                    | Critical: socket access is root-equivalent on the host (not stated upstream).                                | No `docker.sock` volume in run commands, Compose files or manifests.                                                                                                          |
| docker-userns-remap            | Container runtime and Docker | User namespaces are enabled so container root maps to an unprivileged host user.                                             | Medium: limits the effect of container root on the host (not stated upstream).                               | `userns-remap` is set in the daemon configuration; `docker info` shows the setting.                                                                                           |
| security-profiles-enabled      | Container runtime and Docker | Mandatory access control, through SELinux or AppArmor, is enabled.                                                           | High: confines processes beyond discretionary permissions (not stated upstream).                             | `getenforce` returns `Enforcing`, or `aa-status` lists the profiles in use.                                                                                                   |
| seccomp-default-profile        | Container runtime and Docker | The default seccomp profile applies to containers, and seccomp is not set to unconfined.                                     | High: removes system-call filtering (not stated upstream).                                                   | No `seccomp=unconfined` option in run commands or manifests; `SecurityOpt` in `docker inspect` shows no unconfined entry.                                                     |
| host-kernel-patched            | Host infrastructure          | The host kernel is kept patched.                                                                                             | High: the kernel is shared, so a kernel exploit can escape the container (not stated upstream).              | Running kernel version (`uname -r`) matches the distribution's current security update.                                                                                       |
| host-cis-benchmark             | Host infrastructure          | The host operating system is configured against a CIS Benchmark.                                                             | Medium: hardening baseline for the host (not stated upstream).                                               | Benchmark scan report with the score and the failed controls listed.                                                                                                          |
| host-container-optimized-os    | Host infrastructure          | Hosts run an operating system built for containers, such as Flatcar, Bottlerocket, Container-Optimized OS or Fedora CoreOS.  | Low: reduces host footprint (not stated upstream).                                                           | Host image identifier names a container-optimised OS.                                                                                                                         |
| secrets-not-in-env             | Data and secrets             | Sensitive values are not passed as environment variables.                                                                    | High: environment values appear in inspection output, logs and child processes (not stated upstream).        | No keys such as PASSWORD, TOKEN or KEY in `Config.Env` or `env:` entries.                                                                                                     |
| secrets-runtime-injection      | Data and secrets             | Secrets reach the container at run time through volume mounts or a secret store, not from the image.                         | High: baked-in secrets persist in every copy of the image (not stated upstream).                             | Secrets appear as read-only volume mounts or as references to a secret store.                                                                                                 |
| secrets-managed-store          | Data and secrets             | Secrets are created and kept in a managed store, and repositories are guarded against committed secrets.                     | High: unmanaged secrets are hard to revoke and audit (not stated upstream).                                  | Deployment configuration references a store; no plaintext secret files in the repository; pre-commit scanning in place (for example detect-secrets, git-secrets or Gitleaks). |
| secrets-rotation               | Data and secrets             | Secrets are rotated on a defined schedule.                                                                                   | Medium: limits the lifetime of a leaked secret (not stated upstream).                                        | Rotation policy exists; secret ages are within the policy.                                                                                                                    |
| storage-encryption-at-rest     | Data and secrets             | Container storage sits on encrypted filesystems.                                                                             | Medium: protects data on stolen or decommissioned disks (not stated upstream).                               | Disk or volume encryption enabled on the hosts (for example LUKS or encrypted cloud volumes).                                                                                 |
| host-path-restricted           | Data and secrets             | Host paths are not mounted unless required, and write access is granted only where needed.                                   | High: host mounts expose host files to the container (not stated upstream).                                  | No `hostPath` or bind mounts without a clear need; mounts marked read-only where possible.                                                                                    |
| policy-enforcement-opa         | Data and secrets             | A policy engine such as OPA enforces read-only root filesystems, allowed host paths and allowed volume drivers.              | Medium: makes the other controls enforceable at deploy time (not stated upstream).                           | Policy files exist and are enforced; a non-compliant test deployment is rejected.                                                                                             |
| rbac-least-privilege           | Data and secrets             | Humans and applications receive only the secrets and permissions they need.                                                  | High: excess permissions turn any compromise into a wider one (not stated upstream).                         | Role bindings and service accounts list no wildcard or unused grants.                                                                                                         |
| audit-trail-central            | Data and secrets             | Audits run regularly, and security events are collected in a central audit trail that supports forensics.                    | Medium: needed to detect and investigate incidents (not stated upstream).                                    | Log forwarding to a central store is configured; audit schedule and retention are recorded.                                                                                   |
| resource-limits                | Workloads                    | CPU and memory limits are set for each container.                                                                            | Medium: limits the impact of a compromised, resource-hungry container (not stated upstream).                 | `HostConfig` shows memory and CPU limits, or manifests define them.                                                                                                           |
| pids-limit                     | Workloads                    | The number of processes in a container is capped.                                                                            | Medium: prevents fork bombs from exhausting the host (not stated upstream).                                  | `PidsLimit` in `docker inspect` is set to a positive value.                                                                                                                   |
| network-segregation            | Workloads                    | Containers use custom networks, connect only where needed, and sensitive containers stay off public networks.                | High: limits lateral movement after a compromise (not stated upstream).                                      | Network membership lists show no sensitive container on a public network or the default bridge.                                                                               |
| rootfs-read-only               | Workloads                    | The root filesystem and volumes are read-only where the workload allows.                                                     | Medium: prevents malware persistence and configuration tampering (not stated upstream).                      | `ReadonlyRootfs` is `true` in `docker inspect`; `--read-only` set in run commands or manifests.                                                                               |
| syscall-restriction            | Workloads                    | System calls available to containers are restricted across the lifecycle, including storage-related calls and capabilities.  | High: narrows the kernel attack surface (not stated upstream).                                               | A custom seccomp profile is applied and its content is reviewed.                                                                                                              |
| runtime-monitoring             | Workloads                    | Container activity is monitored and events are analysed for suspicious patterns.                                             | High: detects indicators of compromise and zero-day activity (not stated upstream).                          | A monitoring agent runs on every host; alert rules exist and alerts are reviewed.                                                                                             |
| incident-response              | Workloads                    | A response process for container incidents exists and is exercised.                                                          | Medium: speeds containment after an attack (not stated upstream).                                            | Written runbook present; date of the last exercise recorded.                                                                                                                  |
| automated-patching             | Workloads                    | Images are rebuilt and hosts are patched automatically to pick up fixes.                                                     | High: unpatched components are a common entry point (not stated upstream).                                   | Scheduled rebuild pipeline and patch logs; running image age within policy.                                                                                                   |
| drift-prevention               | Workloads                    | Running containers stay immutable, and changes made after start are prevented or detected.                                   | Medium: keeps the running state equal to the reviewed image (not stated upstream).                           | `docker diff <container>` shows no changes; drift alerts configured.                                                                                                          |

Upstream states no severity for any check. Every severity in the table is assigned by
this reference and marked as not stated upstream. The scale matches the severity
vocabulary of `three-perspective-audit-checklist.md`.

## Supply chain and build

Images inherit the trust of their sources, so the build stage determines whether the
code, base images and contents can be trusted before any run-time control applies.

### Static analysis of application code and dependencies

Check ID: `sca-static-analysis`

Check:

- Confirm that a static analysis step runs on the application code and its libraries in
  CI.
- Review the latest results for unresolved findings in code and dependencies.

Fix:

- Add a SAST or software composition analysis tool, such as one of the open-source tools
  listed by OWASP.
- Fail the build when new high-severity findings appear.

### Trusted base image

Check ID: `image-trusted-base`

Check:

- Inspect each `FROM` instruction and confirm that it names an official or verified
  publisher.
- Confirm that no image comes from an unknown public namespace.

Fix:

- Replace unknown base images with official ones and record the chosen tag.

### Minimal base image

Check ID: `image-minimal-base`

Check:

- Confirm that the final stage uses Alpine, scratch or a distroless image.
- Compare the package inventory of the image against the application's needs.

Fix:

- Switch to a minimal base and install only the packages the application requires.

### Small single-process images

Check ID: `image-small-single-process`

Check:

- Confirm that each image runs one application process.
- Review image size and the number of layers.

Fix:

- Split multi-purpose images into one image per application and merge redundant layers.

### Multi-stage build

Check ID: `image-multistage-build`

Check:

- Confirm that the Dockerfile separates build and runtime stages.
- Confirm that the final stage contains no compiler, package manager, source tree or
  intermediate file.

Fix:

- Move the build into an earlier stage and copy only the resulting binaries and runtime
  dependencies.

### Dockerfile linting

Check ID: `dockerfile-lint`

Check:

- Confirm that a linter such as Hadolint runs on every Dockerfile in CI.
- Confirm that the latest run passed; upstream also names Trivy for misconfiguration
  checks.

Fix:

- Add the linter to the pipeline and fix or justify each finding.

### Immutable image references

Check ID: `image-immutable-tag`

Check:

- Search Dockerfiles, Compose files and manifests for `:latest`, `staging` or untagged
  references.
- Confirm that references use a semantic version, commit identifier or SHA-256 digest.

Fix:

- Pin images by digest, for example `alpine@sha256:<digest>`, and tag releases with
  semantic versions.

### Image metadata labels

Check ID: `image-metadata-labels`

Check:

- Confirm that the Dockerfile sets labels for licence, source, authors and project or
  component.
- Confirm the labels appear in `docker inspect`.

Fix:

- Add `LABEL` instructions for each field in the Dockerfile.

### No embedded secrets in images

Check ID: `image-no-embedded-secrets`

Check:

- Review image layers and build arguments for passwords, tokens, keys and connection
  strings.
- Confirm that `docker history` shows no secret values and that no secret file is copied
  into the image.

Fix:

- Remove the secret from the build, rotate it, and inject it at run time instead.

### Secret scan before push

Check ID: `image-secret-scan`

Check:

- Confirm that a secret scanner runs on image contents before each push, locally or in
  CI.
- Confirm that the latest scan reported no findings.

Fix:

- Add a scanner such as Gitleaks or GitGuardian Shield to the push step and block the
  push on findings.

### Common vulnerability scan

Check ID: `image-cve-scan`

Check:

- Confirm that a CVE scanner, such as Trivy, Clair, Anchore or Dagda, runs on each
  image.
- Confirm that the scanner has a failure threshold and that the latest report is within
  it.

Fix:

- Add the scanner to the pipeline with a severity threshold, and rebuild images with
  fixed packages.

### Image signing

Check ID: `image-signing`

Check:

- Confirm that the pipeline signs each image, for example with Docker Content Trust (TUF
  through Notary) or Sigstore Cosign.
- Confirm that deployment verifies signatures and rejects unsigned or altered images.

Fix:

- Enable `DOCKER_CONTENT_TRUST=1` or add signature verification to the deployment step.

## Identity and privileges

A process that runs as root with broad capabilities inside a container is much closer to
root on the host, so identity and privilege settings are checked separately from the
image contents.

### Non-root container user

Check ID: `container-nonroot-user`

Check:

- Inspect the `USER` instruction in the Dockerfile and the image configuration with
  `docker inspect --format '{{.Config.User}}' <image>`.
- Confirm that the value is a non-zero user and that run commands do not override it
  with root.

Fix:

- Add a `USER` instruction that names the dedicated user created in the image.
- Set the equivalent non-root option in the orchestrator manifest.

### Dedicated user and no setuid or setgid files

Check ID: `container-dedicated-uid`

Check:

- Confirm in `/etc/passwd` that the application user has a UID above 10,000 and a
  dedicated group.
- Run `find` on the image filesystem for files with the setuid or setgid bit and confirm
  that none are returned.

Fix:

- Create the user with a fixed UID above 10,000 and remove the setuid and setgid bits
  from the image.

### Privileged containers

Check ID: `container-not-privileged`

Check:

- Run `docker inspect --format '{{.HostConfig.Privileged}}' <container_id>` and confirm
  that the output is `false`.
- Search Compose files and manifests for privileged settings.

Fix:

- Remove the privileged setting and grant only the specific capabilities the workload
  needs.

### Minimal Linux capabilities

Check ID: `container-capabilities-minimal`

Check:

- Inspect `CapAdd` and `CapDrop` in `docker inspect` and confirm that only required
  capabilities are added.
- Confirm that CAP_SYS_MODULE, CAP_SYS_TIME and CAP_SYS_PTRACE are not granted.

Fix:

- Drop all capabilities (`--cap-drop ALL`) and add back only the required ones with
  `--cap-add`.

## Registry

The registry is a trust boundary: upstream notes that an image pulled from a registry is
not guaranteed to be trusted, because it may contain vulnerabilities or have been
replaced by an attacker.

### Registry access control

Check ID: `registry-rbac`

Check:

- Review who can push and who can pull, using the registry's policy or role
  configuration.
- Confirm that anonymous push is disabled and that roles follow role-based access
  control.

Fix:

- Define roles per team, remove broad or anonymous access, and audit the role list
  regularly.

### Private registry behind a firewall

Check ID: `registry-private-network`

Check:

- Confirm that the registry endpoint is internal and not reachable from the public
  internet.
- Confirm that network rules restrict access to the registry to the build and deployment
  systems.

Fix:

- Place the registry on a private network segment and expose it only to the required
  systems.

## Container runtime and Docker

Upstream notes that runtime security supports detection of indicators of compromise,
zero-day attacks and compliance requirements, and that the runtime's default
configuration is not secure. Upstream also reports attacks against unsecured Docker
daemons, mainly cryptojacking worms.

### Secure runtime configuration

Check ID: `runtime-secure-config`

Check:

- Review the daemon configuration file and runtime settings against the CIS Docker
  Benchmark; upstream names docker-bench-security for this.
- Record any exception and its justification.

Fix:

- Apply the secure settings and restart the daemon in a maintenance window.

### Restricted runtime API access

Check ID: `runtime-api-restricted`

Check:

- Inspect the daemon socket permissions and listening addresses (for example with
  `ss -ltnp`).
- Confirm that only the intended users or groups can reach the API.

Fix:

- Restrict socket group membership and remove listeners that are not required.

### Rootless runtime mode

Check ID: `runtime-rootless`

Check:

- Run `docker info` and confirm that rootless mode is reported.
- Confirm that the active context is rootless.

Fix:

- Run the daemon in rootless mode with `docker context use rootless` where the
  environment supports it.

### Exposed Docker API ports

Check ID: `docker-api-port-exposure`

Check:

- Confirm with `ss -ltnp` that no daemon port is open to the network without protection.
- Confirm that the daemon configuration does not expose a TCP listener without TLS.

Fix:

- Remove the network listener, or enable TLS as described in the TLS check.

### TLS between client and daemon

Check ID: `docker-tls-daemon`

Check:

- Confirm that TLS verification is enabled for remote clients.
- Confirm that the daemon configuration has no unencrypted `tcp://` endpoint.

Fix:

- Enable TLS with client certificates for remote access; use the Unix socket for local
  access only.

### Docker socket mounts

Check ID: `docker-socket-not-mounted`

Check:

- Search run commands, Compose files and manifests for `docker.sock`.
- Confirm that any such mount is absent from untrusted workloads.

Fix:

- Remove the mount; upstream states that a socket owner has root-equivalent access to
  the host.

### User namespaces

Check ID: `docker-userns-remap`

Check:

- Confirm that `userns-remap` is set in the daemon configuration.
- Confirm with `docker info` that the setting is active.

Fix:

- Enable user namespace remapping and recreate the containers.

### SELinux or AppArmor enabled

Check ID: `security-profiles-enabled`

Check:

- Run `getenforce` on SELinux hosts and confirm that the result is `Enforcing`.
- Run `aa-status` on AppArmor hosts and confirm that the profiles are loaded.

Fix:

- Enable the mandatory access control in use and apply a profile to each container;
  seccomp is covered by its own check.

### Default seccomp profile

Check ID: `seccomp-default-profile`

Check:

- Search run commands and manifests for `seccomp=unconfined`.
- Confirm that `SecurityOpt` in `docker inspect` contains no unconfined entry.

Fix:

- Remove the unconfined setting so that the default profile applies.

## Host infrastructure

Upstream states that a compromised host compromises its containers, and that the kernel
is shared between the container and the host.

### Patched host kernel

Check ID: `host-kernel-patched`

Check:

- Compare the running kernel from `uname -r` with the distribution's current security
  updates.
- Confirm that the host receives kernel updates through an automated process.

Fix:

- Apply the kernel update and reboot the host within the patch window.

### CIS Benchmark for the host operating system

Check ID: `host-cis-benchmark`

Check:

- Confirm that a CIS Benchmark scan of the host has been run and that its report is
  recent.
- Review the failed controls and their remediation status.

Fix:

- Remediate failed controls and rerun the scan.

### Container-optimised host operating system

Check ID: `host-container-optimized-os`

Check:

- Confirm the host image identifier names an operating system built for containers.

Fix:

- Use an operating system such as Flatcar, Bottlerocket, Container-Optimized OS or
  Fedora CoreOS for container hosts.

## Data and secrets

Upstream defines secrets broadly: passwords, API keys and tokens, SSH keys, private
certificates, encryption keys, connection strings and sensitive configuration settings.
Each check below applies to all of them.

### Secrets not passed as environment variables

Check ID: `secrets-not-in-env`

Check:

- Search `Config.Env` in `docker inspect` output and `env` entries in manifests for keys
  such as PASSWORD, TOKEN or KEY.
- Confirm that no sensitive value appears there.

Fix:

- Replace environment values with file-based secrets mounted at run time.

### Secrets injected at run time

Check ID: `secrets-runtime-injection`

Check:

- Confirm that secrets are supplied as read-only volume mounts or as references to a
  secret store.
- Confirm that the image itself contains no secret.

Fix:

- Mount each secret as a read-only file and remove any baked-in copy.

### Managed secret store

Check ID: `secrets-managed-store`

Check:

- Confirm that secrets are created and stored in a managed store, such as AWS Secrets
  Manager, Azure Key Vault, Google Secret Manager, HashiCorp Vault or CyberArk Conjur.
- Confirm that the repository has no plaintext secret files and that a scanner such as
  detect-secrets, git-secrets or Gitleaks runs before commits.

Fix:

- Move stored secrets into the managed store and add a pre-commit scanner.

### Secret rotation

Check ID: `secrets-rotation`

Check:

- Confirm that a rotation policy exists for each secret type.
- Compare the age of each secret with the policy.

Fix:

- Define the rotation schedule and automate rotation where the store supports it.

### Encrypted container storage

Check ID: `storage-encryption-at-rest`

Check:

- Confirm that the disks or volumes that hold container storage are encrypted.

Fix:

- Enable disk or volume encryption on the hosts (for example LUKS or encrypted cloud
  volumes).

### Host path mounts

Check ID: `host-path-restricted`

Check:

- Search run commands and manifests for `hostPath` and bind mounts.
- Confirm that each host mount is needed and that write access is granted only to
  containers that must modify the path.

Fix:

- Remove unneeded mounts and mark the remaining ones read-only where possible.

### Policy enforcement

Check ID: `policy-enforcement-opa`

Check:

- Confirm that policies (for example written in OPA) enforce read-only root filesystems,
  allowed host paths and allowed volume drivers.
- Confirm that a non-compliant test deployment is rejected.

Fix:

- Write the missing policies and enforce them in the deployment pipeline.

### Least privilege and RBAC

Check ID: `rbac-least-privilege`

Check:

- Review role bindings and service accounts for wildcard or unused grants.
- Confirm that each human or application holds only the secrets it needs.

Fix:

- Narrow each role to the required permissions and remove unused accounts.

### Central audit trail

Check ID: `audit-trail-central`

Check:

- Confirm that security events are forwarded to a central audit store.
- Confirm that audits are scheduled and their results and retention are recorded.

Fix:

- Configure log forwarding, set a retention period and schedule regular audits.

## Workloads

Upstream explains that a container is protected like any other Linux process, and that
the operating system should protect the host kernel from container escapes and prevent
containers from influencing each other.

### Resource limits

Check ID: `workload-resource-limits`

Check:

- Confirm that memory and CPU limits appear in `docker inspect` (`HostConfig`) or in
  manifests.

Fix:

- Set limits with options such as `--memory` and `--cpus` (or `--cpu-shares`) for each
  container.

### Process limit

Check ID: `workload-pids-limit`

Check:

- Confirm that `PidsLimit` in `docker inspect` is set to a positive value.

Fix:

- Run containers with `--pids-limit`; upstream uses 200 as an example.

### Network segregation

Check ID: `workload-network-segregation`

Check:

- List container networks and confirm that sensitive containers are not attached to the
  default bridge or to a public-facing network.
- Confirm that containers can reach each other only where required.

Fix:

- Create custom bridge, overlay or macvlan networks per trust zone and attach containers
  to them.

### Read-only root filesystem

Check ID: `rootfs-read-only`

Check:

- Confirm that `ReadonlyRootfs` is `true` in `docker inspect` for each workload that
  allows it.
- Confirm that volumes are read-only where they do not need writes.

Fix:

- Run with `--read-only` and provide writable paths only where the application requires
  them.

### System-call restriction

Check ID: `syscall-restriction`

Check:

- Confirm that a custom seccomp profile applies to each workload, covering the whole
  lifecycle and storage-related system calls.
- Review the profile to confirm that unneeded calls are blocked.

Fix:

- Generate a profile from the workload's observed calls and apply it with
  `--security-opt seccomp=<file>`.

### Runtime monitoring

Check ID: `runtime-monitoring`

Check:

- Confirm that a monitoring agent runs on each host and that events are analysed for
  suspicious patterns.
- Confirm that alert rules exist and that alerts are reviewed.

Fix:

- Deploy a runtime detection tool. Upstream suggests choosing it by event context,
  safety, low overhead and wide kernel support.

### Incident response process

Check ID: `incident-response`

Check:

- Confirm that a written response process for container incidents exists.
- Confirm that the process has been exercised and the date recorded.

Fix:

- Write the runbook and run a tabletop exercise.

### Automated patching

Check ID: `automated-patching`

Check:

- Confirm that images are rebuilt on a schedule and hosts are patched automatically.
- Compare the age of running images with the patch policy.

Fix:

- Schedule rebuilds and host patching, and record the results.

### Drift prevention

Check ID: `drift-prevention`

Check:

- Run `docker diff <container>` on running containers and confirm that no changes
  appear.
- Confirm that drift is detected or prevented through read-only settings or monitoring.

Fix:

- Replace changed containers with new ones from the reviewed image instead of modifying
  them.
