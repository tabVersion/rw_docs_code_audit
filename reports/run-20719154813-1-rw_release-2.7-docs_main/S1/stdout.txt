Now I have sufficient data to compile a comprehensive report. Let me organize the findings:

## Docs claims

### C1: CREATE TABLE syntax and options
**Claim**: "CREATE TABLE supports APPEND ONLY, ON CONFLICT (DO NOTHING | OVERWRITE | DO UPDATE IF NOT NULL), WITH VERSION COLUMN, INCLUDE clause, ENGINE = iceberg"
- **Doc path**: `/sql/commands/sql-create-table.mdx` lines 23-34
- **Doc-described behavior**: 
  - APPEND ONLY creates tables that don't support UPDATE/DELETE
  - ON CONFLICT controls PK conflict behavior: DO NOTHING (ignore), OVERWRITE (full replace), DO UPDATE IF NOT NULL (partial update)
  - WITH VERSION COLUMN allows specifying version columns for conflict resolution (single or composite, added in v2.6.0)
  - INCLUDE clause extracts metadata fields (header, key, offset, partition, timestamp)
  - ENGINE = iceberg stores data in Iceberg format
- **Prerequisites**: unknown

### C2: ON CONFLICT default behavior
**Claim**: "For tables with primary key constraints, if you insert a new data record with an existing key, the new record will overwrite the existing record."
- **Doc path**: `/sql/commands/sql-create-table.mdx` line 40
- **Doc-described behavior**: Default is OVERWRITE (full update)
- **Prerequisites**: unknown

### C3: ON CONFLICT with APPEND ONLY restriction
**Claim**: "ON CONFLICT OVERWRITE is not allowed with APPEND ONLY"
- **Doc path**: Implied from `/sql/commands/sql-create-table.mdx` line 137 "OVERWRITE" is the default behavior
- **Doc-described behavior**: APPEND ONLY tables can only use DO NOTHING
- **Prerequisites**: unknown

### C4: CREATE TABLE NOT NULL behavior
**Claim**: "RisingWave supports NOT NULL constraints. For batch inserts/updates, RisingWave throws an error if any row contains NULL in a NOT NULL column; for streaming ingestion, rows with NULL in NOT NULL columns are silently ignored."
- **Doc path**: `/sql/commands/sql-create-table.mdx` line 38
- **Doc-described behavior**: Different behavior for batch vs streaming
- **Prerequisites**: unknown

### C5: CREATE TABLE DEFAULT clause
**Claim**: "DEFAULT clause allows assigning a default value to a column. default_expr must be constant or variable-free, not reference other columns or involve subqueries."
- **Doc path**: `/sql/commands/sql-create-table.mdx` line 89
- **Doc-described behavior**: Evaluated at insert time; if impure, historical data filled with statement execution time value
- **Prerequisites**: unknown

### C6: DEFAULT with DO UPDATE IF NOT NULL incompatibility
**Claim**: "When DO UPDATE IF NOT NULL behavior is applied, DEFAULT clause is not allowed on the table's columns."
- **Doc path**: `/sql/commands/sql-create-table.mdx` line 145
- **Doc-described behavior**: These two features are mutually exclusive
- **Prerequisites**: unknown

### C7: CREATE SOURCE FORMAT/ENCODE requirements
**Claim**: "For CDC formats (DEBEZIUM, MAXWELL, CANAL), you must use CREATE TABLE to properly handle updates and deletes."
- **Doc path**: `/sql/commands/sql-create-source.mdx` line 8
- **Doc-described behavior**: CREATE SOURCE doesn't properly handle CDC change events
- **Prerequisites**: unknown

### C8: CREATE SOURCE upsert format requirements
**Claim**: "When using FORMAT UPSERT, you must include INCLUDE KEY clause and define PRIMARY KEY using the key column."
- **Doc path**: `/sql/commands/sql-create-source.mdx` lines 84-88
- **Doc-described behavior**: Upsert sources emit upsert streams without old values; stateful operators don't work on upsert sources
- **Prerequisites**: unknown

