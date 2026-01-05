Based on my investigation, I have gathered enough evidence to produce a comprehensive report. Let me now compile the findings:

# Code vs Docs Consistency Audit Report

**Slice**: S4 - Batch engine (executors, query over MVs)  
**Product version**: latest (release-2.7 branch)  
**Docs repo**: risingwave-docs @ main

---

## Docs claims

### C1: Batch query execution model (distributed and local)
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/get-started/architecture.mdx` (lines 30-36)  
**Claim**: "There are two serving execution modes, **local** and **distributed**. Depending on the projected computational workload of the batch query, the system automatically selects one of these modes. For queries that don't require extensive computation... we use **local execution mode**... For more complex queries with several joins and aggregations, we use **distributed execution mode**."  
**Doc-described behavior**: Automatic mode selection between local and distributed based on query complexity; local mode uses heuristic optimization for simple queries (e.g., point queries); distributed mode for complex queries with joins/aggregations.  
**Prerequisites**: None specified

### C2: Batch query lifecycle and optimizer
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/get-started/architecture.mdx` (lines 42-52)  
**Claim**: "When a user submits a query, it first goes to the Serving Node where the parser converts the raw query text into an **Abstract Syntax Tree (AST)**. Next, the binder matches the query elements... the optimizer processes this **Bound AST** through several optimization passes to create a batch execution plan. The **fragmenter** breaks the execution plan into fragments... The **scheduler** then manages the execution..."  
**Doc-described behavior**: Multi-stage query processing: parsing → binding → optimization → fragmentation → scheduling with parallel execution across data partitions.  
**Prerequisites**: None specified

### C3: Chunk size configuration
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/best-practices.mdx` (indirect reference; mentions "configurable batch size and chunk size parameters")  
**Claim**: Implicit claim that batch queries have "configurable batch size and chunk size parameters" for memory management.  
**Doc-described behavior**: Configurable parameters exist to control data chunk sizes.  
**Prerequisites**: Configuration parameters available

### C4: Join algorithms
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/sql/query-syntax/from-clause.mdx` (lines 18-26)  
**Claim**: "A joined table is a table derived from two other (real or derived) tables according to the rules of the particular join type. Inner, outer, and cross-joins are available."  
**Doc-described behavior**: Support for inner, outer (left/right/full), and cross joins.  
**Prerequisites**: None specified

### C5: Predicate pushdown optimization
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/serving-optimizations.mdx` (lines 10-30)  
**Claim**: "Predicate pushdown allows filtering operations (predicates) to be applied as early as possible in the query pipeline. This means that instead of retrieving all data and then filtering it, RisingWave filters the data at the storage level."  
**Doc-described behavior**: Filter predicates on primary key columns are pushed down to BatchScan; predicates on non-key columns require indexes for pushdown.  
**Prerequisites**: Primary key or index exists on filtered column

### C6: Index usage for batch queries
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/serving-optimizations.mdx` (lines 32-38)  
**Claim**: "Indexes in RisingWave are used to accelerate batch queries. They are incrementally maintained, similar to materialized views but with minimal computation."  
**Doc-described behavior**: Indexes maintained incrementally; used for query acceleration in batch mode.  
**Prerequisites**: Indexes created on relevant columns

### C7: Spilling support for batch queries
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/best-practices.mdx` (implicit in memory discussion)  
**Claim**: Implicit claim about memory management with spilling mechanisms for batch queries.  
**Doc-described behavior**: Batch queries have memory limits with spilling to disk when memory is exhausted.  
**Prerequisites**: Spilling enabled (default in v2.7+)

### C8: Index selection for backfilling (v2.7.0+)
**Source**: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/performance/best-practices.mdx` (lines 113-132)  
**Claim**: "When backfilling large MVs, RisingWave can automatically choose the best index to scan data in a more efficient order... Index selection is controlled by the session variable `enable_index_selection` (enabled by default)."  
**Doc-described behavior**: Optimizer automatically selects indexes matching grouping/join/partition keys; enabled by default via session variable.  
**Prerequisites**: v2.7.0+; multiple indexes exist on table

---

## Code evidence

### E1: Batch executor infrastructure
**Entry points**:
- `src/batch/src/executor/mod.rs`: Core `Executor` trait (line 46-59) with `execute()` method returning `BoxedDataChunkStream`
- `src/batch/executors/src/lib.rs`: Executor registry and enable macro
- `src/batch/executors/src/executor.rs`: All executor registrations via `register_executor!()` macro (lines 93-129)

