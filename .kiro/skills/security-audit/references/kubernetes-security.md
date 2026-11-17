# Kubernetes Security

This file is the reference that the security-audit skill loads when the audit target
includes Kubernetes manifests, cluster configuration, or Helm charts. It supplies the
checks for perspective C (configuration and dependencies) and is derived from the
upstream guide `kubernetes-security-best-practice` (Apache-2.0, commit
e5b7187e8cf8c7eb69bd375919f0cb85354f0b94; see
`licenses/kubernetes-security-best-practice-LICENSE`). The upstream covers host and
network exposure, the API server, admission control, the kubelet, default service
accounts, network policies, the Kubernetes Dashboard, and image pulls. It contains no
material on etcd, secrets encryption, audit logging, Helm charts, or Pod Security
Admission, so this file defines no checks for those areas. Its examples target kops
1.8.1 and Kubernetes releases around 1.8 to 1.10, as inferred from the text. Deprecated
and removed mechanisms were excluded, and the excluded material is not restated here.
Provider-specific checks for AWS and kops are in `kubernetes-cloud-notes.md`.

## Checklist index

| Check ID                                | Topic                     | Check statement                                                                                                                                          | Severity guidance                                                                                              | Audit evidence                                                                                                                                                                             |
| --------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| host-os-hardened                        | Host and network exposure | The operating system of every master and node is hardened against an OS-level guide before Kubernetes is configured.                                     | High: the upstream rates this item as high.                                                                    | No manifest evidence; a documented hardening baseline or benchmark result per host image. Fail when no baseline is evidenced.                                                              |
| node-os-updates-applied                 | Host and network exposure | Node operating system packages are patched, and machine images are replaced after updates rather than kept as created.                                   | High: the upstream rates this item as high.                                                                    | Node image identifier in the cluster or instance configuration, and the patch level of the hosts. Fail when the image has not been replaced after an update cycle.                         |
| private-topology                        | Host and network exposure | Masters and nodes use private addresses only, with outbound access through a NAT gateway and only required ports forwarded.                              | Low: the upstream rates this item as low.                                                                      | Node and master network configuration. Fail when any master or node has a public address.                                                                                                  |
| ports-firewalled                        | Host and network exposure | Kubelet, kube-proxy, network-provider, and API ports are bound to a specific interface where possible, and firewalled from untrusted networks otherwise. | High: the upstream rates this item as high, and it names the port list.                                        | Security-group or firewall rules and listen-address settings for ports 4149, 10250, 10255, 10256, 9099, and 6443. Fail on ingress from 0.0.0.0/0 or equivalent to any of these ports.      |
| bastion-ssh-only                        | Host and network exposure | Nodes and masters accept SSH only from a bastion host, and bastion access is hardened and recorded.                                                      | Medium: the upstream rates this item as medium.                                                                | Ingress rules on port 22 for node and master groups. Fail when port 22 is open to the public on any non-bastion instance.                                                                  |
| cis-benchmark-scan                      | Host and network exposure | kube-bench is run against the CIS Kubernetes Benchmark on masters and nodes as a first hardening step.                                                   | High: the upstream rates this item as high.                                                                    | kube-bench output per master and node. Fail when no run is recorded or FAIL results remain unresolved without justification.                                                               |
| apiserver-authorization-rbac            | API server                | kube-apiserver authorizes requests with RBAC, not AlwaysAllow.                                                                                           | Critical: AlwaysAllow grants any authenticated entity full access; the upstream rates this item as critical.   | The `--authorization-mode` flag on each kube-apiserver process. Pass when the value includes RBAC and excludes AlwaysAllow. Fail when it is AlwaysAllow or not set.                        |
| apiserver-anonymous-auth-disabled       | API server                | Anonymous requests to kube-apiserver are rejected.                                                                                                       | Critical: the upstream rates this item as critical.                                                            | The `--anonymous-auth` flag on each kube-apiserver process. Pass when it is false. Fail when it is true or not set.                                                                        |
| apiserver-unauthenticated-port-disabled | API server                | The API server serves no unauthenticated, unencrypted port on any network interface.                                                                     | Critical: the upstream rates this item as critical.                                                            | Listen addresses of kube-apiserver and firewall rules for the API port. Pass when no such port is reachable from any network. Fail when a port without TLS or authentication is reachable. |
| apiserver-profiling-disabled            | API server                | The profiling endpoint is disabled with `--profiling=false`.                                                                                             | Medium: the upstream rates this item as medium; it gives information disclosure and denial-of-service reasons. | The `--profiling` flag on each kube-apiserver process. Fail when it is true or not set.                                                                                                    |
| admission-always-pull-images            | Admission control         | The AlwaysPullImages admission plugin is enabled, so every new Pod pulls its image with the Pod's credentials.                                           | Medium: the upstream rates this item as medium.                                                                | The admission plugin list passed to kube-apiserver. Fail when AlwaysPullImages is absent.                                                                                                  |
| kubelet-anonymous-auth-disabled         | Kubelet                   | Anonymous requests to the kubelet API are rejected.                                                                                                      | Critical: the upstream rates this item as critical.                                                            | The kubelet `--anonymous-auth` setting on each node. Pass when false. Fail when true or not set.                                                                                           |
| kubelet-authorization-webhook           | Kubelet                   | Kubelet API requests are authorized through the API server by webhook.                                                                                   | Critical: the upstream rates this item as critical; the kubelet API can bypass the Kubernetes API.             | The kubelet `--authorization-mode` setting on each node. Pass when Webhook. Fail when AlwaysAllow or not set.                                                                              |
| default-sa-automount-disabled           | Service accounts          | The token of the default service account is not auto-mounted into Pods in namespaces that do not need API access.                                        | Critical without RBAC, Low with RBAC: the upstream rates the item by authorization mode.                       | `automountServiceAccountToken` on the default ServiceAccount in each namespace, and on Pod specs. Fail when the default ServiceAccount does not set it to false.                           |
| network-policies-enforced               | Network policies          | NetworkPolicy objects restrict pod-to-pod and external traffic, and the network provider enforces them.                                                  | Medium: the upstream rates this item as medium.                                                                | NetworkPolicy objects per namespace, and the network provider in use. Fail when workload namespaces have no policy or the provider does not support policies.                              |
| dashboard-no-cluster-admin-binding      | Dashboard                 | No ClusterRoleBinding grants cluster-admin to the dashboard service account, so the sign-in Skip action cannot grant full access.                        | Critical: the upstream rates this item as critical.                                                            | `kubectl -n kube-system get clusterrolebinding kubernetes-dashboard -o yaml`, and a search for cluster-admin bindings. Fail when any binding to cluster-admin remains for the dashboard.   |
| dashboard-not-public                    | Dashboard                 | The dashboard is not exposed to the public Internet.                                                                                                     | Critical: the upstream rates the Dashboard section as critical.                                                | Service types and Ingress rules for the dashboard. Fail on a LoadBalancer, NodePort, or public Ingress. Access through kubectl proxy is not exposure.                                      |
| dashboard-ingress-network-policy        | Dashboard                 | A NetworkPolicy denies ingress to dashboard Pods from other Pods in the cluster.                                                                         | Critical: inherits the upstream Dashboard section rating; the policy itself is a supplementary control.        | A NetworkPolicy in kube-system selecting the dashboard label with an Ingress policy type and no allow rules, on a provider that enforces policies. Fail when absent or not enforced.       |
| image-pull-policy-enforced              | Image pull and provenance | Image pulls are restricted by an allow or deny policy, enforced either by a Docker image policy plugin or by an ImagePolicyWebhook admission controller. | High: the upstream rates this item as high.                                                                    | Docker daemon plugin configuration, or the kube-apiserver admission configuration that enables ImagePolicyWebhook. Fail when neither mechanism is present.                                 |

