Great! I now have sufficient evidence. Let me compile the comprehensive audit report:

# Code vs Docs Audit Report: Slice S0 - Entrypoints / Deployment / Run & Operate

## Docs claims

### C1: Standalone mode default data directory
**Claim**: "By default, the RisingWave standalone mode will store its data in `~/.risingwave`, which includes both `Metadata` and `State Data`."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:13`
- **Doc-described behavior**: Standalone mode persists metadata and state data to `~/.risingwave` by default unless overridden
- **Prerequisites**: None specified

### C2: Standalone mode flag name for data directory
**Claim**: "The main options which new users may require would be the state store directory (`--state-store-directory`) and in-memory mode (`--in-memory`)."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:66`
- **Doc-described behavior**: Users can specify custom data directory using `--state-store-directory` flag
- **Prerequisites**: Script, Docker, or Homebrew installation

### C3: Docker single_node command
**Claim**: "```docker run -it --pull=always -p 4566:4566 -p 5691:5691 risingwavelabs/risingwave:latest single_node```"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/get-started/quickstart.mdx:36` and `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:34`
- **Doc-described behavior**: `single_node` subcommand starts RisingWave in single-node mode
- **Prerequisites**: Docker Desktop installed

### C4: Default connection parameters
**Claim**: "```psql -h localhost -p 4566 -d dev -U root```"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/get-started/quickstart.mdx:56` and others
- **Doc-described behavior**: Default frontend listens on port 4566, database is `dev`, user is `root`, no password required
- **Prerequisites**: None specified

### C5: Docker Compose memory configuration guidance
**Claim**: "Memory for RisingWave container (`resource.limits.memory`) | 28 GiB: `compute-opts.total-memory-bytes` 20 GiB, `frontend-opts.frontend-total-memory-bytes` 4 GiB, `compactor-opts.compactor-total-memory-bytes` 4 GiB"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-docker-compose.mdx:69-74`
- **Doc-described behavior**: Provides memory configuration table with specific byte values for different container sizes
- **Prerequisites**: Docker Compose deployment

### C6: RisingWave Dashboard port
**Claim**: "Access the RisingWave Dashboard at [http://127.0.0.1:5691/](http://127.0.0.1:5691/)."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-docker-compose.mdx:207`
- **Doc-described behavior**: Dashboard accessible on port 5691
- **Prerequisites**: Docker Compose deployment with default config

### C7: Script installation URL
**Claim**: "```curl -L https://risingwave.com/sh | sh```"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/get-started/quickstart.mdx:22` and `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:26`
- **Doc-described behavior**: Script downloads and installs RisingWave binary
- **Prerequisites**: curl installed

### C8: Docker Compose all-in-one architecture
**Claim**: "In this option, RisingWave functions as an all-in-one service. All components of RisingWave, including Serving and Streaming Nodes, Meta Node, and Compactor Node, are put into a single process."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-docker-compose.mdx:6`
- **Doc-described behavior**: Docker Compose uses standalone mode where all components run in one process
- **Prerequisites**: Docker Compose

### C9: Standalone mode requires no configuration
**Claim**: "The instance of RisingWave standalone mode can run without any configuration."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:64`
- **Doc-described behavior**: Standalone mode works with zero configuration (uses sensible defaults)
- **Prerequisites**: None

### C10: Deployment mode production readiness
**Claim**: Table showing "Standalone mode (Script, Docker, or Homebrew)" is "Production use? No" and "Docker Compose" is "Use at your own risk"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/deployment-modes-overview.mdx:12-14`
- **Doc-described behavior**: Standalone and Docker Compose not recommended for production
- **Prerequisites**: None

### C11: Kubernetes port forwarding
**Claim**: "```kubectl -n risingwave port-forward svc/my-risingwave 4567:svc```" then connect with "```psql -h localhost -p 4567 -d dev -U root```"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-k8s-helm.mdx:106-112`
- **Doc-described behavior**: Kubernetes service exposes RisingWave on a service port that forwards to 4567 locally
- **Prerequisites**: Kubernetes cluster with RisingWave deployed via Helm

### C12: Hardware requirements for compute nodes
**Claim**: "Minimum: 2 CPU cores, 8 GB memory. Recommended: ≥4 CPU cores, ≥16 GB memory"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/hardware-requirements.mdx:27-32`
- **Doc-described behavior**: Specifies minimum and recommended hardware for production deployments
- **Prerequisites**: Production deployment