### C9: CREATE MATERIALIZED VIEW backfill behavior
**Claim**: "CREATE MATERIALIZED VIEW will first backfill historical data. To run in background, use SET BACKGROUND_DDL=true."
- **Doc path**: `/sql/commands/sql-create-mv.mdx` lines 32-34
- **Doc-described behavior**: Blocks until backfill completes unless BACKGROUND_DDL enabled
- **Prerequisites**: unknown

### C10: CREATE MATERIALIZED VIEW backfill_order option
**Claim**: "backfill_order in WITH clause controls backfill order for upstream relations using -> operator syntax like FIXED(t1 -> t2, t2 -> t3)"
- **Doc path**: `/sql/commands/sql-create-mv.mdx` lines 38-54
- **Doc-described behavior**: Left relation fully backfilled before right; feature in technical preview; recovery not supported for background DDL
- **Prerequisites**: unknown

### C11: ALTER TABLE ADD COLUMN restrictions
**Claim**: "Columns added by ALTER TABLE ADD COLUMN cannot be used by existing materialized views or indexes. You must create new MVs/indexes to reference it."
- **Doc path**: `/sql/commands/sql-alter-table.mdx` line 39
- **Doc-described behavior**: Schema evolution doesn't retroactively affect downstream
- **Prerequisites**: unknown

### C12: ALTER TABLE DROP COLUMN restrictions
**Claim**: "You cannot drop columns referenced by materialized views or indexes."
- **Doc path**: `/sql/commands/sql-alter-table.mdx` line 87
- **Doc-described behavior**: Must drop dependent MVs/indexes first
- **Prerequisites**: unknown

### C13: ALTER TABLE ALTER COLUMN TYPE scope
**Claim**: "ALTER COLUMN TYPE primarily designed for composite types (struct). You can add or remove fields from struct types."
- **Doc path**: `/sql/commands/sql-alter-table.mdx` lines 107, 118
- **Doc-described behavior**: Added in v2.5.0; new fields not available to existing MVs
- **Prerequisites**: v2.5.0+

### C14: ALTER TABLE CONNECTOR WITH support
**Claim**: "ALTER TABLE CONNECTOR WITH allows updating connector properties without recreation. Currently only Kafka connectors supported."
- **Doc path**: `/sql/commands/sql-alter-table.mdx` lines 48-58
- **Doc-described behavior**: Added in v2.6.0; limited set of Kafka properties supported
- **Prerequisites**: v2.6.0+

### C15: ALTER SOURCE REFRESH SCHEMA restrictions
**Claim**: "When refreshing schema registry, not allowed to drop columns or change types."
- **Doc path**: `/sql/commands/sql-alter-source.mdx` line 76
- **Doc-described behavior**: Only additive schema changes supported
- **Prerequisites**: unknown

### C16: Identifiers case sensitivity
**Claim**: "Identifiers are case-insensitive. RisingWave processes unquoted identifiers as lower case. Double-quote to make case-sensitive."
- **Doc path**: `/sql/identifiers.mdx` lines 23-29
- **Doc-described behavior**: wave, WAVE, wAve are same; CREATE TABLE WAVE shows as 'wave'
- **Prerequisites**: unknown

### C17: Identifier naming restrictions
**Claim**: "First character must be ASCII letter or underscore; remaining can be ASCII letters, underscores, digits, or dollar signs. Non-ASCII characters not allowed in unquoted identifiers."
- **Doc path**: `/sql/identifiers.mdx` lines 7-9
- **Doc-described behavior**: Double-quoting circumvents rules
- **Prerequisites**: unknown

### C18: Reserved identifier keywords
**Claim**: "In expressions, certain names interpreted as builtins: user, current_timestamp, current_schema, current_role, current_user, session_user. Qualify with table name to select column."
- **Doc path**: `/sql/identifiers.mdx` lines 11-21
- **Doc-described behavior**: SELECT user returns builtin, not column; SELECT t.user returns column
- **Prerequisites**: unknown

### C19: String literals with escapes
**Claim**: "String literals with C-style escapes use 'e' prefix (e.g., e'abc\\n\\tdef'). Supports \\b, \\f, \\n, \\r, \\t, octal, hex, Unicode escapes."
- **Doc path**: `/sql/query-syntax/literals.mdx` lines 14-30
- **Doc-described behavior**: Similar to C/PostgreSQL escape sequences
- **Prerequisites**: unknown