## Host and network exposure

The upstream treats the host as the foundation of cluster security. It recommends
private topologies, firewalled ports, bastion-only SSH, and a CIS benchmark scan as the
first step before Kubernetes-specific settings.

### Host operating system hardening

Check:

- The node operating system is hardened following a recognised guide before Kubernetes
  is installed.
- The upstream cites a Linux security guide as the starting point and does not prescribe
  a specific benchmark.

Fix:

- Apply an OS hardening baseline to every master and node image, and retain the
  evidence.

### Node operating system updates

Check:

- Node packages are patched, and the machine image is updated when a new patch set is
  available, rather than kept as originally created.
- The upstream notes that AMIs should be considered outdated once created, including
  official ones.

Fix:

- Update the image identifier in the cluster configuration and recreate the nodes so
  they boot from the updated image.
- Check and patch the running hosts from the bastion host, as the upstream describes,
  where the image cannot be replaced immediately.

### Private topology

Check:

- Masters and nodes have private addresses only, and outbound access uses a NAT gateway.
- Exposure is limited to the ports that must be reachable from outside the private
  network.

Fix:

- Place the cluster in a private subnet or VPC, and forward only the required ports from
  the NAT gateway.

### Firewalled ports

Check:

- Kubelet ports 4149 (cAdvisor metrics), 10250 (full node API), and 10255
  (unauthenticated read-only API) are not reachable from untrusted networks.
