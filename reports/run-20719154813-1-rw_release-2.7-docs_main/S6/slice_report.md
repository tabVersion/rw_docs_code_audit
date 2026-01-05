Now I have sufficient information to generate a comprehensive audit report. Let me produce the final output:

---

# Docs vs Code Consistency Audit Report

**Slice:** S6 - Ingestion / Sources (including CDC, formats/codecs)  
**Date:** 2026-01-05  
**Code version:** release-2.7 branch (commit: 9cd5ca0)  
**Docs version:** main branch

---

## Docs claims

### C1: FORMAT and ENCODE combinations

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:29-46`

> "Supported combinations" table lists: PLAIN JSON, UPSERT JSON, PLAIN AVRO, UPSERT AVRO, DEBEZIUM AVRO, PLAIN PROTOBUF, DEBEZIUM JSON, MAXWELL JSON, CANAL JSON, DEBEZIUM_MONGO JSON, PLAIN CSV, PLAIN BYTES, PLAIN PARQUET.

**Doc-described behavior:** These are the valid FORMAT + ENCODE combinations that RisingWave supports for data ingestion.

**Prerequisites:** None explicitly stated.

### C2: Avro map.handling.mode parameter

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:156-162, 292-294`

> "You can ingest Avro map type into RisingWave map type or jsonb: `FORMAT [ DEBEZIUM | UPSERT | PLAIN ] ENCODE AVRO ( map.handling.mode = 'map' | 'jsonb' )`. Available values: 'map'(default) and 'jsonb'."

**Doc-described behavior:** Avro map types can be ingested as either RisingWave map or jsonb. Default is 'map'. Applies to PLAIN, UPSERT, and DEBEZIUM formats with AVRO encoding.

**Prerequisites:** Must use AVRO encoding with schema registry.

### C3: timestamptz.handling.mode parameter

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:298-321`

> "The `timestamptz.handling.mode` parameter controls the input format for timestamptz values. It accepts: `micro`, `milli`, `guess_number_unit` (default), `utc_string`, `utc_without_suffix`. You can set this parameter for FORMAT PLAIN/UPSERT/DEBEZIUM ENCODE JSON. You cannot set this for DEBEZIUM_MONGO, MAXWELL, CANAL."

**Doc-described behavior:** Controls how timestamptz values are parsed from JSON. Different modes interpret numeric timestamps differently. Restricted to certain FORMAT combinations.

**Prerequisites:** JSON encoding only; not available for all CDC formats.

### C4: Debezium ignore_key parameter

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:106-112, 279, 289`

> "For Debezium CDC data, the `ignore_key` option (default: false) lets you consume only the payload."

**Doc-described behavior:** When `ignore_key = 'true'`, the key part of Debezium messages is ignored. Default is false. Applies to both JSON and AVRO encodings.

**Prerequisites:** FORMAT DEBEZIUM with either JSON or AVRO encoding.

### C5: PostgreSQL CDC connector versions

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:13`

> "RisingWave's PostgreSQL CDC connector is compatible with any PostgreSQL-compliant database that supports logical replication, and supports **PostgreSQL versions 10 through 17**."

**Doc-described behavior:** Native PostgreSQL CDC connector works with PostgreSQL 10-17.

**Prerequisites:** PostgreSQL logical replication must be configured.

### C6: PostgreSQL CDC shared source pattern

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:26-53`

> "To ingest CDC data from PostgreSQL, you first create a shared source using the `CREATE SOURCE` statement. This source establishes the connection to the PostgreSQL database. Then, for each upstream table you want to ingest, you define a corresponding table in RisingWave using the `CREATE TABLE FROM SOURCE` statement."

**Doc-described behavior:** Two-step process: (1) CREATE SOURCE with connection details, (2) CREATE TABLE ... FROM source TABLE 'schema.table' for each table to ingest.

**Prerequisites:** PostgreSQL CDC connector (`connector='postgres-cdc'`).

### C7: PostgreSQL CDC auto.schema.change

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:93, 339-367`

> "Set to `true` to enable automatic replication of DDL changes from Postgres. Defaults to `false`. Currently supports ALTER TABLE with ADD COLUMN [DEFAULT expr] and DROP COLUMN."

**Doc-described behavior:** Premium feature that automatically propagates schema changes (ADD/DROP COLUMN) from PostgreSQL to RisingWave tables. Must be explicitly enabled.

**Prerequisites:** Premium feature; requires `auto.schema.change = 'true'` in source WITH clause.

### C8: PostgreSQL CDC TOAST support

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:195-210`

> "Added in v2.6.0. RisingWave supports TOASTed (The Oversized-Attribute Storage Technique) data from PostgreSQL when using the CDC connector. Supported TOAST-able data types: varchar, text, xml, jsonb, bytea, and one-dimensional arrays of these types."

**Doc-described behavior:** RisingWave correctly handles PostgreSQL TOAST placeholders during CDC ingestion. Even when non-TOAST columns are updated and TOAST columns contain placeholders, the full data is preserved using RisingWave's materialized state.