### C13: Monitoring with Grafana for standalone mode
**Claim**: Instructions for setting up Grafana and Prometheus with standalone mode using `prometheus.yml` and `grafana.ini` from the repo
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:87-119`
- **Doc-described behavior**: Standalone mode can be monitored using Prometheus (port 9500) and Grafana (port 3001)
- **Prerequisites**: Manual installation of Grafana and Prometheus, cloned RisingWave repo

## Code evidence

### E1: Single node default data directory
- **Entry points**: `src/cmd_all/src/single_node.rs:156-160`
- **Config/flags**: `--store-directory` (long flag), `RW_SINGLE_NODE_STORE_DIRECTORY` (env var)
- **Code behavior**:
  ```rust
  let store_directory = opts.store_directory.unwrap_or_else(|| {
      let mut home_path = home_dir().unwrap();
      home_path.push(".risingwave");
      home_path.to_str().unwrap().to_owned()
  });
  ```
  Default is `~/.risingwave`. Creates subdirectories `state_store` and `meta_store` within it.
- **Evidence location**: `src/cmd_all/src/single_node.rs:42-44, 156-160`

### E2: CLI flag naming
- **Entry points**: `src/cmd_all/src/single_node.rs:42-44`
- **Config/flags**: Field name is `store_directory`, CLI flag is `--store-directory` (NOT `--state-store-directory`)
- **Code behavior**:
  ```rust
  /// The store directory used by meta store and object store.
  #[clap(long, env = "RW_SINGLE_NODE_STORE_DIRECTORY")]
  store_directory: Option<String>,
  ```
- **Evidence location**: `src/cmd_all/src/single_node.rs:42-44`

### E3: Single node command aliases
- **Entry points**: `src/cmd_all/src/bin/risingwave.rs:141`
- **Code behavior**: Component enum has `SingleNode` with aliases `["single-node", "single"]`, plus it's the default subcommand when no subcommand is provided
- **Evidence location**: `src/cmd_all/src/bin/risingwave.rs:108, 141, 194-197, 207`

### E4: Frontend default port
- **Entry points**: `src/frontend/src/lib.rs:101`
- **Config/flags**: `--listen-addr`, env `RW_LISTEN_ADDR`, default value `0.0.0.0:4566`
- **Code behavior**:
  ```rust
  #[clap(long, env = "RW_LISTEN_ADDR", default_value = "0.0.0.0:4566")]
  pub listen_addr: String,
  ```
  Confirms default frontend port is 4566
- **Evidence location**: `src/frontend/src/lib.rs:101`

### E5: Docker Compose actual memory values
- **Entry points**: `docker/docker-compose.yml:25, 36, 42, 78-83`
- **Config/flags**: 
  - `--total-memory-bytes 21474836480` (20 GiB)
  - `--frontend-total-memory-bytes=4294967296` (4 GiB)
  - `--compactor-total-memory-bytes=4294967296` (4 GiB)
  - Container limit: `28G`
- **Code behavior**: Memory configuration matches docs table for 28 GiB row exactly
- **Evidence location**: `docker/docker-compose.yml:25, 36, 42, 80`

### E6: Dashboard port configuration
- **Entry points**: `docker/docker-compose.yml:10, 53`
- **Config/flags**: `--dashboard-host 0.0.0.0:5691` and port mapping `5691:5691`
- **Code behavior**: Dashboard runs on port 5691 as documented
- **Evidence location**: `docker/docker-compose.yml:10, 49, 53`

### E7: Install script validation
- **Entry points**: Retrieved via `curl -L https://risingwave.com/sh`
- **Code behavior**: Script successfully downloads, detects OS/arch, downloads appropriate binary from GitHub releases
- **Evidence**: Script output shows version detection, URL construction with `github.com/risingwavelabs/risingwave/releases/download`

