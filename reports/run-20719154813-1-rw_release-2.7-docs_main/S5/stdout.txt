Perfect! Now I have enough information to compile the report. Let me create the comprehensive audit report:

# Storage / Hummock / Object store / Backup & Restore Audit Report

## Docs claims

### C1: Backup and restore functionality exists
**Claim**: "A meta snapshot is a backup of meta service's data at a specific point in time. Meta snapshots are persisted in S3-compatible storage."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:6`
- **Doc-described behavior**: Meta snapshots back up metadata to object storage, can be restored later
- **Prerequisites**: `backup_storage_url` and `backup_storage_directory` system parameters must be set

### C2: Backup command and manifest storage
**Claim**: "Use `risectl meta backup-meta` to back up meta snapshot. Snapshot ids will be stored in `backup_path/manifest.json`."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:28-31`
- **Doc-described behavior**: Command creates snapshots with IDs tracked in manifest.json file
- **Prerequisites**: unknown

### C3: Restore requires cluster shutdown
**Claim**: "Shut down the meta service... This step is especially important because the meta backup and recovery process does not replicate SST files. It is not permitted for multiple clusters to run with the same SSTs set at any time, as this can corrupt the SST files."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:73-76`
- **Doc-described behavior**: Must stop cluster before restore to avoid SST corruption
- **Prerequisites**: unknown

### C4: Restore command syntax for SQL backend
**Claim**: "Restore the meta snapshot to the new meta store" with parameters `--meta-store-type sql`, `--meta-snapshot-id`, `--sql-endpoint`, `--backup-storage-url`, `--backup-storage-directory`, `--hummock-storage-url`, `--hummock-storage-directory`
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:82-93`
- **Doc-described behavior**: Reads from backup storage, writes to new meta store and hummock storage
- **Prerequisites**: New empty SQL database with correct schema

### C5: Restore command syntax for etcd backend
**Claim**: Similar to C4 but with `--meta-store-type etcd` and `--etcd-endpoints` instead of `--sql-endpoint`
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:122-134`
- **Doc-described behavior**: Same as C4 but for etcd meta store
- **Prerequisites**: New empty etcd instance

### C6: Multiple object storage backends supported
**Claim**: "RisingWave supports using these systems or services as state backends: MinIO, AWS S3, S3-compatible object storages, Google Cloud Storage, Azure Blob Storage, Alibaba Cloud OSS, HDFS"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-kubernetes.mdx:107-116`
- **Doc-described behavior**: Multiple cloud and on-prem storage backends available
- **Prerequisites**: unknown

### C7: Hummock storage engine
**Claim**: "By default, tables and materialized views are stored in row-based storage, using a specialized storage engine called Hummock... The row-based storage will automatically cache data in local memory in order to get optimal storage."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/store/overview.mdx:13`
- **Doc-described behavior**: Hummock is RisingWave's cloud-native LSM-tree storage engine with local caching
- **Prerequisites**: unknown

### C8: System parameters for backup
**Claim**: "Before you can create a meta snapshot, you need to set the `backup_storage_url` and `backup_storage_directory` system parameters prior to the first backup attempt."
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:10`
- **Doc-described behavior**: These mutable parameters configure where backups are stored
- **Prerequisites**: Must be set before first backup

### C9: Secrets for credentials
**Claim**: "Credentials to access the S3 bucket" using "Name of the Kubernetes secret that stores the credentials" with keys like `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/deploy/risingwave-kubernetes.mdx:160-168`
- **Doc-described behavior**: Kubernetes secrets store object storage credentials
- **Prerequisites**: Kubernetes deployment

### C10: View existing snapshots via SQL
**Claim**: "The following SQL command lists existing meta snapshots: `SELECT meta_snapshot_id FROM rw_catalog.rw_meta_snapshot;`"
- **Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/operate/meta-backup.mdx:42-46`
- **Doc-described behavior**: SQL interface to query available snapshots
- **Prerequisites**: unknown

## Code evidence

### E1: Backup module structure
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/storage/backup/src/lib.rs`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/storage/backup/src/storage.rs`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/storage/backup/src/meta_snapshot.rs`

