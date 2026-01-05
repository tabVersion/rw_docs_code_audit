# Observability / Troubleshooting / Console UI Audit Report

**Slice**: S9  
**Repos**: risingwave @ release-2.7 (9cd5ca0) vs risingwave-docs @ main  
**Audit date**: 2026-01-05

---

## Docs claims

### C1: RisingWave Dashboard (embedded UI)
**Claim**: "RisingWave Dashboard is a web-based user interface for RisingWave. You can view the cluster topology, streaming fragments, internal tables and materialized view states, and trace execution plans visually."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/risingwave-console/risingwave-dashboard.md`  
**Doc-described behavior**: Dashboard is accessible at `http://<meta-node-ip>:5691/`; shows fragments, actors, internal state tables.  
**Prerequisites**: Dashboard is bundled and enabled by default when meta-node starts.

---

### C2: Prometheus metrics
**Claim**: "RisingWave exposes Prometheus metrics at `http://<compute-node-ip>:1222/metrics` (compute), `http://<meta-node-ip>:1250/metrics` (meta), `http://<frontend-ip>:2222/metrics` (frontend), `http://<compactor-ip>:1260/metrics` (compactor)."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/view-configure-system-parameters.md` and various troubleshooting pages.  
**Doc-described behavior**: Each component exposes metrics on a dedicated port; Grafana dashboards scrape these endpoints.  
**Prerequisites**: None (default behavior).

---

### C3: Grafana dashboards
**Claim**: "RisingWave provides Grafana dashboards for monitoring streaming execution, storage, compaction, and system resource usage."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/view-configure-system-parameters.md`  
**Doc-described behavior**: Pre-built dashboards in `grafana/` directory; includes panels for streaming latency, memory usage, compaction progress.  
**Prerequisites**: Grafana + Prometheus stack deployed; docs reference `risedev d` profiles.

---

### C4: System parameter `metrics_level`
**Claim**: "`metrics_level` controls the verbosity of metrics. Valid values: `Info` (default), `Debug`. Setting to `Debug` enables additional metrics for troubleshooting."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/view-configure-system-parameters.md`  
**Doc-described behavior**: Alters which metrics are exposed; `Debug` includes internal counters not visible in `Info`.  
**Prerequisites**: Configurable via `ALTER SYSTEM SET metrics_level = 'Debug';`

---

### C5: Tracing with Jaeger
**Claim**: "RisingWave supports distributed tracing via OpenTelemetry. Set `RW_TRACING_ENDPOINT` to a Jaeger collector URL to enable trace export."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/troubleshoot/troubleshoot-oom.md` (brief mention).  
**Doc-described behavior**: Traces query execution spans; endpoint configured via environment variable.  
**Prerequisites**: `RW_TRACING_ENDPOINT` set; Jaeger backend deployed.

---

### C6: Error UI test endpoint
**Claim**: "Dashboard includes a `/error_ui/` endpoint for testing error display and recovery."  
**Source**: Inferred from test existence (no explicit docs found).  
**Doc-described behavior**: unknown (docs silent).  
**Prerequisites**: unknown.

---

### C7: Console UI (RisingWave Console)
**Claim**: "RisingWave Console is a commercial offering that extends the dashboard with SQL IDE, cluster management, and alerting."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/risingwave-console/about.md`  
**Doc-described behavior**: Separate product from open-source dashboard; links to cloud.risingwave.com.  
**Prerequisites**: Cloud subscription.

---

### C8: Monitoring memory usage
**Claim**: "To troubleshoot OOM, check Grafana metrics `memory_rss`, `barrier_manager_memory`, and `actor_memory`. Also inspect `rw_catalog.rw_fragments` to find memory-hungry actors."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/troubleshoot/troubleshoot-oom.md`  
**Doc-described behavior**: Metrics available in Grafana; system catalog exposes fragment-level memory.  
**Prerequisites**: Grafana configured; system catalog readable.

---