- The kube-proxy and Calico health-check ports (10256, 9099) and the API port (6443) are
  held to the same exposure discipline; the upstream treats an exposed health-check port
  as a denial-of-service risk to the network provider.

Fix:

- Bind each listener to loopback or a specific interface where the component allows it.
- Where binding is not possible, block the port in the firewall or security group.

### SSH access through a bastion host

Check:

- Only the bastion host accepts SSH from outside; other nodes and masters do not accept
  public SSH.
- Bastion access is subject to hardened SSH configuration and, where possible, session
  recording.

Fix:

- Create a dedicated bastion host, and restrict port 22 on other instances to the
  bastion's address.
- Apply OpenSSH hardening guidance and enable session recording on the bastion.

### CIS benchmark scan with kube-bench

Check:

- kube-bench has been run against masters and nodes using the CIS Kubernetes Benchmark,
  and its results are on record.
- The upstream presents this as the first step before any Kubernetes-specific review.

Fix:

- Run kube-bench on each master and node, and resolve or justify each FAIL result.

## API server

The upstream lists the API server flags that must be set, and rates each by its
exposure. The flags are checked on each kube-apiserver process.

### Authorization mode

Check:

- The `--authorization-mode` flag includes RBAC and does not use AlwaysAllow.
- The upstream notes that kops defaults to AlwaysAllow, which grants any authenticated
  entity full cluster access.

Fix:

- Set `--authorization-mode` to a value that includes RBAC, for example `Node,RBAC`
  where node authorization is also required.
- Review existing bindings after the change, because RBAC denies requests that
  AlwaysAllow used to permit.

### Anonymous authentication

Check:

- The `--anonymous-auth` flag is false on kube-apiserver.
- The upstream states that this setting does not govern the kubelet API, which is
  covered separately.

Fix:

- Set `--anonymous-auth=false` on every kube-apiserver process and restart the
  component.

### Unauthenticated API port

Check:

- The API server serves no port without TLS, authentication, or authorization; the
  upstream describes such a port as an API with no TLS, no authentication, and no
  authorization.
- The check is verified from the listen addresses and by a network probe of the API port
  from outside the control plane.

Fix:

- Configure kube-apiserver to listen only on its secure port. Where a health check or
  bootstrapping step prevents this, block the port in the firewall from all networks.

### Profiling endpoint

Check:

- The profiling endpoint is disabled, because it can expose system detail and consume
  resources enough to cause denial of service.

Fix:

- Set `--profiling=false` on each kube-apiserver process.

## Admission control

The upstream names the admission plugins that kube-apiserver must enable.

### AlwaysPullImages

Check:

- The AlwaysPullImages plugin is enabled, so the image pull policy of every new Pod is
  forced to Always.