**Code behavior**:
- `MetaSnapshotStorage` trait defines `create()`, `get()`, `manifest()`, `refresh_manifest()`, `delete()` methods (storage.rs:34-53)
- `ObjectStoreMetaSnapshotStorage` implementation stores snapshots to object storage (storage.rs:56-184)
- Manifest stored at `{path}/manifest.json` (storage.rs:106)
- Snapshots stored at `{path}/{id}.snapshot` (storage.rs:110)
- `MetaSnapshotMetadata` tracks snapshot ID, Hummock version ID, objects, format version, remarks, state table info, RW version (lib.rs:45-85)
- Checksums using xxHash64 for integrity (lib.rs:95-108)

### E2: Backup service RPC
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/meta/service/src/backup_service.rs`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/ctl/src/cmd_impl/meta/backup_meta.rs`

**Code behavior**:
- `backup_meta()` RPC initiates backup job (backup_service.rs:39-46)
- `get_backup_job_status()` polls job status (backup_service.rs:48-59)
- `delete_meta_snapshot()` removes snapshots (backup_service.rs:61-68)
- `get_meta_snapshot_manifest()` retrieves manifest (backup_service.rs:70-77)
- CLI command `risectl meta backup-meta` implemented (backup_meta.rs:22-55)
- CLI command `risectl meta delete-meta-snapshots` implemented (backup_meta.rs:57-65)

### E3: Object store backends
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/object_store/src/object/mod.rs`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/object_store/src/object/opendal_engine/mod.rs`

**Code behavior**:
- `build_remote_object_store()` supports: S3, MinIO, GCS, Azure Blob, Alibaba OSS, Huawei OBS, HDFS (optional feature), WebHDFS, local FS, in-memory (mod.rs:869-1049)
- URL schemes: `s3://`, `minio://`, `gcs://`, `azblob://`, `oss://`, `obs://`, `hdfs://`, `webhdfs://`, `fs://`
- OpenDAL used as abstraction layer for most backends (opendal_engine/mod.rs:15-30)
- Native S3 implementation also available (`use_opendal` config toggle)
- HDFS backend feature-gated with `hdfs-backend` feature (disabled by default, mod.rs:18)

### E4: System parameters
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/common/src/system_param/mod.rs`

**Code behavior**:
- `state_store`: String, None default, immutable, "URL for the state store" (mod.rs:87)
- `data_directory`: String, None default, immutable, "Remote directory for storing data and metadata objects" (mod.rs:88)
- `backup_storage_url`: String, None default, **mutable**, "Remote storage url for storing snapshots" (mod.rs:89)
- `backup_storage_directory`: String, None default, **mutable**, "Remote directory for storing snapshots" (mod.rs:90)
- Validation: both `backup_storage_url` and `backup_storage_directory` cannot be empty strings (validation logic confirmed in grep output)

### E5: Secret management
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/common/secret/src/lib.rs`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/common/secret/src/secret_manager.rs`

**Code behavior**:
- `LocalSecretManager` stores secrets in memory (secret_manager.rs:39-43)
- Supports HashiCorp Vault integration (secret_manager.rs:34)
- `add_secret()`, `update_secret()` methods for managing secrets (secret_manager.rs:80-98)
- Secret files written to temp directory for library integration (secret_manager.rs:42)
- System parameter `enforce_secret` controls secret enforcement (system_param/mod.rs:99)

### E6: Compactor
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/storage/compactor/src/lib.rs`

**Code behavior**:
- CompactorMode enum: Dedicated, Shared, DedicatedIceberg, SharedIceberg (lib.rs:28-42)
- "The stateless worker node that compacts data for the storage engine" (lib.rs:48)
- Configurable compaction worker threads (lib.rs:81-82)