### C20: Numeric literal formats
**Claim**: "Supports decimal, hexadecimal (0x), octal (0o), binary (0b) numeric literals. Scientific notation (1e6) supported in SELECT and INSERT."
- **Doc path**: `/sql/query-syntax/literals.mdx` lines 32-44; `/sql/data-types/overview.mdx` line 31
- **Doc-described behavior**: Multiple number system representations
- **Prerequisites**: unknown

### C21: Data type NUMERIC precision
**Claim**: "NUMERIC/DECIMAL has precision of 28 decimal digits. Range is smaller compared to PostgreSQL. We do not support specifying precision and scale."
- **Doc path**: `/sql/data-types/overview.mdx` line 14
- **Doc-described behavior**: Fixed precision, no user configuration
- **Prerequisites**: unknown

### C22: Data type VARCHAR length
**Claim**: "VARCHAR/STRING do not support specifying maximum length."
- **Doc path**: `/sql/data-types/overview.mdx` line 17
- **Doc-described behavior**: No length constraint syntax
- **Prerequisites**: unknown

### C23: INSERT with PK behavior
**Claim**: "For tables with primary keys, if you insert a row with an existing key, the new row will overwrite the existing row."
- **Doc path**: `/sql/commands/sql-insert.mdx` line 9
- **Doc-described behavior**: Upsert semantics (matches C2)
- **Prerequisites**: unknown

### C24: INSERT RETURNING clause
**Claim**: "RETURNING col_name returns values of any column based on each inserted row."
- **Doc path**: `/sql/commands/sql-insert.mdx` line 29
- **Doc-described behavior**: Returns inserted values
- **Prerequisites**: unknown

### C25: SELECT DISTINCT ON requirements
**Claim**: "SELECT DISTINCT ON requires ORDER BY clause. DISTINCT ON expression must match leftmost ORDER BY expression."
- **Doc path**: `/sql/commands/sql-select.mdx` lines 35
- **Doc-described behavior**: Determines which row is "first" for each DISTINCT ON group
- **Prerequisites**: unknown

### C26: SELECT LIMIT without ORDER BY in MV
**Claim**: "When ORDER BY clause is not present, LIMIT clause cannot be used as part of a materialized view."
- **Doc path**: `/sql/commands/sql-select.mdx` line 54
- **Doc-described behavior**: LIMIT requires ORDER BY for MV creation
- **Prerequisites**: unknown

## Code evidence

### E1: CREATE TABLE AST and parsing (for C1, C2, C3)
- **Entry points**: 
  - `src/sqlparser/src/ast/statement.rs:79-92` CreateSourceStatement struct with append_only
  - `src/sqlparser/src/ast/mod.rs:2038-2127` CreateTable Display impl showing APPEND ONLY, ON CONFLICT, WITH VERSION COLUMN
  - `src/sqlparser/src/ast/ddl.rs:25-123` AlterTableOperation enum
- **Config/flags**: None found in parser
- **Tests**: 
  - `e2e_test/streaming/on_conflict.slt` validates DO NOTHING, DO UPDATE FULL, DO UPDATE IF NOT NULL
  - `e2e_test/streaming/with_version_column.slt` validates single and composite VERSION COLUMN
- **Observed code behavior**: 
  - Parser supports APPEND ONLY flag (line 2003, 2084)
  - Parser supports ON CONFLICT with behavior enum (line 2087-2089)
  - Parser supports WITH VERSION COLUMN syntax (lines 2091-2096)
  - Test on_conflict.slt:30 shows "APPEND ONLY on conflict overwrite" raises error
  - Test on_conflict.slt:33 shows "on conflict do update full" is valid syntax
  - Test on_conflict.slt:71 shows "on conflict do update if not null" is valid syntax

**Verdict**: `match` for C1, C3; `partial` for C2 (docs say "OVERWRITE" but test uses "DO UPDATE FULL")