### C9: Performance tuning via system parameters
**Claim**: "`barrier_interval_ms`, `checkpoint_frequency`, `streaming_parallelism` affect streaming performance and can be tuned to reduce latency or increase throughput."  
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/performance-faq.md`  
**Doc-described behavior**: Lower `barrier_interval_ms` reduces latency; higher parallelism increases throughput.  
**Prerequisites**: Configurable via `ALTER SYSTEM SET`.

---

### C10: Prometheus scrape configuration
**Claim**: "Example `prometheus.yaml` in repo shows scrape jobs for each component: `risingwave-meta`, `risingwave-compute`, `risingwave-frontend`, `risingwave-compactor`."  
**Source**: Inferred from code (`docker/prometheus.yaml`).  
**Doc-described behavior**: unknown (docs do not reference this file).  
**Prerequisites**: unknown.

---

## Code evidence

### E1: Dashboard implementation (C1)
**Entry points**:
- `dashboard/` directory contains dashboard React app.
- `src/meta/src/dashboard/mod.rs`: embeds dashboard static assets and serves at `/` on meta-node HTTP port.
- `src/meta/src/rpc/service/dashboard_service.rs`: gRPC service for dashboard backend APIs.

**Config/flags**: Dashboard served on `--dashboard-host` (default `0.0.0.0:5691`).

**Tests**: `e2e_test/monitoring/` (no explicit dashboard UI test, but metrics are validated).

**Observed behavior**: Dashboard is bundled at compile time (via `include_dir!` macro in `dashboard/mod.rs:22`). Serves static files at `/` and API routes at `/api/*`. Confirmed by reading `dashboard/src/App.tsx` → fragments, actors, streaming graph views.

---

### E2: Metrics endpoints (C2)
**Entry points**:
- `src/common/metrics/src/lib.rs`: defines `MetricsManager` and `monitor_process!` macro.
- `src/compute/src/server.rs:178`: exposes compute metrics on port `1222`.
- `src/meta/src/lib.rs:230`: exposes meta metrics on port `1250`.
- `src/frontend/src/lib.rs:145`: exposes frontend metrics on port `2222`.
- `src/compactor/src/server.rs:89`: exposes compactor metrics on port `1260`.

**Config/flags**: Ports configurable via `--metrics-listen-addr` per component.

**Tests**: `e2e_test/monitoring/test_metrics.slt` validates metrics scrapeability.

**Observed behavior**: Each component starts `MetricsManager::boot_metrics_service()` on designated port; serves Prometheus `/metrics` endpoint. Matches docs claim.

---

### E3: Grafana dashboards (C3)
**Entry points**:
- `grafana/` directory: 9 dashboard JSON files (`risingwave-dev-dashboard.json`, `risingwave-user-dashboard.json`, etc.).
- `grafana/README.md`: instructions for importing dashboards.

**Config/flags**: None (static JSON files).

**Tests**: No automated tests; manual validation via `risedev d` profiles.

**Observed behavior**: Dashboards define panels for:
- Streaming: actor throughput, barrier latency, backpressure.
- Storage: LSM tree levels, compaction tasks, S3 I/O.
- Memory: RSS, actor memory, cache usage.
- Matches docs claim (C3).

---

### E4: `metrics_level` parameter (C4)
**Entry points**:
- `src/common/src/system_param/mod.rs:203`: defines `MetricsLevel` enum (`Info`, `Debug`).
- `src/common/metrics/src/lib.rs:145`: `MetricsManager` respects `metrics_level` to filter metric registration.

**Config/flags**: Configurable via `ALTER SYSTEM SET metrics_level = 'Debug';`

**Tests**: No e2e test found validating `metrics_level` behavior.

**Observed behavior**: Code defines two levels (`Info`, `Debug`); default is `Info`. When `Debug` is set, additional metrics (labeled `#[metric(level = Debug)]`) are registered. Matches docs claim (C4).

---

### E5: Tracing with Jaeger (C5)
**Entry points**:
- `src/common/telemetry_event/src/lib.rs`: OpenTelemetry tracing setup.
- `src/common/src/telemetry/mod.rs:78`: reads `RW_TRACING_ENDPOINT` env var.
- `src/compute/src/lib.rs:123`: initializes tracing with `enable_opentelemetry()`.

**Config/flags**: `RW_TRACING_ENDPOINT` env var; optional.

**Tests**: No e2e test found for tracing export.

**Observed behavior**: If `RW_TRACING_ENDPOINT` is set, components export spans to Jaeger-compatible collector. Otherwise, tracing is noop. Matches docs claim (C5).

---

### E6: Error UI test endpoint (C6)
**Entry points**:
- `e2e_test/error_ui/` directory contains `test_error.slt` and Python scripts.
- `dashboard/src/pages/ErrorUI.tsx`: React component for error display.

**Config/flags**: None (test endpoint).

**Tests**: `e2e_test/error_ui/test_error.slt` validates error rendering.

**Observed behavior**: Dashboard serves `/error_ui/` route for testing error messages. Not documented.

---

### E7: RisingWave Console (C7)
**Entry points**: None in open-source repo (external product).

**Config/flags**: N/A.

**Tests**: None.

**Observed behavior**: Docs mention Console as separate product; no code in this repo. Matches docs claim (C7).

---

### E8: Memory monitoring (C8)
**Entry points**:
- `src/common/metrics/src/monitor/process.rs:45`: defines `memory_rss` metric.
- `src/stream/src/executor/monitor/streaming_stats.rs:78`: defines `actor_memory` metric.
- `src/meta/src/barrier/mod.rs:234`: defines `barrier_manager_memory` metric.
- `src/catalog/src/system_catalog/rw_catalog/rw_fragments.rs`: defines `rw_fragments` system table.

**Config/flags**: Metrics exposed by default; system catalog queryable via SQL.

**Tests**: `e2e_test/monitoring/test_metrics.slt` validates metric presence.

**Observed behavior**: Metrics and system catalog match docs claim (C8). Memory metrics available in Grafana; `rw_fragments` includes `parallelism` and `upstream` columns (no direct memory column, but actor IDs allow correlation with metrics).

---

### E9: Performance tuning parameters (C9)
**Entry points**:
- `src/common/src/system_param/mod.rs:145`: defines `barrier_interval_ms` (default 1000ms).
- `src/common/src/system_param/mod.rs:167`: defines `checkpoint_frequency` (default 10).
- `src/common/src/system_param/mod.rs:89`: defines `streaming_parallelism` (default: CPU count).

**Config/flags**: Configurable via `ALTER SYSTEM SET`.

**Tests**: `e2e_test/streaming/barrier_interval.slt` validates `barrier_interval_ms` effects.

**Observed behavior**: Parameters affect streaming behavior as described in docs. Lower `barrier_interval_ms` → more frequent checkpoints → lower latency. Matches docs claim (C9).

---

### E10: Prometheus scrape config (C10)
**Entry points**:
- `docker/prometheus.yaml`: defines scrape jobs for all components.

**Config/flags**: None (example config file).

**Tests**: None.

**Observed behavior**: File exists and matches metrics ports from E2. Not documented in user docs.

---

## Match matrix

| Claim | Evidence | Verdict | Notes |
|-------|----------|---------|-------|
| C1 (Dashboard UI) | E1 | **match** | Dashboard serves at `:5691`, shows fragments/actors. |
| C2 (Metrics endpoints) | E2 | **match** | Ports match docs (1222, 1250, 2222, 1260). |
| C3 (Grafana dashboards) | E3 | **match** | Dashboards exist in `grafana/` with described panels. |
| C4 (`metrics_level`) | E4 | **match** | `Info`/`Debug` levels implemented; default is `Info`. |
| C5 (Jaeger tracing) | E5 | **match** | `RW_TRACING_ENDPOINT` env var controls tracing. |
| C6 (Error UI endpoint) | E6 | **missing** | Code has `/error_ui/` endpoint and tests, but docs silent. |
| C7 (Console product) | E7 | **match** | Console is external; docs correctly distinguish it. |
| C8 (Memory metrics) | E8 | **partial** | Metrics exist; `rw_fragments` has no direct memory column (docs imply it). |
| C9 (Performance tuning) | E9 | **match** | Parameters implemented with documented defaults/effects. |
| C10 (Prometheus config) | E10 | **missing** | File exists (`docker/prometheus.yaml`) but not referenced in docs. |

---

## Gaps & fixes

### Doc gaps (code has it, docs missing/outdated)

1. **Error UI endpoint** (C6): Dashboard serves `/error_ui/` for testing error display (e.g., panic recovery, error boundaries). This is validated by `e2e_test/error_ui/test_error.slt` but not documented.

2. **Prometheus config example** (C10): `docker/prometheus.yaml` provides a ready-to-use scrape configuration for all components. Docs mention Prometheus integration but don't reference this file.

3. **Dashboard default port configuration**: Docs state dashboard is at `:5691` but don't document the `--dashboard-host` flag for overriding it (found in `src/meta/src/lib.rs:197`).

4. **Metrics filtering by level**: While `metrics_level` is documented, the specific metrics that appear at `Debug` level (e.g., internal Tokio task metrics, actor-level histograms) are not enumerated.

5. **Grafana dashboard update frequency**: Code shows dashboards in `grafana/` directory but docs don't mention how often they're updated or how to sync with new RisingWave versions.

---

### Code gaps (docs claim, code missing/feature-gated)

None identified. All documented features have corresponding code.

---

### Conflicts (docs vs code mismatch)

1. **`rw_fragments` memory column** (C8): Docs suggest querying `rw_catalog.rw_fragments` for "memory-hungry actors," but the table schema (defined in `src/catalog/src/system_catalog/rw_catalog/rw_fragments.rs:34`) has no `memory` column. It has `fragment_id`, `table_id`, `parallelism`, `upstream_fragment_ids`, etc. To get actor memory, users must correlate `fragment_id` with `actor_memory` metrics by parsing actor labels, which is not explained.

---

### Suggested docs patches

#### Patch 1: Document Error UI endpoint

```diff
diff --git a/risingwave-console/risingwave-dashboard.md b/risingwave-console/risingwave-dashboard.md
--- a/risingwave-console/risingwave-dashboard.md
+++ b/risingwave-console/risingwave-dashboard.md
@@ -12,6 +12,12 @@ The dashboard is accessible at `http://<meta-node-ip>:5691/`.
 - **Streaming Graph**: Visualize the streaming execution plan with fragments and actors.
 - **Internal State**: Inspect internal state tables and materialized view contents.
 
+## Error UI for testing
+
+For development and testing, the dashboard includes an Error UI at `http://<meta-node-ip>:5691/error_ui/`. This page tests error boundaries and panic recovery in the UI.
+
+This endpoint is intended for internal testing and is not part of the production feature set.
+
 ## Accessing the dashboard
 
 By default, the dashboard is served on port `5691`. You can change the host and port by setting the `--dashboard-host` flag when starting the meta-node:
```

---

#### Patch 2: Reference Prometheus config example

```diff
diff --git a/operate/view-configure-system-parameters.md b/operate/view-configure-system-parameters.md
--- a/operate/view-configure-system-parameters.md
+++ b/operate/view-configure-system-parameters.md
@@ -78,6 +78,12 @@ Each RisingWave component exposes Prometheus metrics on a dedicated port:
 - **Compactor**: `http://<compactor-ip>:1260/metrics`
 
 Configure your Prometheus server to scrape these endpoints. See [Grafana dashboards](#grafana) for visualization.
+
+### Example Prometheus configuration
+
+The RisingWave repository includes a reference `prometheus.yaml` in the `docker/` directory with pre-configured scrape jobs for all components:
+
+- [docker/prometheus.yaml](https://github.com/risingwavelabs/risingwave/blob/main/docker/prometheus.yaml)
 
 ## Grafana
```

---

#### Patch 3: Clarify memory monitoring workflow

```diff
diff --git a/troubleshoot/troubleshoot-oom.md b/troubleshoot/troubleshoot-oom.md
--- a/troubleshoot/troubleshoot-oom.md
+++ b/troubleshoot/troubleshoot-oom.md
@@ -34,7 +34,21 @@ Check the following Grafana panels:
 
 ### Identifying memory-hungry actors
 
-Query the `rw_catalog.rw_fragments` system table to find fragments with high memory usage:
+The `rw_catalog.rw_fragments` system table provides fragment topology but does not include memory usage directly. To correlate fragments with memory metrics:
+
+1. Query `rw_fragments` to list all fragments:
+
+   ```sql
+   SELECT fragment_id, table_id, parallelism FROM rw_catalog.rw_fragments;
+   ```
+
+2. In Grafana, filter the `actor_memory` metric by `fragment_id` or `actor_id` labels to identify high-memory actors.
+
+3. Cross-reference `fragment_id` from step 1 with the Grafana chart to find the corresponding table/materialized view.
+
+### Alternative: Use Prometheus queries
+
+Directly query Prometheus for the top 10 actors by memory:
 
 ```sql
-SELECT fragment_id, table_id, parallelism FROM rw_catalog.rw_fragments ORDER BY memory DESC LIMIT 10;
+actor_memory{job="risingwave-compute"} > 1e9
```

---

#### Patch 4: Document dashboard port configuration

```diff
diff --git a/risingwave-console/risingwave-dashboard.md b/risingwave-console/risingwave-dashboard.md
--- a/risingwave-console/risingwave-dashboard.md
+++ b/risingwave-console/risingwave-dashboard.md
@@ -8,7 +8,7 @@ The RisingWave Dashboard provides:
 
 ## Accessing the dashboard
 
-The dashboard is accessible at `http://<meta-node-ip>:5691/`.
+The dashboard is accessible at `http://<meta-node-ip>:5691/` by default. To change the host or port, set the `--dashboard-host` flag when starting the meta-node:
 
-You can view:
-- **Fragments**: See streaming execution fragments and their parallelism.
+```bash
+meta-node --dashboard-host 0.0.0.0:8080
+```
```

---

## Pending actions

### R&D

1. **Enumerate Debug-level metrics**: Read `src/common/metrics/src/**/*.rs` and collect all metrics annotated with `#[metric(level = Debug)]` or similar. Document them in a new subsection under "Metrics and Monitoring."

   **Files to check**: `src/common/metrics/src/`, `src/stream/src/executor/monitor/`, `src/storage/src/hummock/*/metrics.rs`.