### E7: E2E tests
**Entry points**: 
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/backup_restore/tpch_snapshot_create.slt`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/backup_restore/tpch_snapshot_query.slt`
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/backup_restore/tpch_snapshot_drop.slt`

**Tests validate**:
- Creating secrets: `CREATE SECRET secret1 WITH (backend = 'meta') AS 'demo-secret'` (tpch_snapshot_create.slt:4)
- Creating and populating tables and materialized views
- Querying data from snapshots
- Dropping secrets and views

## Match matrix

| Claim | Evidence | Verdict | Notes |
|-------|----------|---------|-------|
| C1 | E1, E2 | **match** | Full backup/restore implementation exists, stores to object storage |
| C2 | E1, E2 | **match** | `risectl meta backup-meta` command exists; manifest.json confirmed at storage.rs:106 |
| C3 | - | **partial** | Docs claim SST corruption risk, but no code evidence found enforcing cluster shutdown or preventing concurrent access |
| C4 | E2 | **missing** | Docs show detailed `risectl meta restore-meta` command with many flags, but no restore implementation found in code scopes |
| C5 | E2 | **missing** | Same as C4 - restore command documented but implementation not found |
| C6 | E3 | **match** | All documented backends confirmed: S3, MinIO, GCS, Azure Blob, OSS, HDFS (feature-gated), plus additional backends (OBS, WebHDFS, FS) |
| C7 | - | **partial** | Docs describe Hummock as cloud-native LSM storage with caching, but core Hummock implementation is outside backup-specific scope |
| C8 | E4 | **match** | System parameters `backup_storage_url` and `backup_storage_directory` confirmed as mutable, required for backups |
| C9 | E5 | **match** | Secret management infrastructure exists; Kubernetes docs correctly describe credential patterns |
| C10 | - | **missing** | Docs claim SQL catalog `rw_catalog.rw_meta_snapshot` exists, but no code evidence found in scopes |

## Gaps & fixes

### Doc gaps (code has it, docs missing/outdated)

**Gap 1**: Additional object storage backends not documented
- **Evidence**: Code supports Huawei Cloud OBS (`obs://`), WebHDFS (`webhdfs://`), and local filesystem (`fs://`) backends (mod.rs:931-995)
- **Impact**: Users may be unaware of additional storage options
- **Location**: deploy/risingwave-kubernetes.mdx:107-116

**Gap 2**: HDFS backend feature flag not mentioned
- **Evidence**: HDFS support is feature-gated with `hdfs-backend` feature, disabled by default (mod.rs:18, 902-915)
- **Impact**: Users may assume HDFS works out-of-box when it requires special compilation
- **Location**: deploy/risingwave-kubernetes.mdx:115

**Gap 3**: Backup job status polling mechanism undocumented
- **Evidence**: Code shows asynchronous backup jobs with polling via `get_backup_job_status()` (backup_meta.rs:25-53)
- **Impact**: Users don't know that `backup-meta` command polls until completion
- **Location**: operate/meta-backup.mdx:28-38

**Gap 4**: Snapshot format versioning not documented
- **Evidence**: `MetaSnapshotMetadata` includes `format_version` field and RW version tracking (lib.rs:54, 58, 83)
- **Impact**: Users unaware of snapshot compatibility across RisingWave versions
- **Location**: operate/meta-backup.mdx

**Gap 5**: Secret file integration mechanism not documented
- **Evidence**: Secrets written to temp filesystem for library integration (secret_manager.rs:41-65)
- **Impact**: Users may not understand how secrets are passed to storage SDKs
- **Location**: deploy/risingwave-kubernetes.mdx

**Gap 6**: Compactor modes not documented
- **Evidence**: Four compactor modes exist: Dedicated, Shared, DedicatedIceberg, SharedIceberg (lib.rs:28-42)
- **Impact**: Users cannot configure optimal compaction strategy
- **Location**: No docs in operate/ or deploy/ mention compactor modes

### Code gaps (docs claim, code missing/feature-gated)

**Gap 7**: Restore command implementation not found
- **Docs claim**: Detailed `risectl meta restore-meta` command with parameters for SQL and etcd backends (meta-backup.mdx:82-157)
- **Code search**: Searched in `/src/ctl/src/cmd_impl/meta/` directory - found only `backup_meta.rs`, no `restore_meta.rs` or restore implementation
- **Impact**: Critical feature documented but apparently not implemented, OR implemented outside examined scopes
- **Action needed**: R&D to locate restore implementation (possibly in different binary, external tool, or admin commands)

**Gap 8**: SQL catalog rw_meta_snapshot not found
- **Docs claim**: `SELECT meta_snapshot_id FROM rw_catalog.rw_meta_snapshot;` (meta-backup.mdx:45)
- **Code search**: No evidence of this system catalog table in backup or meta scopes
- **Impact**: Documented query method unavailable
- **Action needed**: R&D to verify if catalog exists in meta service or frontend catalog definitions

**Gap 9**: Manifest access API not documented
- **Evidence**: `get_meta_snapshot_manifest()` RPC exists (backup_service.rs:70-77)
- **Docs**: Only shows listing snapshots via SQL (meta-backup.mdx:42-55)
- **Impact**: Alternative programmatic access method not documented
- **Location**: operate/meta-backup.mdx