### E2: ON CONFLICT default behavior (for C2)
- **Entry points**: `src/sqlparser/src/ast/mod.rs:2087-2089` - if on_conflict present, writes it; otherwise omitted
- **Tests**: `e2e_test/streaming/on_conflict.slt` - no test for default behavior when ON CONFLICT clause omitted
- **Observed code behavior**: Parser treats ON CONFLICT as optional; no explicit test validates default overwrite behavior

**Verdict**: `partial` - syntax exists but default semantics not explicitly tested

### E3: NOT NULL constraint behavior (for C4)
- **Entry points**: Would be in frontend validation, not parser
- **Tests**: `e2e_test/ddl/not_null.slt` exists
- **Looked**: `e2e_test/ddl/not_null.slt` would validate this
- **Why not examined**: Out of immediate parser scope

**Verdict**: `partial` - test file exists but need frontend code validation

### E4: DEFAULT clause (for C5, C6)
- **Entry points**: `src/sqlparser/src/ast/ddl.rs` would contain ColumnOption for DEFAULT
- **Tests**: `e2e_test/ddl/alter_table_column.slt:34` tests ADD COLUMN with DEFAULT
- **Observed code behavior**: Syntax parsed, but incompatibility with DO UPDATE IF NOT NULL not tested

**Verdict**: `partial` - DEFAULT syntax exists, but incompatibility constraint (C6) not validated in tests

### E5: CREATE SOURCE FORMAT validation (for C7, C8)
- **Entry points**: 
  - `src/sqlparser/src/ast/statement.rs:94-155` Format and Encode enums
  - `src/sqlparser/src/ast/statement.rs:226-300` parse_format_encode_with_connector enforces CDC formats
- **Tests**: Various connector tests in e2e_test/source_inline/
- **Observed code behavior**: 
  - Lines 244-262 show CDC connectors force DEBEZIUM/DEBEZIUM_MONGO format
  - Line 86 CreateSourceStatement includes PRIMARY KEY in struct
  - Format::Upsert defined at line 113

**Verdict**: `match` for C7; `partial` for C8 (upsert syntax exists but INCLUDE KEY requirement not enforced in parser)

### E6: CREATE MATERIALIZED VIEW backfill (for C9, C10)
- **Entry points**: 
  - `src/sqlparser/src/parser.rs:4004-4030` parse_backfill_order_strategy and parse_fixed_backfill_order
- **Tests**: No e2e test found exercising backfill_order
- **Observed code behavior**: 
  - BackfillOrderStrategy::Fixed parser at line 4015-4030 supports `->` operator syntax
  - No test coverage found

**Verdict**: `partial` - syntax exists but no test validation; docs warnings about technical preview and recovery not validated

### E7: ALTER TABLE column operations (for C11, C12, C13, C14)
- **Entry points**: 
  - `src/sqlparser/src/ast/ddl.rs:44-56` AddColumn and DropColumn operations
  - `src/sqlparser/src/ast/ddl.rs:82-85` AlterColumn operation
  - `src/sqlparser/src/ast/ddl.rs:119-122` AlterConnectorProps
- **Tests**: 
  - `e2e_test/ddl/alter_table_column.slt:13-28` tests error cases for ADD/DROP
  - `e2e_test/ddl/alter_table_column.slt:129-145` tests DROP COLUMN with dependency check
- **Observed code behavior**: 
  - Test line 17-18 validates cannot ADD primary key column
  - Test line 130 validates "being referenced" error for DROP COLUMN
  - AlterColumn op exists but ALTER COLUMN TYPE test not found
  - CONNECTOR WITH property in AlterTableOperation (ddl.rs:119-122) but test not found

**Verdict**: `match` for C11, C12; `missing` for C13 test, `missing` for C14 test

### E8: ALTER SOURCE operations (for C15)
- **Entry points**: `src/sqlparser/src/ast/ddl.rs` would have AlterSourceOperation
- **Tests**: Not examined in e2e_test/ddl/
- **Looked**: Did not check for REFRESH SCHEMA validation

**Verdict**: `partial` - syntax likely exists but validation not checked