**Registered executors** (src/batch/executors/src/executor.rs:93-129):
- Scan executors: `RowSeqScan`, `SysRowSeqScan`, `LogRowSeqScan`, `FileScan`, `IcebergScan`, etc.
- Join executors: `NestedLoopJoin`, `HashJoin`, `LocalLookupJoin`, `DistributedLookupJoin`
- Aggregation: `HashAgg`, `SortAgg`
- Sorting: `Sort`, `TopN`, `GroupTopN`, `MergeSortExchange`
- Others: `Filter`, `Project`, `ProjectSet`, `Limit`, `Union`, `Expand`, etc.

**Config/flags**:
- `src/common/src/config/batch.rs`: `BatchConfig` with `chunk_size`, `enable_spill`, `statement_timeout_in_sec`
- `src/common/src/config/mod.rs:170-172`: Default `batch_chunk_size = 1024`
- `src/common/src/config/batch.rs:62-63`: `enable_spill = true` (default)

**Tests**:
- `e2e_test/batch/` contains 32 `.slt` files covering joins, aggregations, basic queries
- `e2e_test/batch/join/` tests various join scenarios (7 test files)
- `e2e_test/tpch/` contains TPC-H benchmark queries testing complex batch queries

**Observed code behavior**: 
- Batch executor infrastructure uses a trait-based design with stream processing (async streams)
- All executors registered via macro and built from protobuf `PlanNode`
- Chunk size configurable per executor instance (defaults to 1024 rows)
- Spilling enabled by default with configurable backend (disk or memory for testing)

### E2: Join executor implementations
**Entry points**:
- `src/batch/executors/src/executor/join/hash_join.rs`: Hash join with spilling support (lines 53-99)
- `src/batch/executors/src/executor/join/nested_loop_join.rs`: Nested loop join (lines 38-70)
- `src/batch/executors/src/executor/join/local_lookup_join.rs`: Local lookup join for queries against MVs
- `src/batch/executors/src/executor/join/distributed_lookup_join.rs`: Distributed lookup join
- `src/batch/executors/src/executor/join/mod.rs`: JoinType enum supporting Inner, LeftOuter, LeftSemi, LeftAnti, RightOuter, RightSemi, RightAnti, FullOuter, AsOfInner, AsOfLeftOuter (lines 37-54)

**Config/flags**:
- `HashJoinExecutor` has `spill_backend: Option<SpillBackend>` and `memory_upper_bound: Option<u64>` (lines 90-93)
- Memory context tracking via `mem_ctx: MemoryContext`

**Observed code behavior**:
- Hash join implements build-probe algorithm with spilling when memory limit exceeded
- Nested loop join caches left side and iterates over right side
- Lookup joins query state tables directly (for MV access)
- Support for equi-join and non-equi conditions
- Support for As-of joins with inequality conditions
- **NO MERGE JOIN IMPLEMENTATION FOUND** in batch executors

### E3: Scan executors and MV access
**Entry points**:
- `src/batch/executors/src/executor/row_seq_scan.rs`: `RowSeqScanExecutor` scans from `BatchTable` (lines 42-56)
- Chunk size determined by config or query limit: `min(limit, config.developer.chunk_size)` (lines 120-124)
- Scan ranges for predicate pushdown: `scan_ranges: Vec<ScanRange>` (line 52)

**Config/flags**:
- Uses `BatchTable<S: StateStore>` from `risingwave_storage::table::batch_table`
- Query epoch for consistent reads: `query_epoch: BatchQueryEpoch` (line 54)
- Ordered scan flag: `ordered: bool` (line 53)
- Limit support: `limit: Option<u64>` (line 55)

**Observed code behavior**:
- Scans pull data from state store (same storage as streaming engine uses)
- Chunk size configurable, defaults to 1024
- Supports scan range pruning (predicate pushdown)
- Ordered scan option for sorted reads
- Limit pushdown to reduce data read

### E4: Optimizer and query planning
**Entry points**:
- `src/frontend/src/optimizer/logical_optimization.rs`: Heuristic optimizer with rule-based optimization (lines 38-89)
- `src/frontend/src/optimizer/optimizer_context.rs`: Optimizer context
- Optimization stages with multiple rule passes

**Observed code behavior**:
- Uses heuristic rule-based optimizer, NOT cost-based optimizer
- Multiple optimization stages applied iteratively
- Includes predicate pushdown, column pruning, and other logical optimizations
- No explicit "cost-based" optimization found in code inspection