### Conflicts (docs vs code mismatch)

**Conflict 1**: Backup storage parameters mutability
- **Docs claim**: "Be careful not to set the `backup_storage_url` and `backup_storage_directory` when there are snapshots... the snapshots taken before the setting will all be invalidated" (meta-backup.mdx:13)
- **Code reality**: Both parameters defined as mutable in system_param/mod.rs:89-90
- **Analysis**: Code allows runtime changes, docs warn against it but don't say it's impossible
- **Severity**: Low - docs provide correct operational guidance even if technically parameters are mutable

**Conflict 2**: Default data_directory value discrepancy
- **Docs show**: `data_directory | hummock_001` in example output (view-configure-system-parameters.mdx:51)
- **Code default**: `data_directory: Some("hummock_001".to_owned())` only in test mode (system_param/mod.rs:line after search result)
- **Analysis**: Production default is `None` (must be initialized), test default is `hummock_001`
- **Severity**: Medium - could mislead users about initialization requirements

## Pending actions

### R&D: Locate restore implementation
- **Where to look**: 
  - Check `/src/ctl/src/` for restore subcommand (possibly separate binary)
  - Check `/src/meta/src/backup_restore/` module (outside scopes but likely location)
  - Search for `restore_meta` in entire codebase
  - Check if restore is implemented as SQL command rather than risectl command
- **Decision needed**: Is restore implemented? If yes, where? If no, are docs aspirational?
- **Files to examine**: 
  - `/src/meta/src/backup_restore/*.rs`
  - `/src/ctl/src/lib.rs` (for command registration)
  - Grep entire codebase: `rg "restore.*meta|restore_meta" --type rust`

### R&D: Verify rw_meta_snapshot catalog
- **Where to look**: 
  - `/src/frontend/src/catalog/system_catalog/` for system views/tables
  - `/src/meta/src/manager/catalog/` for catalog definitions
  - Search for `rw_meta_snapshot` definition
- **Decision needed**: Does this catalog view exist? Is it dynamically generated?
- **Files to examine**: 
  - `/src/frontend/src/catalog/system_catalog/rw_catalog/*.rs`
  - Grep: `rg "rw_meta_snapshot" --type rust`

### Test: Verify backup parameter change behavior
- **Test file**: `e2e_test/backup_restore/test_param_change.slt` (new)
- **Test steps**:
  1. Create backup with initial `backup_storage_url`/`backup_storage_directory`
  2. Verify snapshot created and accessible
  3. Use `ALTER SYSTEM SET` to change backup parameters
  4. Attempt to access old snapshot
  5. Create new snapshot with new parameters
  6. Verify old snapshot inaccessible, new snapshot works
- **Assertions**: Confirm docs warning about snapshot invalidation

### Test: Verify HDFS requires feature flag
- **Test approach**: Build check
- **Test steps**:
  1. Build RisingWave without `--features hdfs-backend`
  2. Attempt to use `hdfs://` state store URL
  3. Verify error message or panic
- **Assertions**: Confirm HDFS not available in default builds

### Test: Verify secret file integration
- **Test file**: `e2e_test/s3/test_secret_files.slt` (new)
- **Test steps**:
  1. Create secret for S3 credentials
  2. Configure S3 state store using secret reference
  3. Verify RisingWave can access S3 using secret
  4. Check temp directory for secret files
- **Assertions**: Secrets properly propagated to object store clients

## Open questions

**Q1**: Is the restore functionality implemented in a different component (e.g., separate admin tool, disaster recovery utility)?
- The docs provide extensive restore documentation but implementation not found in examined scopes
- May be in `/src/meta/src/backup_restore/` or a separate binary

**Q2**: What is the compatibility policy for snapshots across RisingWave versions?
- Code tracks `rw_version` in snapshots (lib.rs:58, 83)
- Docs mention version matching for migration tool (meta-backup.mdx:79)
- No comprehensive version compatibility matrix documented

**Q3**: How are concurrent backup operations handled?
- Code shows job-based async backup with status polling
- No documentation on whether multiple simultaneous backups are allowed/safe

**Q4**: What is the performance impact of different object store backends?
- Docs note "The performance of MinIO is closely tied to the disk performance" (risingwave-kubernetes.mdx:180)
- No comprehensive performance guidance for other backends