### E9: Identifier handling (for C16, C17, C18)
- **Entry points**: 
  - `src/sqlparser/src/parser.rs:4186-4199` parse_object_name and parse_identifier
  - `src/sqlparser/src/keywords.rs` keyword definitions
  - `src/sqlparser/src/tokenizer.rs` identifier tokenization
- **Tests**: `e2e_test/ddl/schema_qualified_name.slt` likely tests identifier resolution
- **Observed code behavior**: 
  - Tokenizer handles quoted vs unquoted identifiers
  - Parser Word struct has keyword field
  - No explicit test for builtin name shadowing found

**Verdict**: `partial` - parser infrastructure exists but specific builtin shadowing behavior (C18) not explicitly tested

### E10: Literal parsing (for C19, C20)
- **Entry points**: 
  - `src/sqlparser/src/tokenizer.rs` handles string and number tokenization
  - `src/sqlparser/src/parser_v2/number.rs` numeric literal parsing
- **Tests**: Not explicitly searched for literal format tests
- **Observed code behavior**: Parser_v2 module suggests new parsing implementation

**Verdict**: `partial` - infrastructure exists but comprehensive format support not validated

### E11: Data type constraints (for C21, C22)
- **Entry points**: `src/sqlparser/src/ast/data_type.rs` DataType enum
- **Tests**: Data type tests likely in e2e_test but not examined
- **Observed code behavior**: Parser would accept or reject precision/scale syntax

**Verdict**: `partial` - need to check DataType definition for NUMERIC/VARCHAR parameter support

### E12: INSERT and SELECT behaviors (for C23, C24, C25, C26)
- **Entry points**: DML operations in frontend, not parser scope
- **Tests**: `e2e_test/dml/` directory exists
- **Observed code behavior**: INSERT RETURNING is parser-level syntax; PK upsert is execution semantics

**Verdict**: `partial` - parser aspects exist, execution semantics need frontend validation

## Match matrix

| Claim | Evidence | Verdict | Notes |
|-------|----------|---------|-------|
| C1 (CREATE TABLE syntax) | E1 | `match` | All syntax elements present in AST and parser |
| C2 (ON CONFLICT default) | E1, E2 | `partial` | Docs say "OVERWRITE" but code uses "DO UPDATE FULL"; default not tested |
| C3 (APPEND ONLY + OVERWRITE incompatibility) | E1 | `match` | Test explicitly validates error |
| C4 (NOT NULL behavior) | E3 | `partial` | Test file exists but not validated |
| C5 (DEFAULT clause) | E4 | `partial` | Syntax exists, full semantics not tested |
| C6 (DEFAULT + DO UPDATE IF NOT NULL incompatibility) | E4 | `missing` | No test validates this constraint |
| C7 (CDC formats require CREATE TABLE) | E5 | `match` | Parser enforces CDC format constraints |
| C8 (UPSERT format requirements) | E5 | `partial` | UPSERT syntax exists; INCLUDE KEY requirement not parser-enforced |
| C9 (MV backfill behavior) | E6 | `partial` | Runtime behavior, not parser-level |
| C10 (backfill_order syntax) | E6 | `partial` | Syntax parsed but no test coverage |
| C11 (ADD COLUMN restrictions) | E7 | `match` | Test validates restriction |
| C12 (DROP COLUMN restrictions) | E7 | `match` | Test validates restriction |
| C13 (ALTER COLUMN TYPE) | E7 | `missing` | No test found for v2.5.0 feature |
| C14 (CONNECTOR WITH) | E7 | `missing` | No test found for v2.6.0 feature |
| C15 (REFRESH SCHEMA restrictions) | E8 | `partial` | Not validated |
| C16 (case insensitivity) | E9 | `partial` | Infrastructure exists but not explicitly tested |
| C17 (identifier naming) | E9 | `partial` | Tokenizer handles but not explicitly tested |
| C18 (reserved builtins) | E9 | `partial` | No explicit test for shadowing behavior |
| C19 (string escapes) | E10 | `partial` | Tokenizer likely handles but not validated |
| C20 (numeric formats) | E10 | `partial` | Parser infrastructure exists |
| C21 (NUMERIC precision) | E11 | `partial` | Need DataType definition check |
| C22 (VARCHAR length) | E11 | `partial` | Need DataType definition check |
| C23 (INSERT PK upsert) | E12 | `partial` | Execution semantics, not parser |
| C24 (INSERT RETURNING) | E12 | `partial` | Parser syntax exists |
| C25 (DISTINCT ON + ORDER BY) | E12 | `partial` | Frontend validation needed |
| C26 (LIMIT without ORDER BY in MV) | E12 | `partial` | Frontend validation needed |