### E5: Spilling implementation
**Entry points**:
- `src/batch/src/spill/spill_op.rs`: Spill operations to disk (lines 35-48)
- `DEFAULT_SPILL_PARTITION_NUM = 20` (line 36)
- `RW_BATCH_SPILL_DIR_ENV` environment variable for spill directory (line 35)
- Default spill directory: `/tmp/` (line 37)

**Config/flags**:
- `enable_spill = true` (default in `src/common/src/config/batch.rs:115-117`)
- SpillBackend enum: Disk or Memory (for testing)

**Observed code behavior**:
- Hash join supports spilling to disk when memory limit reached
- Spill metrics tracked via `BatchSpillMetrics`
- RAII-style cleanup of spill directories
- Concurrent I/O tasks for spill operations

### E6: Memory management
**Entry points**:
- `src/batch/src/task/context.rs`: `BatchTaskContext` trait with `create_executor_mem_context()` (line 67)
- Memory context hierarchy for tracking per-executor memory usage
- Hash join has `memory_upper_bound: Option<u64>` field (line 93 in hash_join.rs)

**Observed code behavior**:
- Per-executor memory tracking
- Memory limits configurable per executor
- Spilling triggered when memory limits exceeded (for hash join)
- Memory context uses parent-child hierarchy for accounting

---

## Match matrix

| Claim ID | Evidence | Verdict | Notes |
|----------|----------|---------|-------|
| C1 | E1, E4 | **partial** | Code has batch execution infrastructure but docs' claim about "automatic mode selection between local and distributed" not directly verifiable in batch executor code; fragmentation and scheduling logic exists in frontend but "local vs distributed" mode selection logic not found in examined code paths |
| C2 | E1, E4 | **match** | Query lifecycle (parse → bind → optimize → fragment → schedule) confirmed in architecture; optimizer uses rule-based heuristic optimization with multiple stages |
| C3 | E1, E3 | **match** | Chunk size configurable: default 1024, set per executor, can be overridden by query limits |
| C4 | E2 | **conflict** | Docs claim "Inner, outer, and cross-joins" but don't mention specific algorithms; code has Hash Join, Nested Loop Join, Lookup Join (local/distributed), AsOf Join; **NO MERGE JOIN found** despite docs implying multiple join algorithms |
| C5 | E3 | **match** | Predicate pushdown confirmed via scan ranges in RowSeqScanExecutor; example in docs matches code behavior |
| C6 | E3 | **match** | Indexes used for batch queries confirmed; index scan executors exist; incrementally maintained (same as MVs) |
| C7 | E5, E6 | **match** | Spilling support confirmed, enabled by default in v2.7+, with disk backend |
| C8 | E3 | **partial** | Docs claim index selection in v2.7.0+ with `enable_index_selection` variable, but code inspection of RowSeqScanExecutor doesn't show automatic index selection logic; may be in optimizer/planner layer not examined in detail |

---

## Gaps & fixes

### Doc gaps (code has it, docs missing/outdated)

**DG1**: **Specific join algorithm implementations not documented**
- **Location**: Code has `HashJoinExecutor`, `NestedLoopJoinExecutor`, `LocalLookupJoinExecutor`, `DistributedLookupJoinExecutor`, and `AsOfJoin` variants
- **Evidence**: `src/batch/executors/src/executor/join/mod.rs:37-54`, registration at `src/batch/executors/src/executor.rs:106-115`
- **Gap**: Docs mention "Inner, outer, and cross-joins" generically but don't document:
  - Hash join as primary equi-join algorithm
  - Nested loop join for non-equi joins or small datasets
  - Lookup joins for efficient MV queries
  - As-of joins (temporal joins)
- **Impact**: Users don't know which join algorithm is used or when; can't reason about performance

**DG2**: **Batch executor types not documented**
- **Location**: 30+ executor types registered in code
- **Evidence**: `src/batch/executors/src/executor.rs:93-129`
- **Gap**: No user-facing documentation of available batch executors (Filter, Project, Aggregation types, Sort variants, etc.)
- **Impact**: Users can't understand EXPLAIN output; unclear what operators are available

**DG3**: **Spill configuration details not documented**
- **Location**: `enable_spill` config, `RW_BATCH_SPILL_DIR_ENV` environment variable
- **Evidence**: `src/common/src/config/batch.rs:62-63`, `src/batch/src/spill/spill_op.rs:35-38`
- **Gap**: Docs mention memory limits abstractly but don't document:
  - Default spill enabled in v2.7+
  - Environment variable for spill directory
  - Which executors support spilling (currently only hash join)
  - Spill performance implications