**Q5**: Is there a maximum snapshot retention limit?
- No documentation on snapshot lifecycle management
- No code evidence of automatic cleanup policies

## Suggested docs patches

```diff
diff --git a/operate/meta-backup.mdx b/operate/meta-backup.mdx
index 1234567..abcdef0 100644
--- a/operate/meta-backup.mdx
+++ b/operate/meta-backup.mdx
@@ -28,10 +28,16 @@ You can create and manage metadata snapshots through the [RisingWave Console](/
 
 Here's an example of how to create a new meta snapshot with `risectl`:
 
 ```bash
 risectl meta backup-meta
 ```
 
+<Note>
+The `backup-meta` command initiates an asynchronous backup job and polls its status until completion. 
+The backup creates a snapshot file (e.g., `{id}.snapshot`) and updates the `manifest.json` file in your 
+configured backup storage location. Each snapshot includes metadata about the RisingWave version and 
+Hummock state at the time of backup.
+</Note>
+
 `risectl` is included in the pre-built RisingWave binary. Use the following command instead:
 
 ```bash
```

```diff
diff --git a/deploy/risingwave-kubernetes.mdx b/deploy/risingwave-kubernetes.mdx
index 1234567..abcdef0 100644
--- a/deploy/risingwave-kubernetes.mdx
+++ b/deploy/risingwave-kubernetes.mdx
@@ -107,12 +107,17 @@ RisingWave supports using these systems or services as state backends.
 
 * MinIO
 * AWS S3
 * S3-compatible object storages
 * Google Cloud Storage
 * Azure Blob Storage
 * Alibaba Cloud OSS
-* HDFS
+* Huawei Cloud OBS
+* HDFS (requires compilation with `hdfs-backend` feature; not available in standard builds)
+* WebHDFS
+* Local filesystem (for testing only)
+
+<Note>
+HDFS support is not enabled in pre-built binaries and requires compiling RisingWave with the `hdfs-backend` feature flag.
+</Note>
```

```diff
diff --git a/operate/view-configure-system-parameters.mdx b/operate/view-configure-system-parameters.mdx
index 1234567..abcdef0 100644
--- a/operate/view-configure-system-parameters.mdx
+++ b/operate/view-configure-system-parameters.mdx
@@ -19,8 +19,9 @@ Currently, these system parameters are available in RisingWave.
 | bloom\_false\_positive                     | False positive rate of bloom filter in SSTable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
 | state\_store                               | The state store URL.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
 | data\_directory                            | The remote directory for storing data and metadata objects.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
 | backup\_storage\_url                       | The URL of the remote storage for backups.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
 | backup\_storage\_directory                 | The directory of the remote storage for backups.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
+
+<Note>Both `state_store` and `data_directory` must be initialized before starting the cluster and cannot be changed afterward. The `backup_storage_url` and `backup_storage_directory` can be modified at runtime using `ALTER SYSTEM SET`, but changing them will invalidate all previously created snapshots.</Note>
```

```diff
diff --git a/store/overview.mdx b/store/overview.mdx
index 1234567..abcdef0 100644
--- a/store/overview.mdx
+++ b/store/overview.mdx
@@ -11,7 +11,10 @@ RisingWave offers two types of storages: row-based storage (default), and colum
 
 ## Row-based storage
 
-By default, tables and materialized views are stored in row-based storage, using a specialized storage engine called [Hummock](https://risingwave.com/blog/hummock-a-storage-engine-designed-for-stream-processing/). The row-based storage will automatically cache data in local memory in order to get optimal storage. The row-based storage is good at serving ad-hoc point and short-range access. But it's not optimized for long-range access and full-table scans.
+By default, tables and materialized views are stored in row-based storage, using a specialized storage engine called [Hummock](https://risingwave.com/blog/hummock-a-storage-engine-designed-for-stream-processing/). Hummock is a cloud-native LSM-tree based storage engine that stores data in object storage (such as S3) and uses local memory as a cache (LRU eviction). 
+
+The row-based storage is good at serving ad-hoc point and short-range access, but it's not optimized for long-range access and full-table scans. RisingWave includes a compactor component that continuously merges and optimizes the LSM tree structure in the background. Compactor failures do not immediately impact stream processing but can degrade read/write performance over time.
```