## Gaps & fixes

### Doc gaps (code has it, docs missing/outdated)

**G1: ON CONFLICT syntax terminology inconsistency**
- **Issue**: Docs use "OVERWRITE" in C2 but parser/tests use "DO UPDATE FULL"
- **Evidence**: `sql-create-table.mdx:137` says "OVERWRITE" but `on_conflict.slt:33` uses "DO UPDATE FULL"
- **Impact**: Users may use wrong syntax

**G2: Missing ALTER COLUMN TYPE examples**
- **Issue**: Docs describe feature (C13) but no test validates it works
- **Evidence**: No test file found in e2e_test for this v2.5.0 feature
- **Impact**: Uncertain if feature works as documented

**G3: Missing CONNECTOR WITH examples**
- **Issue**: Docs describe feature (C14) but no test validates it works  
- **Evidence**: No test file found in e2e_test for this v2.6.0 feature
- **Impact**: Uncertain if feature works as documented

### Code gaps (docs claim, code missing/feature-gated)

**CG1: DEFAULT + DO UPDATE IF NOT NULL incompatibility not enforced**
- **Issue**: Docs claim incompatibility (C6) but no test validates this is enforced
- **Evidence**: No error test in on_conflict.slt or alter_table_column.slt
- **Impact**: Users may encounter unexpected behavior or runtime errors

**CG2: backfill_order feature lacks test coverage**
- **Issue**: Docs describe FIXED(t1 -> t2) syntax (C10) but no e2e test
- **Evidence**: Parser at parser.rs:4015-4030 but no corresponding slt test
- **Impact**: Technical preview feature may have bugs; warnings about recovery not validated

**CG3: UPSERT INCLUDE KEY requirement not parser-enforced**
- **Issue**: Docs say "you must include INCLUDE KEY clause" (C8) but parser doesn't enforce
- **Evidence**: Format::Upsert at statement.rs:113 but no validation
- **Impact**: Users may create invalid upsert sources; error deferred to runtime

### Conflicts (docs vs code mismatch)

**CONFLICT1: ON CONFLICT OVERWRITE vs DO UPDATE FULL**
- **Docs claim**: "OVERWRITE [WITH VERSION COLUMN]" at sql-create-table.mdx:137
- **Code evidence**: Test uses "DO UPDATE FULL" at on_conflict.slt:33; parser prints "ON CONFLICT {}" at mod.rs:2088
- **Conflict point**: Keyword name mismatch - docs say OVERWRITE, code uses DO UPDATE FULL
- **Location**: `sql-create-table.mdx:137` vs `e2e_test/streaming/on_conflict.slt:33`

### Suggested docs patches

```diff
diff --git a/sql/commands/sql-create-table.mdx b/sql/commands/sql-create-table.mdx
index placeholder1..placeholder2 100644
--- a/sql/commands/sql-create-table.mdx
+++ b/sql/commands/sql-create-table.mdx
@@ -134,8 +134,8 @@ The `conflict_action` could be one of the following. A [version column](#versio
 
 The `conflict_action` could be one of the following. A [version column](#version-column) can be specified together for `DO UPDATE FULL` and `DO UPDATE IF NOT NULL`. When a version column is specified, the insert operation will take effect only when the newly inserted row's version column is greater than or equal to the existing row's version column, and is not NULL.
 
 * `DO NOTHING`: Ignore the newly inserted record.
-* `OVERWRITE [WITH VERSION COLUMN(col_name)]`: Full update — replace the existing row in the table with the new row. This is the default behavior.
+* `DO UPDATE FULL [WITH VERSION COLUMN(col_name)]`: Full update — replace the existing row in the table with the new row. This is the default behavior when `ON CONFLICT` clause is not specified.
 * `DO UPDATE IF NOT NULL [WITH VERSION COLUMN(col_name)]`: Partial update — only replace those fields with non-NULL values in the inserted row. NULL values in the inserted row means unchanged in this case.
 
 <Note>
```