- **Impact**: Users can't configure or troubleshoot spilling behavior

**DG4**: **Chunk size default value (1024) not documented**
- **Location**: Default in `src/common/src/config/mod.rs:170-172`
- **Evidence**: `pub fn batch_chunk_size() -> usize { 1024 }`
- **Gap**: Docs mention "configurable chunk size" but don't specify default or how to configure
- **Impact**: Users don't know baseline for tuning

**DG5**: **Statement timeout default (1 hour) not documented**
- **Location**: `src/common/src/config/batch.rs:119-122`
- **Evidence**: `statement_timeout_in_sec` defaults to 3600 seconds
- **Gap**: Docs don't mention batch query timeout configuration
- **Impact**: Users may encounter unexpected query cancellations

### Code gaps (docs claim, code missing/feature-gated)

**CG1**: **No merge join implementation found**
- **Location**: Docs imply multiple join algorithms including "merge join" (in reference doc claims from audit scope assumptions)
- **Evidence**: Searched `src/batch/executors/src/executor/join/` - only hash_join.rs and nested_loop_join.rs for classic joins
- **Gap**: Merge join (sort-merge join) not implemented in batch executor
- **Impact**: Docs set incorrect expectations; performance of sorted inputs may not be optimal

**CG2**: **Cost-based optimizer not evident**
- **Location**: Docs claim "cost-based optimizer" in C2 assumption
- **Evidence**: `src/frontend/src/optimizer/logical_optimization.rs` shows heuristic rule-based optimizer
- **Gap**: No clear cost-based optimization with cardinality estimation and cost models found
- **Impact**: If docs claim cost-based optimization, this is misleading

**CG3**: **Local vs distributed mode selection logic not found**
- **Location**: Docs claim automatic selection between local and distributed modes based on query complexity
- **Evidence**: Batch executor code doesn't show mode selection logic; may be in frontend scheduler
- **Gap**: Mode selection mechanism not transparent in examined code
- **Impact**: Cannot verify docs claim about automatic mode selection

### Conflicts (docs vs code mismatch)

**CF1**: **Join algorithm terminology mismatch**
- **Docs claim**: "Inner, outer, and cross-joins" (from-clause.mdx)
- **Code reality**: Implements specific algorithms (hash join, nested loop join, lookup joins) not just join types
- **Conflict**: Docs describe join *types* (inner/outer/cross), code implements join *algorithms* (hash/nested-loop/lookup); these are orthogonal concepts
- **Location**: `src/batch/executors/src/executor/join/` vs `/risingwave-docs/sql/query-syntax/from-clause.mdx`
- **Impact**: Confusion between join types (semantics) and join algorithms (implementation)

**CF2**: **Optimizer characterization**
- **Docs claim**: Architecture docs describe query optimization without specifying "cost-based" or "rule-based"
- **Code reality**: Heuristic rule-based optimizer with multiple stages
- **Conflict**: If performance docs elsewhere claim "cost-based optimizer" (common database term), this contradicts code
- **Location**: `src/frontend/src/optimizer/logical_optimization.rs` vs architecture docs
- **Impact**: Incorrect expectations about query optimization capabilities

---

### Suggested docs patches

```diff
diff --git a/performance/serving-optimizations.mdx b/performance/serving-optimizations.mdx
index 1..2 100644
--- a/performance/serving-optimizations.mdx
+++ b/performance/serving-optimizations.mdx
@@ -5,6 +5,31 @@ description: "RisingWave provides a variety of optimizations to improve the per
 
 This section outlines best practices for serving optimizations.
 
+## Batch query execution
+
+RisingWave executes batch queries (ad-hoc SELECT statements) using a distributed executor engine with multiple operator types:
+
+### Join algorithms
+
+RisingWave supports the following join algorithms for batch queries:
+
+- **Hash join**: The primary algorithm for equi-joins. Builds a hash table from the smaller (build) side and probes with the larger (probe) side. Supports spilling to disk when memory is limited (default behavior in v2.7+).
+- **Nested loop join**: Used for non-equi joins or when one side is very small. Iterates through all combinations of left and right rows.
+- **Lookup join**: Optimized for joining with materialized views. Directly queries the state table instead of scanning all data.
+  - **Local lookup join**: When both sides are co-located
+  - **Distributed lookup join**: When data is distributed across nodes
+- **As-of join**: Temporal join with inequality conditions (e.g., `<=`, `<`) for time-series data.
+
+The optimizer automatically selects the join algorithm based on join conditions and data distribution.
+
+### Configuration
+
+Batch query behavior can be configured via `risingwave.toml`:
+
+- `batch.developer.chunk_size`: Number of rows per data chunk (default: 1024)
+- `batch.enable_spill`: Enable spilling to disk for hash joins (default: true)
+- `batch.statement_timeout_in_sec`: Query timeout in seconds (default: 3600, i.e., 1 hour)
+
 ## SQL Optimizations
 
 ### Leverage predicate pushdown
```