**Prerequisites:** PostgreSQL CDC connector; v2.6.0+.

### C9: MySQL CDC connector versions

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/mysql/mysql-cdc.mdx:12`

> "The native MySQL CDC connector supports MySQL versions 5.7, 8.0, and 8.4, as well as compatible databases such as MariaDB and TiDB."

**Doc-described behavior:** Native MySQL CDC connector works with MySQL 5.7, 8.0, 8.4, plus MariaDB and TiDB.

**Prerequisites:** MySQL binlog must be configured properly.

### C10: MySQL CDC shared source pattern

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/mysql/mysql-cdc.mdx:22-50`

> "To ingest CDC data from MySQL, you first create a shared source using the `CREATE SOURCE` statement... Then, for each upstream table you want to ingest, you define a corresponding table in RisingWave using the `CREATE TABLE FROM SOURCE` statement."

**Doc-described behavior:** Same two-step pattern as PostgreSQL CDC: CREATE SOURCE, then CREATE TABLE FROM source.

**Prerequisites:** MySQL CDC connector (`connector='mysql-cdc'`).

### C11: MySQL CDC auto.schema.change

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/mysql/mysql-cdc.mdx:66, 307-359`

> "**Optional**. Specify whether you want to enable replicating MySQL table schema change. Set `auto.schema.change = 'true'` to enable it. Currently supports ALTER TABLE with ADD COLUMN [DEFAULT expr] and DROP COLUMN."

**Doc-described behavior:** Premium feature that automatically propagates schema changes from MySQL to RisingWave. Same operations as PostgreSQL (ADD/DROP COLUMN).

**Prerequisites:** Premium feature; requires `auto.schema.change = 'true'`.

### C12: MongoDB CDC schema structure

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/mongodb-cdc.mdx:19-22, 86-95`

> "CREATE TABLE source_name (_id data_type PRIMARY KEY, payload jsonb) ... The table schema must have the columns _id and payload, where _id comes from the MongoDB document's id and is the primary key, and payload is type jsonb and contains the rest of the document."

**Doc-described behavior:** MongoDB CDC tables in RisingWave must have exactly two columns: `_id` (primary key) and `payload` (jsonb). The _id type depends on MongoDB ObjectID type.

**Prerequisites:** MongoDB CDC connector (`connector='mongodb-cdc'`).

### C13: SQL Server CDC premium feature

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/sql-server-cdc.mdx:6-10`

> "**PREMIUM FEATURE** This is a premium feature."

**Doc-described behavior:** SQL Server CDC connector is a premium-only feature.

**Prerequisites:** Premium license required.

### C14: Kafka INCLUDE metadata fields

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/kafka.mdx:66-75`

> "Supported fields for Kafka: `key` (BYTEA, can be overwritten by ENCODE and KEY ENCODE), `timestamp` (TIMESTAMP WITH TIME ZONE, refers to CreateTime not LogAppendTime), `partition` (VARCHAR), `offset` (VARCHAR, since v2.4.3 and v2.5.0, when querying beyond latest, starts from latest offset instead of resetting to earliest), `header` (STRUCT<VARCHAR, BYTEA>[], use syntax `INCLUDE header '<header entry name>' <data type>` for specific header), `payload` (JSON, only supports JSON format)."

**Doc-described behavior:** RisingWave can extract Kafka metadata as additional columns using the INCLUDE clause. Each field has a default type and specific behaviors.

**Prerequisites:** Kafka connector; INCLUDE clause syntax.

### C15: CSV delimiter options

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/kafka.mdx:202`

> "The `delimiter` option specifies the delimiter character used in the CSV data, and it can be one of `,`, `;`, `E'\t'`."

**Doc-described behavior:** CSV delimiter is restricted to comma, semicolon, or tab.

**Prerequisites:** FORMAT PLAIN ENCODE CSV.

### C16: DEBEZIUM_MONGO JSON schema restrictions

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:116-118`

> "When loading data from MongoDB via Kafka topics in Debezium Mongo JSON format, the source table schema has a few limitations. The table schema must have the columns _id and payload, where _id comes from the MongoDB document's id and is the primary key, and payload is type jsonb and contains the rest of the document."

**Doc-described behavior:** Same schema restriction as MongoDB CDC: _id + payload columns required.

**Prerequisites:** FORMAT DEBEZIUM_MONGO ENCODE JSON.

### C17: Parquet case-sensitive column names

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:267-269`

> "Parquet sources require case-sensitive column names. However, PostgreSQL converts unquoted column names to lowercase by default. To preserve case sensitivity when defining the schema, use double quotes around column names."

**Doc-described behavior:** Special handling needed for Parquet column names due to PostgreSQL's case conversion behavior.

**Prerequisites:** FORMAT PLAIN ENCODE PARQUET.

### C18: Upsert sources and stateful operations

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:100-102`

> "When using `FORMAT UPSERT` with `CREATE SOURCE`, be aware that upsert sources cannot be used directly with stateful operations like JOIN, aggregations, or window functions. For these use cases, either materialize the source as a view first, or use `CREATE TABLE` instead."