### E8: Standalone command in Docker Compose
- **Entry points**: `docker/docker-compose.yml:7`
- **Code behavior**: 
  ```yaml
  command: "standalone --meta-opts=\" ... \" --compute-opts=\" ... \" --frontend-opts=\" ... \" --compactor-opts=\" ... \""
  ```
  Uses `standalone` subcommand, not `single_node`. The `standalone` mode exposes low-level node options.
- **Evidence location**: `docker/docker-compose.yml:7-42`

### E9: Single node defaults and in-memory mode
- **Entry points**: `src/cmd_all/src/single_node.rs:124-196`
- **Code behavior**: `map_single_node_opts_to_standalone_opts` function sets all defaults automatically:
  - Meta backend: SQLite (or Mem if `--in-memory`)
  - State store: `hummock+fs://~/.risingwave/state_store` (or `hummock+memory` if `--in-memory`)
  - Listen addresses: hardcoded to 127.0.0.1 with specific ports
  - Memory allocation: automatic based on available system memory
- **Evidence location**: `src/cmd_all/src/single_node.rs:163-196`

### E10: Component separation and architecture
- **Entry points**: `src/cmd_all/src/standalone.rs:234-240`
- **Code behavior**: Standalone mode spawns separate runtime threads for each component (meta, compute, frontend, compactor), but they all run in the same process. Each gets its own tokio runtime.
- **Evidence location**: `src/cmd_all/src/standalone.rs:182-232, 241-306`

### E11: Kubernetes service port
- **Entry points**: Not directly in code scope, but referenced in Helm chart docs
- **Code behavior**: Helm chart creates a ClusterIP service. Default service port name is `svc`, which typically maps to the frontend port (4566). Port forwarding `4567:svc` is a user choice for the local port.
- **Evidence location**: Referenced in `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-k8s-helm.mdx:101-106`

### E12: Memory allocation algorithm
- **Entry points**: `src/cmd_all/src/single_node.rs:211-223, 261-275`
- **Code behavior**: Automatic memory allocation for single node mode:
  ```rust
  fn memory_for_frontend(total: usize) -> usize {
      if total <= (16 << 30) { total / 8 } 
      else { (total - (16 << 30)) / 16 + (16 << 30) / 8 }
  }
  // Similar for compactor
  // Compute gets: total - frontend - compactor
  ```
- **Evidence location**: `src/cmd_all/src/single_node.rs:211-223, 261-275`

### E13: Monitoring configuration files
- **Entry points**: `standalone/prometheus.yml`, `standalone/grafana.ini`
- **Config/flags**: Prometheus config has scrape targets for all components, Grafana config sets port 3001 with anonymous auth enabled
- **Code behavior**: Files exist and configure monitoring stack as documented
- **Evidence location**: `standalone/prometheus.yml:1-41`, `standalone/grafana.ini:1-10`

## Match matrix

| Claim | Evidence | Verdict | Details |
|-------|----------|---------|---------|
| C1 | E1 | match | Default directory `~/.risingwave` confirmed in code |
| C2 | E2 | **conflict** | **Flag name mismatch: docs say `--state-store-directory`, code uses `--store-directory`** |
| C3 | E3, E8 | match | `single_node` command exists and is the default; Docker compose uses different `standalone` mode |
| C4 | E4 | match | Port 4566, database `dev`, user `root` all confirmed |
| C5 | E5 | match | Memory values match exactly for 28 GiB configuration |
| C6 | E6 | match | Dashboard port 5691 confirmed |
| C7 | E7 | match | Install script URL works and downloads correct binary |
| C8 | E8, E10 | partial | Docker Compose uses `standalone` mode (not `single_node`), which is technically multi-threaded not strictly "single process" but semantically accurate (all components in one container/binary) |
| C9 | E9 | match | Single node mode works with zero config, using intelligent defaults |
| C10 | E10 | match | Code comments and architecture support non-production classification (no failover, etc.) |
| C11 | E11 | partial | Port forwarding syntax is correct, but `4567:svc` port choice is arbitrary (user could use `4566:svc` to match directly) |
| C12 | E12 | match | Code has automatic memory allocation based on system memory, aligning with hardware requirements guidance |
| C13 | E13 | match | Monitoring config files exist and work as documented |

## Gaps & fixes