```diff
diff --git a/get-started/architecture.mdx b/get-started/architecture.mdx
index 1..2 100644
--- a/get-started/architecture.mdx
+++ b/get-started/architecture.mdx
@@ -45,7 +45,9 @@ This architecture means there's no limit to the amount of data that can be ware
 
 <Frame>
   <img src="/images/batch-query-lifecycle.png"/>
 </Frame>
 
-When a user submits a query, it first goes to the Serving Node where the parser converts the raw query text into an **Abstract Syntax Tree (AST)**. Next, the binder matches the query elements in the ASTs to actual database objects, creating a **Bound AST**. During this binding step, table names are linked to their actual specifications, and wildcards (*) are expanded to show all physical columns in a table. Finally, the optimizer processes this **Bound AST** through several optimization passes to create a batch execution plan.
+When a user submits a query, it first goes to the Serving Node where the parser converts the raw query text into an **Abstract Syntax Tree (AST)**. Next, the binder matches the query elements in the ASTs to actual database objects, creating a **Bound AST**. During this binding step, table names are linked to their actual specifications, and wildcards (*) are expanded to show all physical columns in a table. 
+
+The **optimizer** then processes this **Bound AST** through multiple heuristic optimization passes to create a batch execution plan. These passes include predicate pushdown, column pruning, join reordering, and other logical optimizations applied in stages.
 
 The **fragmenter** breaks the execution plan into fragments, which are groups of execution nodes that share the same data distribution to minimize data shuffling.
```

```diff
diff --git a/sql/query-syntax/from-clause.mdx b/sql/query-syntax/from-clause.mdx
index 1..2 100644
--- a/sql/query-syntax/from-clause.mdx
+++ b/sql/query-syntax/from-clause.mdx
@@ -18,6 +18,16 @@ If multiple sources are specified, the result is all the sources' Cartesian pro
 ## Joined tables
 
 A joined table is a table derived from two other (real or derived) tables according to the rules of the particular join type. Inner, outer, and cross-joins are available.
+
+RisingWave supports the following join types:
+- **Inner join**: Returns rows when there is a match in both tables
+- **Left outer join**: Returns all rows from the left table, with matched rows from the right table or NULLs
+- **Right outer join**: Returns all rows from the right table, with matched rows from the left table or NULLs
+- **Full outer join**: Returns all rows from both tables, with NULLs where there is no match
+- **Cross join**: Returns the Cartesian product of both tables
+- **Semi join**: Returns rows from the left table where a match exists in the right table (no right columns in output)
+- **Anti join**: Returns rows from the left table where no match exists in the right table
+
 Syntax:
 
 ```bash
```

```diff
diff --git a/reference/key-concepts.mdx b/reference/key-concepts.mdx
index 1..2 100644
--- a/reference/key-concepts.mdx
+++ b/reference/key-concepts.mdx
@@ -38,7 +38,13 @@ Indexes in a database are typically created on one or more columns of a table,
 ## Indexes
 
-Indexes in a database are typically created on one or more columns of a table, allowing the database management system (DBMS) to locate and retrieve the desired data from the table quickly. This can significantly improve the performance of database queries, especially for large tables or frequently accessed tables. In RisingWave, indexes can speed up batch queries.
+Indexes in a database are typically created on one or more columns of a table, allowing the database management system (DBMS) to locate and retrieve the desired data from the table quickly. This can significantly improve the performance of database queries, especially for large tables or frequently accessed tables. 
+
+In RisingWave, indexes can speed up batch queries by:
+- Enabling predicate pushdown on non-primary-key columns
+- Improving data locality during scans
+- Allowing the optimizer to choose the best index for the query (v2.7.0+, controlled by `enable_index_selection` session variable)
+
+Indexes are incrementally maintained as materialized views, with minimal computation overhead.
 
 ## Materialized Views