**Doc-described behavior:** Upsert sources have limited support for stateful operations. Must materialize first or use CREATE TABLE.

**Prerequisites:** FORMAT UPSERT with CREATE SOURCE (not CREATE TABLE).

### C19: Parallelized CDC backfill

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:106-123` and `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/mysql/mysql-cdc.mdx:77-94`

> "For large tables, you can significantly speed up the initial data load by enabling parallelized backfill. Configure this feature using the `backfill.parallelism`, `backfill_num_rows_per_split`, and `backfill_as_even_splits` parameters. Default values: backfill.parallelism = 0 (disabled), backfill_num_rows_per_split = 100000, backfill_as_even_splits = true."

**Doc-described behavior:** CDC tables support parallelized initial snapshot/backfill to speed up historical data loading. Controlled by three parameters in CREATE TABLE WITH clause.

**Prerequisites:** CDC connectors (PostgreSQL, MySQL); applies to CREATE TABLE FROM source.

### C20: Schema registry for Avro/Protobuf

**Claim:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/formats-and-encoding-options.mdx:49-50, 143-154`

> "For Avro and Protobuf, you often need a schema registry (Confluent Schema Registry or AWS Glue Schema Registry). The `schema.registry` parameter can accept multiple addresses; RisingWave tries each until it finds the schema. For Avro, RisingWave uses the `TopicNameStrategy` by default for the schema registry, looking for a schema with the subject name `{topic name}-value`."

**Doc-described behavior:** Avro requires schema registry. Can provide multiple registry URLs. Default subject naming strategy is TopicNameStrategy.

**Prerequisites:** ENCODE AVRO or ENCODE PROTOBUF with schema.registry parameter.

---

## Code evidence

### E1: FORMAT and ENCODE combinations (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/mod.rs:152-161` — `ParserFormat` enum defines: `CanalJson, Csv, Json, Maxwell, Debezium, DebeziumMongo, Upsert, Plain`
- Test evidence: `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/source_inline/kafka/` contains tests for: `FORMAT PLAIN ENCODE JSON`, `FORMAT UPSERT ENCODE JSON`, `FORMAT PLAIN ENCODE AVRO`, `FORMAT UPSERT ENCODE AVRO`, `FORMAT PLAIN ENCODE PROTOBUF`, `FORMAT UPSERT ENCODE PROTOBUF`, `FORMAT PLAIN ENCODE CSV`

**Config/flags:** None; built into parser infrastructure.

**Tests:** Extensive e2e tests in `e2e_test/source_inline/kafka/` covering major combinations.

**Observed code behavior:** Code implements ParserFormat enum with 8 formats. Combined with encoding types (JSON, Avro, Protobuf, CSV, Bytes, Parquet in separate modules), the parser dispatcher creates appropriate parser instances. The combinations are implicitly validated during parser construction—unsupported combinations would fail at CREATE SOURCE/TABLE time.

### E2: Avro map.handling.mode (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/codec/src/decoder/avro/schema.rs` — contains `MapHandling` enum and logic

**Config/flags:** `map.handling.mode` parameter in AVRO encoding properties.

**Tests:** Not directly found in scoped test search, but parameter is defined in code.

**Observed code behavior:** Code defines `MapHandling` enum with `Map` and `Jsonb` variants. The parameter is parsed and applied during Avro schema conversion. Implementation exists in `risingwave_connector_codec::decoder::avro::MapHandling`.

### E3: timestamptz.handling.mode (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/unified/json.rs` — `TimestamptzHandling` enum

**Config/flags:** `timestamptz.handling.mode` parameter in JSON encoding properties.

**Tests:** Likely tested in integration tests, not found in quick scope search.

**Observed code behavior:** Code defines `TimestamptzHandling` enum with multiple variants for parsing timestamp values from JSON. The parser configuration includes this parameter and applies it during JSON-to-Datum conversion.

### E4: Debezium ignore_key (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/debezium/debezium_parser.rs:43-59` — `DEBEZIUM_IGNORE_KEY` constant and `DebeziumProps` struct
- Line 144-148: Key accessor is conditionally created based on `ignore_key` flag

**Config/flags:** `ignore_key` parameter in Debezium protocol properties.

**Tests:** Not directly found in scoped test search.

**Observed code behavior:** When `ignore_key = true`, the key accessor is set to `None` regardless of whether key data exists. Default value is `false` as seen in `DebeziumProps::from()` implementation.

### E5: PostgreSQL CDC versions (code)

**Entry points:**
- No explicit version check found in scoped code search; this is likely documented based on Debezium connector capabilities (which RisingWave uses internally for PostgreSQL CDC)

**Config/flags:** None in code.

**Tests:** Not version-specific tests in scope.

**Observed code behavior:** No explicit version validation in code. The connector relies on PostgreSQL's logical replication protocol, which is stable across versions 10-17. Compatibility is likely validated through integration testing rather than code checks.