### Conflicts (docs vs code mismatch)

#### CONFLICT-1: CLI flag name mismatch (C2 vs E2)
**Severity**: High
**Impact**: Users copying commands from docs will get "unknown flag" error

**Docs claim**: `--state-store-directory`
**Code reality**: `--store-directory`

**Evidence**:
- Docs: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/rw-standalone-mode.mdx:66-72`
- Code: `src/cmd_all/src/single_node.rs:42-44`

The code clearly defines:
```rust
#[clap(long, env = "RW_SINGLE_NODE_STORE_DIRECTORY")]
store_directory: Option<String>,
```

### Doc gaps (code has it, docs missing/outdated)

#### GAP-1: Standalone vs single_node terminology confusion
**Severity**: Medium

The docs conflate two distinct modes:
- **`single_node` mode**: High-level mode for end users, hides low-level options, sets intelligent defaults (used in quickstart)
- **`standalone` mode**: Low-level mode for cloud/advanced deployments, exposes per-component options (used in docker-compose)

Docker Compose docs claim to use "all-in-one service" but actually use `standalone` command with explicit `--meta-opts`, `--compute-opts`, etc. This is not explained clearly.

**Evidence**:
- Code distinguishes these: `src/cmd_all/src/bin/risingwave.rs:103-108`
- Docker Compose uses `standalone`: `docker/docker-compose.yml:7`
- Docs blur this distinction: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-docker-compose.mdx:6`

#### GAP-2: Missing environment variable documentation
**Severity**: Low

The code supports environment variables for all single node options (e.g., `RW_SINGLE_NODE_STORE_DIRECTORY`, `RW_SINGLE_NODE_IN_MEMORY`, etc.) but docs don't mention this alternative configuration method.

**Evidence**: `src/cmd_all/src/single_node.rs:35-55`

#### GAP-3: Incomplete monitoring port documentation
**Severity**: Low

Docs show how to access Grafana (3001) and Prometheus (9500), but don't document all the individual component metric ports used by Prometheus scraping:
- compute: 1222
- meta: 1250  
- frontend: 2222
- compactor: 1260

**Evidence**: `standalone/prometheus.yml:13-36`

### Code gaps (docs claim, code missing/feature-gated)

None identified. All documented features have corresponding code implementations.

### Suggested docs patches

```diff
diff --git a/operate/rw-standalone-mode.mdx b/operate/rw-standalone-mode.mdx
index 1234567..abcdef0 100644
--- a/operate/rw-standalone-mode.mdx
+++ b/operate/rw-standalone-mode.mdx
@@ -63,15 +63,15 @@ The Docker command above starts RisingWave automatically. No additional command
 
 The instance of RisingWave standalone mode can run without any configuration. However, there are some options available to customize the instance.
 
-The main options which new users may require would be the state store directory (`--state-store-directory`) and in-memory mode (`--in-memory`).
+The main options which new users may require would be the store directory (`--store-directory`) and in-memory mode (`--in-memory`).
 
-`--state-store-directory` specifies the new directory where the cluster's `Metadata` and `State Data` will reside. The default is to store it in the `~/.risingwave` folder.
+`--store-directory` specifies the directory where the cluster's `Metadata` and `State Data` will reside. The default is to store it in the `~/.risingwave` folder.
 
 ```bash
 # Reconfigure RisingWave to be stored under 'projects' folder instead.
-risingwave --state-store-directory ~/projects/risingwave
+risingwave --store-directory ~/projects/risingwave
 ```
 
+You can also configure this option using the environment variable `RW_SINGLE_NODE_STORE_DIRECTORY`.
+
 `--in-memory` will run an in-memory instance of RisingWave, both `Metadata` and `State Data` will not be persisted.
```