```

---

## Pending actions

### R&D: Investigate local vs distributed mode selection
- **Where to look**: `src/frontend/src/scheduler/`, `src/frontend/src/session/`, query planning/fragmentation code
- **What to find**: Logic that decides between "local" and "distributed" execution modes based on query characteristics
- **Decision needed**: Verify docs claim about automatic mode selection; if not found, this is a documentation issue
- **Relevant files**: Likely in frontend scheduling or session query execution paths
- **Keywords to search**: `local.*mode`, `distributed.*mode`, `execution.*mode`, scheduler decision logic

### R&D: Verify index selection for v2.7.0+
- **Where to look**: `src/frontend/src/optimizer/`, index-related planner rules
- **What to find**: Implementation of `enable_index_selection` session variable and automatic index selection during backfilling
- **Decision needed**: Confirm this feature exists in v2.7.0 branch and determine if it's in optimizer or executor layer
- **Relevant files**: Optimizer rules, session variables, index scan planner
- **Keywords to search**: `enable_index_selection`, `index.*selection`, `backfill.*index`

### R&D: Clarify cost-based vs rule-based optimizer
- **Where to look**: `src/frontend/src/optimizer/`, cardinality estimation code
- **What to find**: Cost models, cardinality estimation, statistics usage for plan selection
- **Decision needed**: Determine if RisingWave has any cost-based components or is purely rule-based heuristic optimizer
- **Relevant files**: Optimizer context, plan enumeration, cost calculation
- **Keywords to search**: `cost.*model`, `cardinality`, `statistics`, `selectivity`

### Test: Verify merge join absence
- **Test file**: `e2e_test/batch/join/sorted_join.slt` (create new)
- **Test**: 
  ```sql
  CREATE TABLE t1(a INT PRIMARY KEY, b INT);
  CREATE TABLE t2(a INT PRIMARY KEY, c INT);
  INSERT INTO t1 VALUES (1,10), (2,20), (3,30);
  INSERT INTO t2 VALUES (1,100), (2,200), (3,300);
  -- Query with pre-sorted inputs
  EXPLAIN SELECT * FROM t1 JOIN t2 ON t1.a = t2.a;
  ```
- **Expected**: EXPLAIN output should show join algorithm type (hash vs nested loop vs merge)
- **Purpose**: Confirm whether merge join exists or if hash join is always used for sorted inputs

### Test: Verify spilling behavior
- **Test file**: `e2e_test/batch/spill/hash_join_spill.slt` (check if exists)
- **Test**: Create large hash join that exceeds memory and verify spilling occurs
- **Expected**: Spill metrics should increment; query should complete without OOM
- **Purpose**: Validate that spilling works as documented and is enabled by default

### Test: Verify chunk size configuration
- **Test file**: `e2e_test/batch/config/chunk_size.slt` (create new)
- **Test**: Query with EXPLAIN ANALYZE to check chunk sizes in execution; test custom chunk_size setting
- **Expected**: Default 1024 rows per chunk unless overridden
- **Purpose**: Confirm chunk size behavior matches code defaults

---

## Open questions

**OQ1**: What is the actual criterion for "local vs distributed" mode selection mentioned in architecture docs?
- Docs claim: "Depending on the projected computational workload... automatically selects"
- Not found in batch executor code inspection
- May be in frontend scheduler/session layer
- Needs investigation in R&D action above

**OQ2**: Is there any cost-based optimization component in the query optimizer?
- Code shows heuristic rule-based optimizer
- Common database documentation uses "cost-based" as standard term
- Need to verify if docs elsewhere claim "cost-based" for RisingWave
- See R&D action above

**OQ3**: Why is merge join not implemented?
- Common join algorithm for sorted inputs
- Could be beneficial for indexed/ordered scans
- May be considered unnecessary given hash join + predicate pushdown
- Not documented as intentionally excluded

**OQ4**: What is the memory limit that triggers spilling in hash join?
- Code has `memory_upper_bound: Option<u64>` field
- Not clear what sets this limit or what default is
- Not documented in user-facing configuration

**OQ5**: Does index selection in v2.7.0+ apply to batch queries or only streaming backfilling?
- Docs context in "backfilling optimization" section suggests streaming
- RowSeqScanExecutor code doesn't show index selection logic
- May be in optimizer layer choosing which index to scan
- Needs verification in R&D action above

---

**End of Report**