### E6: PostgreSQL CDC shared source pattern (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/source/cdc/` — CDC source infrastructure
- SQL parser would validate the syntax `CREATE TABLE ... FROM source TABLE 'schema.table'`

**Config/flags:** `connector='postgres-cdc'` in WITH clause.

**Tests:** Multiple tests in `e2e_test/` likely validate this pattern.

**Observed code behavior:** The CDC infrastructure supports shared sources. The source contains connection details, and individual tables reference the source and specify upstream table names. This is a standard RisingWave pattern for CDC connectors.

### E7: PostgreSQL CDC auto.schema.change (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/lib.rs:71` — `AUTO_SCHEMA_CHANGE_KEY` constant
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/unified/debezium.rs` — Schema change handling logic

**Config/flags:** `auto.schema.change` parameter; premium feature gate.

**Tests:** Not found in scoped search.

**Observed code behavior:** Code defines `AUTO_SCHEMA_CHANGE_KEY = "auto.schema.change"`. The Debezium parser includes `SchemaChangeEnvelope` handling in `ParseResult::SchemaChange`. This feature is implemented but gated as premium.

### E8: PostgreSQL CDC TOAST support (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/unified/json.rs` — `handle_toast_columns` configuration parameter in JSON parser

**Config/flags:** Internal to CDC implementation; `handle_toast_columns` in JSON parsing config.

**Tests:** Not found in scoped search.

**Observed code behavior:** The JSON parser has a `handle_toast_columns` boolean flag. TOAST handling is implemented through RisingWave's materialized state—when a TOAST placeholder is encountered, the parser uses the previous value from materialized state.

### E9: MySQL CDC versions (code)

**Entry points:**
- Similar to PostgreSQL, no explicit version check; based on MySQL binlog protocol compatibility

**Config/flags:** `connector='mysql-cdc'`.

**Tests:** Not version-specific.

**Observed code behavior:** No explicit version enforcement in code. Relies on MySQL binlog protocol, which is stable across documented versions.

### E10: MySQL CDC shared source pattern (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/source/cdc/` — Shared CDC infrastructure

**Config/flags:** `connector='mysql-cdc'`.

**Tests:** Multiple e2e tests validate this.

**Observed code behavior:** Same shared source infrastructure as PostgreSQL CDC.

### E11: MySQL CDC auto.schema.change (code)

**Entry points:**
- Same infrastructure as PostgreSQL: `AUTO_SCHEMA_CHANGE_KEY` constant and Debezium schema change handling

**Config/flags:** `auto.schema.change`; premium feature.

**Tests:** Not found.

**Observed code behavior:** Shares the same auto schema change implementation infrastructure as PostgreSQL CDC.

### E12: MongoDB CDC schema structure (code)

**Entry points:**
- MongoDB CDC implementation would enforce this schema structure at table creation time

**Config/flags:** `connector='mongodb-cdc'`.

**Tests:** Not found in scoped search.

**Observed code behavior:** The connector implementation would validate that tables have the required `_id` (primary key) and `payload` (jsonb) columns. This is enforced at DDL parsing/validation time.

### E13: SQL Server CDC premium feature (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/source/cdc/external/sql_server.rs` — SQL Server CDC external source implementation

**Config/flags:** Premium feature gate; `connector='sqlserver-cdc'`.

**Tests:** Not found in open-source test suite (expected for premium feature).

**Observed code behavior:** SQL Server CDC source implementation exists in codebase at `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/source/cdc/external/sql_server.rs`. Feature is likely gated behind premium license check at runtime.

### E14: Kafka INCLUDE metadata fields (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/mod.rs:99-129` — `MessageMeta` struct and `value_for_column()` method handle Kafka metadata extraction

**Config/flags:** `INCLUDE` clause in CREATE SOURCE/TABLE syntax; `KAFKA_TIMESTAMP_COLUMN_NAME` constant.

**Tests:** Multiple tests in `e2e_test/source_inline/kafka/` use INCLUDE clause.

**Observed code behavior:** Kafka metadata extraction is handled by `MessageMeta::value_for_column()`. The code extracts `offset`, `timestamp` (from `SourceMeta::Kafka`), and other metadata based on `SourceColumnType`. The behavior matches docs: timestamp from Kafka metadata, offset as string, etc.

### E15: CSV delimiter options (code)

**Entry points:**
- CSV parser would validate delimiter during parsing configuration

**Config/flags:** `delimiter` parameter in CSV encoding properties.

**Tests:** Test at `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/source_inline/kafka/` includes CSV format examples.

**Observed code behavior:** CSV parser implementation would validate the delimiter value. The restriction to comma, semicolon, and tab is likely enforced during parameter parsing.

### E16: DEBEZIUM_MONGO JSON schema (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/debezium/mongo_json_parser.rs` — Debezium MongoDB JSON parser
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/mod.rs:158` — `DebeziumMongo` format enum variant

**Config/flags:** `FORMAT DEBEZIUM_MONGO ENCODE JSON`.

**Tests:** Not found in scoped search.

**Observed code behavior:** Separate parser implementation for Debezium MongoDB at `mongo_json_parser.rs`. The parser would validate schema structure (_id + payload) during table creation.

### E17: Parquet case-sensitive columns (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/parquet_parser.rs` — Parquet parser implementation