- Without it, a locally cached image can be reused by a Pod that holds no pull
  credentials.

Fix:

- Add AlwaysPullImages to the admission plugin list of kube-apiserver.

## Kubelet

The kubelet exposes its own API for running commands on a node. The upstream states that
this API can bypass the Kubernetes API, so kubelet settings are checked separately from
the API server.

### Kubelet anonymous authentication

Check:

- The kubelet `--anonymous-auth` setting is false on every node.

Fix:

- Set `--anonymous-auth=false` in the kubelet configuration of every node and restart
  the kubelet.

### Kubelet authorization mode

Check:

- The kubelet `--authorization-mode` setting is Webhook, so the API server authorizes
  each kubelet request.

Fix:

- Set `--authorization-mode=Webhook` in the kubelet configuration and restart the
  kubelet.

## Service accounts

The upstream explains that the admission controller assigns the default service account
to every Pod and mounts its token unless auto-mounting is disabled. The upstream rates
the item by whether RBAC is enabled.

### Auto-mounting of the default service account token

Check:

- The default ServiceAccount in each namespace sets `automountServiceAccountToken` to
  false, unless the namespace's Pods need Kubernetes API access.
- The upstream rates this item Low with RBAC enabled and Critical without it.

Fix:

- Patch the default ServiceAccount in each namespace to disable auto-mounting. The
  upstream command,
  `kubectl patch serviceaccount default -p "automountServiceAccountToken: false"`, does
  not appear to be valid JSON for `-p`, so the corrected command must be verified before
  use.
- Repeat the change for each new namespace, because the admission controller creates the
  default ServiceAccount there.

## Network policies

The upstream describes NetworkPolicy as the firewall of the cluster and states that Pods
can communicate without restriction unless policies are defined.

### NetworkPolicy enforcement

Check:

- Each workload namespace has NetworkPolicy objects that restrict internal and external
  traffic.
- The network provider supports NetworkPolicy; the upstream recommends switching
  provider if it does not.

Fix:

- Define NetworkPolicy objects for each namespace, starting from the upstream's
  referenced recipes.
- Select a network provider that supports the policy API.

## Dashboard

The upstream states that before Kubernetes 1.8.0 the dashboard was granted full cluster
access by default. The first check applies to clusters that may have been upgraded from
older installations, and the other two apply to any dashboard deployment.

### No cluster-admin binding for the dashboard

Check:

- No ClusterRoleBinding to cluster-admin remains for the kubernetes-dashboard
  ServiceAccount, because the Skip action on the sign-in page would otherwise grant full
  access.

Fix:

- Remove any leftover binding to cluster-admin, and confirm the result with the upstream
  command.

### Dashboard not publicly exposed

Check:

- The dashboard has no public Service or Ingress; the upstream cites a cryptojacking
  incident as the reason.
- Access through kubectl proxy is not treated as exposure by the upstream.

Fix:

- Do not expose the dashboard through a public Service or Ingress; the upstream's access
  route is kubectl proxy.

### Network policy for the dashboard

Check:

- A NetworkPolicy in kube-system selects the dashboard Pods and denies ingress from
  other Pods.
- The upstream notes that this policy does not block requests through kubectl proxy.

Fix:

- Apply the deny-dashboard NetworkPolicy from the upstream, on a network provider that
  enforces policies.

## Image pull and provenance

The upstream treats the image pull as the entry point for untrusted content, and notes
that any user with access to the Docker socket or the Kubernetes API can pull any image.
The upstream does not cover image signing or provenance attestation.

### Restricted image pulls

Check:

- Image pulls are restricted by an allow or deny policy, enforced at the Docker daemon
  by a plugin or at the API server by ImagePolicyWebhook.
- The upstream cites a Docker image policy plugin; its maintenance status is not stated
  upstream and must be verified before adoption.

Fix:

- Install an image policy plugin on the Docker daemon, or configure ImagePolicyWebhook
  with a policy service.
- Restrict access to the Docker socket and to the Kubernetes API, since the upstream
  notes that either permits pulling any image.