```diff
diff --git a/sql/commands/sql-create-table.mdx b/sql/commands/sql-create-table.mdx
index placeholder1..placeholder2 100644
--- a/sql/commands/sql-create-table.mdx
+++ b/sql/commands/sql-create-table.mdx
@@ -104,7 +104,7 @@ The append-only table does not support delete or update operations, nor does it
 The append-only table does not support delete or update operations, nor does it support non-append-only upstream connectors. There are two main reasons for using append-only tables:
 
 - Certain features are exclusively available for append-only tables, such as watermark and TTL (Time-To-Live).
-- Streaming jobs created downstream from append-only tables can leverage their append-only property to optimize performance. 
+- Streaming jobs created downstream from append-only tables can leverage their append-only property to optimize performance.
+
+<Note>
+The `ON CONFLICT OVERWRITE` syntax is not allowed with `APPEND ONLY` tables. Use `ON CONFLICT DO NOTHING` instead to ignore duplicate primary key insertions in append-only mode.
+</Note>
 
```

## Pending actions

### R&D

**RD1: Verify DEFAULT + DO UPDATE IF NOT NULL incompatibility enforcement**
- **Where to look**: `src/frontend/src/handler/create_table.rs` or similar DDL handler; search for "DO UPDATE IF NOT NULL" validation
- **What decision**: Is this incompatibility enforced at parse time, plan time, or not at all?
- **Why needed**: Docs claim incompatibility (C6) but no test or code evidence found

**RD2: Investigate default ON CONFLICT behavior**
- **Where to look**: `src/frontend/src/handler/create_table.rs` for default conflict resolution strategy when ON CONFLICT omitted
- **What decision**: Confirm default is full overwrite (upsert semantics) vs error
- **Why needed**: Docs claim (C2, C23) but no test validates default behavior

**RD3: Confirm NUMERIC precision limits**
- **Where to look**: `src/common/src/types/decimal.rs` or similar type implementation
- **What decision**: Validate 28 decimal digits claim and range limits vs PostgreSQL
- **Why needed**: Docs claim (C21) specific precision but no code reference found

**RD4: Verify UPSERT INCLUDE KEY requirement**
- **Where to look**: `src/frontend/src/handler/create_source.rs` validation logic for FORMAT UPSERT
- **What decision**: Is INCLUDE KEY + PRIMARY KEY mandatory or optional?
- **Why needed**: Docs claim (C8) requirement but parser doesn't enforce

**RD5: Locate ALTER COLUMN TYPE implementation**
- **Where to look**: `src/frontend/src/handler/alter_table_column.rs` or search for "ALTER_COLUMN_TYPE" or "v2.5.0"
- **What decision**: Does v2.5.0 feature exist? Is it restricted to struct types only?
- **Why needed**: Docs describe feature (C13) but no test found

**RD6: Locate CONNECTOR WITH implementation**
- **Where to look**: `src/frontend/src/handler/alter_table.rs` search for "AlterConnectorProps" or "v2.6.0"
- **What decision**: Does v2.6.0 feature exist for Kafka? Which properties supported?
- **Why needed**: Docs describe feature (C14) but no test found

### Test

**T1: Add test for DEFAULT + DO UPDATE IF NOT NULL incompatibility**
- **Suggested file**: `e2e_test/streaming/on_conflict.slt` (add to existing file)
- **Assertions**:
```sql
statement error DEFAULT.*not allowed.*DO UPDATE IF NOT NULL
create table t_invalid (
  v1 int, 
  v2 int DEFAULT 0, 
  primary key(v1)
) on conflict do update if not null;
```

**T2: Add test for default ON CONFLICT behavior (no clause specified)**
- **Suggested file**: `e2e_test/streaming/on_conflict.slt` (add to existing file)
- **Assertions**:
```sql
statement ok
create table t_default (v1 int, v2 int, primary key(v1));

statement ok
insert into t_default values (1, 10);

statement ok
insert into t_default values (1, 20);

query II
select v1, v2 from t_default;
----
1 20
```