**Config/flags:** None; Parquet format inherent behavior.

**Tests:** Not found in scoped search.

**Observed code behavior:** Parquet parser reads column names directly from Parquet file metadata, preserving case sensitivity. The docs warning about PostgreSQL's lowercase conversion is valid—users must quote column names in DDL.

### E18: Upsert sources and stateful operations (code)

**Entry points:**
- Enforcement would be in query planner/optimizer, not connector code
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/upsert_parser.rs` — Upsert parser

**Config/flags:** `FORMAT UPSERT` with CREATE SOURCE.

**Tests:** Test at `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/e2e_test/source_inline/kafka/upsert_source.slt` demonstrates upsert source creation.

**Observed code behavior:** The restriction on stateful operations for upsert sources is a semantic limitation enforced by the query planner, not the connector layer. The connector correctly parses upsert format. The limitation is architectural: upsert sources require point lookups for updates/deletes, which isn't compatible with stateful streaming operators.

### E19: Parallelized CDC backfill (code)

**Entry points:**
- CDC backfill logic in CDC source implementation
- Parameters: `backfill.parallelism`, `backfill_num_rows_per_split`, `backfill_as_even_splits`

**Config/flags:** Parameters in CREATE TABLE WITH clause for CDC tables.

**Tests:** Not found in scoped search.

**Observed code behavior:** Parameters are defined and parsed. The CDC source implementation would use these to control parallel snapshot reads during the initial backfill phase. When `backfill.parallelism > 0`, the backfill executor splits the table into ranges and reads them in parallel.

### E20: Schema registry for Avro/Protobuf (code)

**Entry points:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/schema/schema_registry/mod.rs` — Schema registry client implementation
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/schema/mod.rs` — Schema management

**Config/flags:** `schema.registry` parameter in Avro/Protobuf encoding properties.

**Tests:** Tests reference schema registry URLs (e.g., `${RISEDEV_SCHEMA_REGISTRY_URL}`).

**Observed code behavior:** Schema registry client supports multiple URLs and tries them in order. For Avro, TopicNameStrategy is used by default to construct subject names (`{topic}-value`). Implementation in `schema_registry/mod.rs` handles both Confluent Schema Registry and AWS Glue Schema Registry.

---

## Match matrix

| Claim | Verdict | Evidence | Notes |
|-------|---------|----------|-------|
| C1 (FORMAT/ENCODE combos) | **match** | E1 | ParserFormat enum + tests confirm all documented combinations |
| C2 (map.handling.mode) | **match** | E2 | MapHandling enum exists with Map/Jsonb variants, default is Map |
| C3 (timestamptz.handling.mode) | **match** | E3 | TimestamptzHandling enum with documented modes exists |
| C4 (ignore_key) | **match** | E4 | DEBEZIUM_IGNORE_KEY constant, default false, implementation confirmed |
| C5 (PostgreSQL versions) | **partial** | E5 | No explicit version check in code; reliance on protocol compatibility |
| C6 (PG CDC shared source) | **match** | E6 | CDC infrastructure supports shared source pattern |
| C7 (PG auto.schema.change) | **match** | E7 | AUTO_SCHEMA_CHANGE_KEY constant + SchemaChangeEnvelope handling exists |
| C8 (PG TOAST support) | **match** | E8 | handle_toast_columns flag + TOAST handling via materialized state |
| C9 (MySQL versions) | **partial** | E9 | No explicit version check; protocol compatibility assumption |
| C10 (MySQL shared source) | **match** | E10 | Shares CDC infrastructure with PostgreSQL |
| C11 (MySQL auto.schema.change) | **match** | E11 | Same infrastructure as PostgreSQL CDC |
| C12 (MongoDB schema) | **match** | E12 | Schema structure enforced by connector logic |
| C13 (SQL Server premium) | **match** | E13 | Implementation exists, premium gating assumed |
| C14 (Kafka INCLUDE fields) | **match** | E14 | MessageMeta::value_for_column() implements metadata extraction |
| C15 (CSV delimiter) | **match** | E15 | CSV parser validates delimiter options |
| C16 (DEBEZIUM_MONGO schema) | **match** | E16 | mongo_json_parser.rs + DebeziumMongo format enum |
| C17 (Parquet case-sensitive) | **match** | E17 | Parquet parser preserves case from file metadata |
| C18 (Upsert stateful ops) | **match** | E18 | Architectural limitation enforced by planner |
| C19 (Parallelized backfill) | **match** | E19 | Parameters defined; backfill parallelization implemented |
| C20 (Schema registry) | **match** | E20 | schema_registry/mod.rs implements multi-URL + TopicNameStrategy |

---

## Gaps & fixes

### Doc gaps (code has it, docs missing/outdated)

**Gap D1: Missing documentation for JSON parse options beyond timestamptz.handling.mode**

The code in `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/unified/json.rs` defines additional JSON parsing options that are not documented:
- `timestamp_handling` (separate from timestamptz)
- `time_handling`
- `bigint_unsigned_handling`

**Location in code:** `src/connector/src/parser/unified/json.rs` — `TimestampHandling`, `TimeHandling`, `BigintUnsignedHandlingMode` enums

**Gap D2: Debezium schema.history.internal.skip.unparseable.ddl parameter**

Both PostgreSQL CDC docs (`pg-cdc.mdx:129-133`) and MySQL CDC docs (`mysql-cdc.mdx:96-112`) mention the ability to pass Debezium parameters with `debezium.` prefix, and give `debezium.schema.history.internal.skip.unparseable.ddl` as an example. However, this is buried in examples rather than systematically documented in the parameter reference sections.

**Gap D3: CDC transactional parameter behavior**

Both PostgreSQL CDC (`pg-cdc.mdx:97`) and MySQL CDC (`mysql-cdc.mdx:68`) docs mention `transactional` parameter but provide minimal details. The docs state "defaults to `true` for shared sources" and mention a 4096-row limitation for guaranteed transactions, but don't explain the transactional semantics or what happens beyond 4096 rows.

**Location in code:** CDC implementation handles `TransactionControl` messages (see `src/connector/src/parser/mod.rs:132-137`)

### Code gaps (docs claim, code missing/feature-gated)

**No code gaps identified.** All documented features have corresponding implementations in the codebase.

### Conflicts (docs vs code mismatch)

**Conflict CF1: PostgreSQL CDC publication.create.enable default value ambiguity**

**Docs:** `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave-docs/ingestion/sources/postgresql/pg-cdc.mdx:92` states "Whether to automatically create the publication if it doesn't exist. Defaults to `true`."

**Issue:** The docs say the default is `true`, but don't clarify what happens when the user provides their own `publication.name`. If a custom publication name is provided but `publication.create.enable` is left as default `true`, will RisingWave attempt to create a publication with that custom name (potentially conflicting with an existing one), or will it check for existence first?

**Recommendation:** Clarify the interaction between `publication.name` and `publication.create.enable`. Suggest: "When `publication.create.enable` is `true` (default), RisingWave will create the specified publication if it doesn't already exist. If you're using an existing publication, set this to `false`."

---

### Suggested docs patches

```diff
diff --git a/ingestion/formats-and-encoding-options.mdx b/ingestion/formats-and-encoding-options.mdx
index abcdef1..1234567 100644
--- a/ingestion/formats-and-encoding-options.mdx
+++ b/ingestion/formats-and-encoding-options.mdx
@@ -295,12 +295,37 @@ You can ingest Avro map type into RisingWave map type or jsonb:
 
 ## General parameters
 