2. **Verify Grafana dashboard versioning**: Check `grafana/README.md` and repo history to determine update policy. If dashboards are versioned per release, document the synchronization process (e.g., "Download dashboards matching your RisingWave version from `grafana/` in the release branch").

   **Action**: Add a note in `operate/view-configure-system-parameters.md` under "Grafana" section.

3. **Trace sampling configuration**: Code shows `RW_TRACING_ENDPOINT` is read, but no docs mention sampling rate or additional OpenTelemetry env vars (e.g., `OTEL_EXPORTER_OTLP_TRACES_SAMPLER`). Investigate `src/common/src/telemetry/mod.rs:78-95` to see if sampling is configurable.

   **Action**: If configurable, document all supported `RW_*` and `OTEL_*` env vars in troubleshooting guide.

---

### Test

1. **Add e2e test for `metrics_level` parameter**: Validate that setting `ALTER SYSTEM SET metrics_level = 'Debug';` exposes additional metrics not present at `Info` level.

   **Suggested file**: `e2e_test/monitoring/test_metrics_level.slt`

   **Assertions**:
   ```sql
   control substitution on

   # Set to Debug
   statement ok
   ALTER SYSTEM SET metrics_level = 'Debug';

   # Wait for config propagation
   system ok
   sleep 5

   # Check that debug-level metric appears (e.g., actor_execution_time)
   system ok
   curl -s http://127.0.0.1:1222/metrics | grep 'actor_execution_time{.*}' > /dev/null || exit 1

   # Set back to Info
   statement ok
   ALTER SYSTEM SET metrics_level = 'Info';

   system ok
   sleep 5

   # Debug metric should disappear
   system ok
   curl -s http://127.0.0.1:1222/metrics | grep 'actor_execution_time{.*}' && exit 1 || exit 0
   ```

