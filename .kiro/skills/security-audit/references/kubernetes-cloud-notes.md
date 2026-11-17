# Kubernetes Cloud and Distribution Notes

This file holds the installer-specific material from the upstream guide
`kubernetes-security-best-practice`, which is summarised in `kubernetes-security.md`. It
covers kops (the installer guide, which targets AWS). The upstream also mentions GKE
(beta) and vSphere (alpha) as kops providers, but it gives no checks for them, so none
are defined here. The checks below are supplementary to the general checks: general
checks are referred to by Check ID and are not repeated. Each check carries a Check ID
line, followed by Check and Fix bullets in the same format as the general file.

## AWS-specific material removed as legacy

The upstream AWS guide and its manifests for a legacy metadata proxy were removed from
this reference, because that proxy is legacy and its manifests are no longer served. No
AWS-specific check is defined in this file. The general checks in
`kubernetes-security.md` apply to AWS-hosted clusters.

## kops

The general checks that have kops evidence locations are apiserver-authorization-rbac
(the authorization setting, which kops defaults to AlwaysAllow), private-topology (the
topology setting), bastion-ssh-only (the bastion instance group),
node-os-updates-applied (the image setting), network-policies-enforced (the networking
setting), and the admission checks (the admission list). Observation: the upstream
examples are pinned to kops 1.8.1.

### Networking provider supports network policies

Check ID: `kops-networking-supports-policies`

Check:

- The networking setting names a provider that enforces NetworkPolicy. The upstream
  selects canal, because kubenet cannot be used in a private topology and the upstream
  wants network policy support. Severity: Medium, as the upstream rates its Use Network
  Policies topic.
- Fail when the setting is kubenet or a provider without NetworkPolicy support.

Fix:

- Set the networking provider to canal, or another provider that enforces NetworkPolicy,
  when creating or editing the cluster.

### Admission plugin list

Check ID: `kops-admission-list-complete`

Check:

- The `kubeAPIServer.admissionControl` list includes AlwaysPullImages. Severity: Medium,
  inherited from the general check admission-always-pull-images.
- Audit evidence: the cluster specification, compared with the plugins that the
  Kubernetes release in use supports.

Fix:

- Add the missing plugin to the cluster specification and apply it with
  `kops update cluster`, as the upstream deployment step shows.

### Unauthenticated port with health checks

Check ID: `kops-unauthenticated-port-firewalled`

Check:

- With kops 1.8.1, the insecure port cannot be closed because of the API health check,
  which the upstream cites as issue 43784. In that case the port must not be reachable
  from any network, and the API load balancer must target the secure port. Severity:
  Critical, as the upstream rates its Insecure Port topic, consistent with the general
  check apiserver-unauthenticated-port-disabled.
- Fail when the insecure port is reachable from any network.

Fix:

- Close the port on the API server when the kops release supports it; otherwise block
  the port in the security group.

### Profiling endpoint in kops

Check ID: `kops-profiling-flag-set`

Check:

- Profiling is disabled on kube-apiserver, although kops 1.8.1 could not set the flag
  through the kubeAPIServer section, which the upstream cites as issue 4688. Severity:
  Medium, as the upstream rates its Disable Profiling topic.
- Fail when the profiling flag is enabled on any master.

Fix:

- Set `--profiling=false` on each master by a mechanism other than the kubeAPIServer
  section. The upstream names no workaround, so the mechanism must be verified against
  the kops release in use.

### API endpoint topology

Check ID: `kops-api-endpoint-private`

Check:

- When public access to the Kubernetes API is not needed, the API load balancer is
  internal, following the upstream reference to the kops topology guide. Severity: Low,
  as the upstream rates its Private topology topic.
- Audit evidence: the API load balancer type in the cluster specification; the field
  name is not stated upstream and must be verified against the kops documentation.

Fix:

- Change the API topology as the kops topology guide describes, after confirming that
  VPN or equivalent access is available, because the upstream warns that the API becomes
  unreachable otherwise.

### Private DNS zone

Check ID: `kops-dns-zone-private`

Check:

- The Route53 zone managed by kops is private when the cluster does not need public name
  resolution. The upstream states that the zone is public by default so that bastion
  records resolve publicly. Severity: Low, as the upstream rates its Private topology
  topic.
- Fail when the zone is public for a cluster that does not require public resolution.

Fix:

- Pass `--dns private` when creating the cluster, or edit the cluster to set a private
  zone, after confirming that resolution works through VPN access.