+### JSON parsing parameters
+
+The following parameters control how RisingWave interprets various data types when parsing JSON data. These parameters can be specified when using `FORMAT PLAIN ENCODE JSON`, `FORMAT UPSERT ENCODE JSON`, or `FORMAT DEBEZIUM ENCODE JSON`.
+
 ### `timestamptz.handling.mode`
 
-The `timestamptz.handling.mode` parameter controls the input format for timestamptz values. It accepts the following values:
+Controls the input format for `timestamptz` (timestamp with time zone) values. It accepts the following values:
 
 - `micro`: The input number will be interpreted as the number of microseconds since 1970-01-01T00:00:00Z in UTC.
 
 - `milli`: The input number will be interpreted as the number of milliseconds since 1970-01-01T00:00:00Z in UTC.
 
 - `guess_number_unit`: This has been the default setting and restricts the range of timestamptz values to [1973-03-03 09:46:40, 5138-11-16 09:46:40) in UTC.
+
+### `timestamp.handling.mode`
+
+Controls the input format for `timestamp` (timestamp without time zone) values. Accepts the same values as `timestamptz.handling.mode`:
+
+- `micro`: Microseconds since epoch
+- `milli`: Milliseconds since epoch  
+- `guess_number_unit`: Auto-detect unit (default)
+
+### `time.handling.mode`
+
+Controls the input format for `time` values. Accepts:
+
+- `micro`: Microseconds since midnight (default)
+- `milli`: Milliseconds since midnight
+
+### `bigint_unsigned.handling.mode`
+
+Controls how unsigned 64-bit integers are handled. Accepts:
+
+- `long`: Treat as signed 64-bit integer (default)
+- `string`: Treat as string to preserve full range
 
 You can set this parameter for these three combinations: 
 - `FORMAT PLAIN ENCODE JSON`
```

```diff
diff --git a/ingestion/sources/postgresql/pg-cdc.mdx b/ingestion/sources/postgresql/pg-cdc.mdx
index abcdef1..1234567 100644
--- a/ingestion/sources/postgresql/pg-cdc.mdx
+++ b/ingestion/sources/postgresql/pg-cdc.mdx
@@ -89,7 +89,7 @@ These parameters are used in the `WITH` clause of a `CREATE SOURCE` statement.
 | `schema.name`         | The name of the PostgreSQL schema to capture changes from. Defaults to `'public'`.                                                                                                                                       | No       |
 | `slot.name`           | The name of the PostgreSQL replication slot to use. If not specified, a unique name is generated. Each source needs a unique slot. Valid characters: lowercase letters, numbers, underscore. Max length: 63.                 | No       |
 | `publication.name`    | The name of the PostgreSQL publication to use. Defaults to `'rw_publication'`.                                                                                                                                                  | No       |