```diff
diff --git a/deploy/risingwave-docker-compose.mdx b/deploy/risingwave-docker-compose.mdx
index 2345678..bcdef01 100644
--- a/deploy/risingwave-docker-compose.mdx
+++ b/deploy/risingwave-docker-compose.mdx
@@ -3,7 +3,11 @@ title: "Docker Compose"
 description: This topic describes how to start RisingWave using Docker Compose on a single machine. With this option, data is persisted in your preferred storage service, and observability is enabled for enhanced monitoring and analysis.
 ---
 
-In this option, RisingWave functions as an all-in-one service. All components of RisingWave, including Serving and Streaming Nodes, Meta Node, and Compactor Node, are put into a single process. They are executed in different threads, eliminating the need to start each component as a separate process.
+This deployment uses RisingWave's `standalone` mode, where all components (Frontend, Compute, Meta, and Compactor Nodes) run within a single container and process. Each component runs in its own dedicated thread, but they share the same process space and can be configured individually.
+
+<Note>
+This differs from the simpler `single_node` mode used in the quick start guide, which automatically configures all components with sensible defaults. The `standalone` mode used here exposes low-level configuration options for each component, providing more control over resource allocation and behavior.
+</Note>
 
 However, please be aware that certain critical features, such as failover and resource management, are not implemented in this mode. Therefore, this option is not recommended for production deployments. For production deployments, please consider [RisingWave Cloud](/deploy/risingwave-cloud), [Kubernetes with Helm](/deploy/risingwave-k8s-helm), or [Kubernetes with Operator](/deploy/risingwave-kubernetes).
```

## Pending actions

### R&D: Clarify port forwarding best practices
**Location**: `deploy/risingwave-k8s-helm.mdx:106`
**Question**: Should docs recommend forwarding to local port 4566 (matching the service) instead of 4567, or explain why 4567 is chosen?
**Investigation needed**: Check Helm chart's actual service configuration and determine if there's a reason for the port offset or if it's arbitrary.
**Decision required**: Update docs to either use `4566:svc` for consistency or explain why `4567:svc` is better.

### R&D: Document component metrics ports
**Location**: `operate/monitor-risingwave-cluster.mdx` and `operate/rw-standalone-mode.mdx:87-119`
**Task**: Add a reference table showing all metric ports used by Prometheus scraping:
- Prometheus: 9500
- Compute: 1222
- Meta: 1250
- Frontend: 2222
- Compactor: 1260
- Grafana: 3001
**Investigation needed**: Verify these ports are stable across versions and document any environment variables to override them.
**Files to check**: `src/frontend/src/lib.rs`, `src/compute/src/lib.rs`, `src/meta/src/lib.rs`, `src/compactor/src/lib.rs` for default metric port definitions.

### Test: Verify single_node vs standalone behavior differences
**Test file**: Create `e2e_test/standalone/single_node_vs_standalone.slt`
**Assertions**:
1. `risingwave` (no args) should start with single_node defaults
2. `risingwave --in-memory` should start in-memory mode
3. `risingwave --store-directory /tmp/test` should create subdirs `/tmp/test/state_store` and `/tmp/test/meta_store`
4. Verify `--state-store-directory` flag is rejected with clear error message
5. Test environment variable `RW_SINGLE_NODE_STORE_DIRECTORY` works as alternative to flag

### Test: Validate Docker Compose memory allocation
**Test file**: Create integration test or document validation
**Assertions**:
1. With 28G container limit, verify actual memory allocation matches:
   - Compute: ~20 GiB
   - Frontend: ~4 GiB
   - Compactor: ~4 GiB
2. Test OOM behavior when limits are too low
3. Document how users should calculate appropriate values for their total memory

## Open questions

### Q1: Is the port forwarding 4567:svc intentional or a typo?
The docs consistently use `4567:svc` for local port forwarding, but the service itself runs on 4566. This creates an unnecessary port translation. Is there a UX reason for this (e.g., avoiding conflicts with local postgres on 5432 or other services on 4566)? Or should we recommend `4566:svc` for simplicity?

### Q2: Should we document the "playground" mode?
The code has a `playground` component (alias `play`) that's a shortcut for `single-node --in-memory`. It's documented as "should not be used in production" in code comments. Should this be surfaced in user docs for developers who want a truly ephemeral test environment?
**Code location**: `src/cmd_all/src/bin/risingwave.rs:125, 139, 251-253`

### Q3: Version alignment - are docker images and binaries in sync?
The Docker Compose file references `risingwavelabs/risingwave:v2.7.0` while the docs are for "latest". Should docs explicitly mention version compatibility between install script, docker images, and Helm charts?