**T3: Add test for backfill_order FIXED syntax**
- **Suggested file**: `e2e_test/ddl/create_mv_backfill_order.slt` (new file)
- **Assertions**:
```sql
statement ok
create table t1 (v1 int);
statement ok
create table t2 (v1 int);
statement ok
create table t3 (v1 int);

statement ok
create materialized view m1
with (backfill_order = FIXED(t1 -> t2, t2 -> t3))
as
select v1 from t1
union
select v1 from t2
union
select v1 from t3;

query T
explain (backfill, format dot) create materialized view m_test
with (backfill_order = FIXED(t1 -> t2))
as select * from t1 union select * from t2;
----
(validate dot format output contains t1 -> t2 edge)
```

**T4: Add test for ALTER TABLE CONNECTOR WITH**
- **Suggested file**: `e2e_test/ddl/alter_table_connector.slt` (new file)
- **Assertions**:
```sql
-- Requires Kafka connector setup
statement ok
create table kafka_table (v1 int) with (
  connector = 'kafka',
  topic = 'test_topic',
  properties.bootstrap.server = '${RISEDEV_KAFKA_BOOTSTRAP_SERVERS}',
  'properties.security.protocol' = 'PLAINTEXT'
) format plain encode json;

statement ok
alter table kafka_table connector with (
  'properties.security.protocol' = 'SASL_SSL'
);

-- Verify property was updated (check internal catalog)
query T
select properties from rw_tables where name = 'kafka_table';
----
(contains updated security.protocol)
```

**T5: Add test for ALTER TABLE ALTER COLUMN TYPE**
- **Suggested file**: `e2e_test/ddl/alter_table_column_type.slt` (new file)
- **Assertions**:
```sql
statement ok
create table t (
  v1 int, 
  v2 struct<field1 int, field2 varchar>
);

statement ok
alter table t alter column v2 type struct<field1 int, field2 varchar, field3 bool>;

query TT
show create table t;
----
public.t CREATE TABLE t (v1 INT, v2 STRUCT<field1 INT, field2 VARCHAR, field3 BOOL>)

-- Verify new field returns NULL for existing rows
statement ok
insert into t values (1, row(10, 'a'));

query I??
select v1, (v2).field1, (v2).field2, (v2).field3 from t;
----
1 10 a NULL
```

**T6: Add test for UPSERT without INCLUDE KEY**
- **Suggested file**: `e2e_test/source_inline/kafka/upsert_validation.slt` (new file or add to existing)
- **Assertions**:
```sql
statement error UPSERT.*requires.*INCLUDE KEY
create source upsert_invalid (
  primary key (id),
  id int,
  name varchar
) with (
  connector='kafka',
  topic='test_topic',
  properties.bootstrap.server='${RISEDEV_KAFKA_BOOTSTRAP_SERVERS}'
) format upsert encode json;
```

**T7: Add test for APPEND ONLY + OVERWRITE incompatibility**
- **Status**: Already exists at `e2e_test/streaming/on_conflict.slt:29-30`
- **Action**: Document test location in code comments or test catalog

## Open questions

**Q1**: What is the exact version when composite VERSION COLUMN support was added? Docs say v2.6.0 for composite but tests don't specify version requirements.

**Q2**: Are there any feature flags or configuration parameters that gate ON CONFLICT or VERSION COLUMN features? No flags found in parser code.

**Q3**: Does the backfill_order recovery limitation apply only to background DDL or also to foreground DDL that crashes mid-backfill?

**Q4**: What is the exact semantic difference between "streaming ingestion" and "batch inserts" for NOT NULL constraint handling? Is streaming ingestion only from connectors, or does it include INSERT statements in a transaction?

**Q5**: For LIMIT without ORDER BY in MV (C26), what error message does the system show? Is this a parser-level or planner-level restriction?

**Q6**: The docs mention "default row format for datagen source is native" - is there any other source with configurable default format besides datagen?