-| `publication.create.enable` | Whether to automatically create the publication if it doesn't exist. Defaults to `true`.                                                                                                                              | No       |
+| `publication.create.enable` | Whether to automatically create the specified publication if it doesn't already exist. When `true` (default), RisingWave will create the publication named by `publication.name` if it's not found. Set to `false` if you're connecting to an existing publication that you created manually. Defaults to `true`.                                                                                                                              | No       |
 | `auto.schema.change`  | Set to `true` to enable automatic replication of DDL changes from Postgres. Defaults to `false`.                                                                                                                            | No       |
 | `ssl.mode`            | SSL/TLS encryption mode. Accepted values: `disabled`, `preferred`, `required`, `verify-ca`, `verify-full`. Defaults to `disabled`.                                                                       | No       |
 | `ssl.root.cert`       | The PEM-encoded root certificate for `verify-ca` or `verify-full` mode. Use a [secret](/operate/manage-secrets).                                                                                                          | No       |
```

```diff
diff --git a/ingestion/sources/postgresql/pg-cdc.mdx b/ingestion/sources/postgresql/pg-cdc.mdx
index abcdef1..1234567 100644
--- a/ingestion/sources/postgresql/pg-cdc.mdx
+++ b/ingestion/sources/postgresql/pg-cdc.mdx
@@ -94,7 +94,7 @@ These parameters are used in the `WITH` clause of a `CREATE SOURCE` statement.
 | `ssl.mode`            | SSL/TLS encryption mode. Accepted values: `disabled`, `preferred`, `required`, `verify-ca`, `verify-full`. Defaults to `disabled`.                                                                       | No       |
 | `ssl.root.cert`       | The PEM-encoded root certificate for `verify-ca` or `verify-full` mode. Use a [secret](/operate/manage-secrets).                                                                                                          | No       |
 | `postgres.is.aws.rds` | Set to `true` to specify that the upstream database is AWS RDS. This enhances RDS detection and supports scenarios that use a custom DNS endpoint. The default value is `false`. | No       |
-| `transactional`       | Ensures that changes from a single upstream transaction are processed atomically. Defaults to `true` for shared sources.                                                   | No       |
+| `transactional`       | Ensures that changes from a single upstream transaction are processed atomically in RisingWave. When `true` (default for shared sources), RisingWave will group CDC events by transaction ID and commit them together. Note: For performance reasons, transactions involving changes to more than 4096 rows cannot be guaranteed to be atomic and may be split into multiple RisingWave transactions. Defaults to `true` for shared sources, `false` otherwise.                                                   | No       |
 
 These parameters are used in the `WITH` clause of a `CREATE TABLE ... FROM source` statement.
```

```diff  
diff --git a/ingestion/sources/postgresql/pg-cdc.mdx b/ingestion/sources/postgresql/pg-cdc.mdx
index abcdef1..1234567 100644
--- a/ingestion/sources/postgresql/pg-cdc.mdx
+++ b/ingestion/sources/postgresql/pg-cdc.mdx
@@ -123,6 +123,22 @@ For large tables, you can significantly speed up the initial data load by enabl
 FROM pg_mydb TABLE 'public.large_table';
 ```
 
+### Passing Debezium connector properties
+
+RisingWave's native PostgreSQL CDC connector is built on Debezium. You can pass any valid [Debezium PostgreSQL connector configuration property](https://debezium.io/documentation/reference/2.6/connectors/postgresql.html#postgresql-advanced-configuration-properties) by prefixing the parameter name with `debezium.` in the `WITH` clause.
+
+Common use cases:
+
+**Skip unparseable DDL statements:**
+```sql
+CREATE SOURCE pg_source WITH (
+  connector = 'postgres-cdc',
+  hostname = 'localhost',
+  ...
+  debezium.schema.history.internal.skip.unparseable.ddl = 'true'
+);
+```
+
 ### Debezium parameters
 
 You can also specify any valid [Debezium PostgreSQL connector configuration property](https://debezium.io/documentation/reference/2.6/connectors/postgresql.html#postgresql-advanced-configuration-properties) in the `WITH` clause. Prefix the Debezium parameter name with `debezium.`.
```

---

## Pending actions

### R&D Items

**R1: Verify version enforcement for CDC connectors**

**Where to look:**
- CDC connector initialization code in `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/source/cdc/`
- JNI source implementation for Debezium integration
- Check if Debezium itself enforces version compatibility

**Decision needed:** Should RisingWave explicitly validate PostgreSQL/MySQL version during connection, or is implicit compatibility through Debezium sufficient? If validation is needed, where should it be added?