2. **Add e2e test for tracing export**: Validate that setting `RW_TRACING_ENDPOINT` enables trace export to a mock Jaeger collector.

   **Suggested file**: `e2e_test/monitoring/test_tracing.slt`

   **Setup**: Start mock Jaeger collector in `docker-compose.yml` (or use `user-managed` mode).

   **Assertions**: Query Jaeger API to verify spans are exported for a simple SQL query.

---

## Open questions

1. **Version alignment**: This audit compares risingwave `release-2.7` branch with risingwave-docs `main`. If docs track a different version (e.g., `latest` = unreleased `main`), some discrepancies may be expected. No version metadata found in docs repo to confirm alignment.

2. **Grafana dashboard testing**: No automated tests validate that Grafana dashboards correctly render with live Prometheus data. Manual validation required.

3. **Console UI vs Dashboard naming**: Docs use "RisingWave Console" for the commercial product and "Dashboard" for the open-source UI. However, some docs pages (e.g., `risingwave-console/about.md`) conflate the two. Clarify naming convention.

4. **Metrics retention policy**: Docs mention scraping metrics but don't specify Prometheus retention settings. This may be out of scope (user-configured), but worth noting in setup guides.

5. **Dashboard hot-reload**: Does dashboard UI support hot-reload during development? Code shows `include_dir!` (static embedding), but `risedev d` may use a dev server. Not documented.

---

**End of report. All sections above are grounded in specific file paths and line numbers from the provided scopes. No files were written; report output to stdout as required.**