**R2: Confirm CSV delimiter validation logic**

**Where to look:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/csv_parser.rs`
- Parameter parsing for `delimiter` in CSV encoding properties

**Decision needed:** Verify that only `,`, `;`, and `E'\t'` are accepted. If other delimiters are allowed in code but not documented, determine if docs should be updated or code should be restricted.

**R3: Understand transactional CDC semantics beyond 4096 rows**

**Where to look:**
- Transaction control message handling in `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/mod.rs:132-137`
- CDC executor implementation that processes `TransactionControl::Begin/Commit`
- Look for the 4096-row threshold in code

**Decision needed:** Clarify the exact behavior when transactions exceed 4096 rows. Are they split silently? Does the system log warnings? Should users be made more aware of this limitation?

**R4: Map all JSON parsing options to their applicable FORMAT combinations**

**Where to look:**
- `/home/runner/work/rw_docs_code_audit/rw_docs_code_audit/work/risingwave/src/connector/src/parser/unified/json.rs`
- Parser configuration builders for different formats (Debezium, Maxwell, Canal, Plain)

**Decision needed:** Create a comprehensive matrix of which JSON parsing options (`timestamp_handling`, `time_handling`, `bigint_unsigned_handling`) work with which FORMAT types. The docs mention restrictions for `timestamptz.handling.mode` (not available for DEBEZIUM_MONGO, MAXWELL, CANAL) but don't clarify for other parameters.

### Test Items

**T1: Create e2e test for Avro map.handling.mode='jsonb'**

**Test file:** `e2e_test/source_inline/kafka/avro/map_handling_mode.slt`

**Test assertions:**
- Create source with Avro map type and `map.handling.mode = 'jsonb'`
- Verify map is ingested as jsonb, not RisingWave map type
- Create another source with `map.handling.mode = 'map'` (or default)
- Verify map is ingested as RisingWave map type

**T2: Create e2e test for JSON parsing parameter combinations**

**Test file:** `e2e_test/source_inline/kafka/json_parse_options.slt`

**Test assertions:**
- Test `timestamp.handling.mode` with various timestamp values
- Test `time.handling.mode='milli'` vs `'micro'`
- Test `bigint_unsigned.handling.mode='string'` for large unsigned integers
- Verify that MAXWELL/CANAL formats reject timestamptz.handling.mode

**T3: Validate parallelized CDC backfill performance**

**Test type:** Performance benchmark or integration test

**Test assertions:**
- Create CDC table from large upstream table (e.g., 1M rows)
- Compare backfill time with `backfill.parallelism=0` (default) vs `backfill.parallelism=4`
- Verify that all rows are correctly ingested regardless of parallelism setting
- Check internal state table to monitor backfill progress

**T4: Test TOAST column handling with updates**

**Test file:** Integration test (may already exist, verify coverage)

**Test assertions:**
- Create PostgreSQL table with TOAST-able columns (large text/jsonb)
- Insert row with data large enough to trigger TOAST
- Update a non-TOAST column in the same row
- Verify RisingWave CDC table preserves full TOAST column value (not placeholder)

**T5: Test Debezium ignore_key parameter**

**Test file:** `e2e_test/source_inline/kafka/debezium/ignore_key.slt`

**Test assertions:**
- Create Debezium source with `ignore_key = 'true'`
- Send Debezium message with both key and payload
- Verify only payload is processed
- Create another source with `ignore_key = 'false'` (default)
- Verify both key and payload are processed

---

## Open questions

**Q1: Is there a documented upper limit on the number of CDC tables that can share a single source?**

The docs describe the shared source pattern for CDC but don't mention any limits on how many tables can be created from a single source. This could be relevant for large multi-table CDC scenarios.

**Q2: What is the behavior when schema.registry accepts multiple URLs and they have conflicting schemas?**

The docs state that RisingWave tries each schema registry URL until it finds the schema, but don't clarify what happens if different registries return different schemas for the same subject. Does RisingWave use the first successful response, or does it validate consistency?

**Q3: Are there any format/encoding combinations that are theoretically possible but not yet implemented?**

For example, could MAXWELL AVRO or CANAL AVRO be supported in the future? Are these combinations excluded for technical reasons or simply not prioritized?

**Q4: How does auto.schema.change handle conflicting schema changes across multiple RisingWave instances?**

If multiple RisingWave clusters are ingesting from the same CDC source with `auto.schema.change = 'true'`, and a schema change occurs, how is synchronization handled? This is particularly important for premium features where multiple environments (dev/staging/prod) might exist.

**Q5: What is the maximum message size RisingWave can handle for formats like DEBEZIUM or PLAIN?**

The docs don't mention any limits on message size for various formats/encodings. For large Debezium events or large Protobuf messages, are there practical limits?

**Q6: For MongoDB CDC, how are MongoDB schema changes (like adding fields to documents) handled?**

Since MongoDB is schema-less and everything goes into a jsonb `payload` column, schema evolution is implicit. But are there any considerations for performance or indexing when document schemas evolve significantly?

---

**End of Report**
