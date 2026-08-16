# EDGAR Acquisition & Provenance Design v2

**Date:** 2026-08-15  
**Status:** APPROVED DESIGN / IMPLEMENTATION NOT YET CERTIFIED  
**Repository:** `Tallenholm/special-rotary-phone`  
**Phase-0 framework:** v0.8 re-closed specification  
**Scope:** SEC EDGAR acquisition, provenance, source-version policy, immutable storage, source snapshots, and integrity verification.

## 1. Decision

Build the EDGAR acquisition/provenance layer before expanding into XBRL construction.

The canonical provenance store will use **content-addressed immutable raw objects plus content-addressed immutable acquisition records**. A shared append-only JSONL file or mutable database will **not** be the canonical source of truth. JSONL, SQLite, or Parquet may be built later as disposable derived indexes.

The design separates:

1. network observation facts;
2. parsed filing metadata;
3. downstream derived records; and
4. research dataset/source snapshots.

This separation is mandatory because acquisition history must never be rewritten when parser logic changes.

## 2. Goals

The implementation must make it possible to prove:

- exactly which SEC bytes were used;
- exactly when the collector observed those bytes;
- exactly which SEC resource produced them;
- whether the resource is an archival historical artifact, a revisable snapshot, or discovery/QA-only;
- whether a historical backtest is allowed to treat the resource as point-in-time evidence;
- which parser/transformation version produced each downstream record;
- exactly which immutable source records were frozen into a research dataset; and
- whether any stored object, record, snapshot, or lineage link has been corrupted or lost.

## 3. Non-goals

This slice does **not**:

- parse XBRL facts;
- construct quarterly fundamentals;
- implement 8-K event classifiers;
- implement alpha models or backtests;
- certify historical or prospective performance;
- connect a brokerage account;
- authorize live or automated trading;
- add cryptographic signatures or external timestamp anchoring; or
- treat a derived index as evidence.

Those remain separate gates.

## 4. Architecture

```text
SEC resource
    |
    v
HTTP fetch
    |
    +--> immutable raw content object
    |       sha256(decoded HTTP entity body)
    |
    +--> immutable acquisition record
            sha256(canonical acquisition JSON)
                    |
                    v
             derived FilingRecord
                    |
          Document / Section / XBRL
                    |
                    v
        deterministic SourceSnapshot
                    |
                    v
     experiment-level derived lineage
```

The acquisition layer owns observation provenance. Parsed filing and document fields belong to downstream immutable derived records that reference the exact acquisition and content hashes that produced them.

## 5. Canonical storage layout

```text
data/edgar/
  objects/
    sha256/
      ab/
        abcdef012345...

  acquisitions/
    sha256/
      de/
        def123....json

  snapshots/
    sha256/
      12/
        123456....json

  indexes/
    index.sqlite        # optional, derived, disposable
    acquisitions.parquet # optional, derived, disposable
```

### 5.1 Raw object paths

Raw object paths are generated **only** from a validated SHA-256 digest. SEC filenames, URL basenames, descriptions, `Content-Disposition` filenames, accession text, and other remote strings never determine the filesystem destination.

This prevents path traversal and filename-normalization bugs by construction.

### 5.2 Content collision behavior

If a content-addressed target already exists:

- recompute/verify its SHA-256 and size;
- if they match, treat the write as idempotent;
- if they do not match the address, fail hard with an integrity/collision error.

No existing raw object may be overwritten with different bytes.

## 6. Exact raw-body definition

`content_sha256` hashes the complete HTTP entity body **after HTTP transfer/content decoding performed by the HTTP client and before any HTML, XBRL, text, Unicode, or parser transformation**.

The bytes that are hashed are exactly the bytes persisted in the raw object store and later supplied to parsers.

Response transport metadata such as `Content-Encoding` remains recorded separately.

This definition is intentionally parser-independent and avoids treating gzip transport differences as different logical research payloads when the decoded response body is identical.

## 7. AcquisitionRecord

An acquisition record represents **one successful network observation of a response body**. It records observation facts only.

Conceptual required fields:

```text
schema_version
collector_version
resource_policy
resource_policy_version

request_started_at_utc
response_completed_at_utc

requested_url
final_url
redirect_chain[]
http_method
status_code

request_headers_relevant{}
response_headers_relevant{}

content_sha256
size_bytes
body_representation
```

### 7.1 Relevant request headers

Only headers that can affect representation or provenance may be persisted, for example:

- `User-Agent`;
- `Accept`;
- `Accept-Encoding`;
- `If-None-Match`; and
- `If-Modified-Since`.

Secret/authentication material must never be persisted. SEC acquisition is expected to be unauthenticated.

### 7.2 Relevant response headers

Capture when present:

- `Content-Type`;
- `Content-Encoding`;
- `Content-Length`;
- `ETag`;
- `Last-Modified`; and
- `Date`.

`Date` and `Last-Modified` are source metadata. They do **not** replace collector knowledge time.

### 7.3 Fields explicitly excluded from AcquisitionRecord

The following are parsed or interpreted facts and therefore do **not** belong to the immutable acquisition record:

- CIK;
- accession number;
- form;
- filing date;
- report date;
- acceptance timestamp;
- conservative public timestamp;
- amendment flag;
- primary document;
- filing items;
- SIC;
- ticker; and
- exchange.

They belong in downstream derived records referencing the acquisition source.

## 8. Acquisition identity

The acquisition record's canonical JSON is hashed with SHA-256.

The resulting digest is the record identity:

```text
acquisition_record_sha256
```

The serialized JSON **does not include its own SHA-256 field**. The digest is computed externally and used as the storage address.

This avoids circular hashing.

Two observations of the same response body at different times produce the same `content_sha256` but different acquisition-record hashes because their observation timestamps differ.

## 9. Canonical serialization v1

The project will define one canonical JSON encoding for provenance records.

Allowed value types:

- object;
- array;
- UTF-8 string;
- integer;
- boolean; and
- null.

Floating-point values are forbidden in canonical provenance records.

Canonicalization rules:

- UTF-8 output;
- object keys sorted lexicographically;
- no insignificant whitespace;
- timestamps represented in UTC RFC3339 with fixed microsecond precision and trailing `Z`;
- null values represented explicitly where the schema defines nullable fields;
- array ordering preserved where order is semantic;
- strings are preserved as supplied and are not silently Unicode-normalized; and
- the terminating filesystem newline, if any, is excluded from the record hash.

The canonicalizer itself is versioned and test-covered.

## 10. Time semantics

Three timing concepts must remain separate.

### 10.1 Collector knowledge time

`response_completed_at_utc` is the earliest time the collector can claim to have observed the complete stored payload.

It must:

- be timezone-aware UTC;
- come from an injectable/testable wall-clock source;
- never be backdated from filing metadata; and
- not be replaced by the HTTP `Date` header.

### 10.2 Source-native historical availability

Downstream filing metadata may establish fields such as:

```text
acceptance_datetime
conservative_public_datetime
```

These describe the SEC filing's source-native historical timing, not when this collector downloaded the object.

### 10.3 Derived-feature availability

Later transformations produce their own availability such as `feature_as_of`. They must not inherit an earlier timestamp merely because the raw filing existed earlier.

## 11. No historical backdating

If the collector downloads a 2014 filing in 2026:

```text
response_completed_at_utc = 2026-...
```

must remain true.

A downstream filing record may separately establish that the archived SEC filing was accepted and historically public in 2014.

A revisable API snapshot first captured in 2026 may **not** be projected backward into 2014 unless source-native historical version evidence independently proves the earlier state.

## 12. SEC resource policies

Every successful acquisition receives an explicit, versioned resource policy. The first implementation supports three policies.

### 12.1 `SEC_ARCHIVED_HISTORICAL_ARTIFACT_V1`

For accession-level archived filing material intended to support historical reconstruction.

Examples include accession-level original filing HTML/iXBRL and complete submission artifacts.

Historical eligibility may rely on source-native filing/acceptance metadata derived from the artifact and SEC archive structure, subject to later verification rules.

If the same logical archived artifact is observed with different bytes at different acquisitions, retain both and raise an `unexpected_content_drift` audit finding. Never overwrite or discard either observation.

### 12.2 `SEC_MUTABLE_SNAPSHOT_V1`

For revisable endpoints whose current representation can change over time.

A changed payload is expected version history, not automatically a conflict.

Without source-native historical version evidence, the captured representation is eligible only from collector observation time forward.

### 12.3 `SEC_DISCOVERY_QA_ONLY_V1`

For sources used to locate, reconcile, or QA information but that are not sufficient by themselves to establish historical backtest truth.

A discovery/QA-only record cannot pass a historical PIT gate merely because it contains old dates.

### 12.4 Policy resolution

Resource policy assignment must be deterministic and versioned. Silent caller overrides are not permitted.

If a new SEC endpoint does not match a supported policy rule, acquisition may preserve the bytes but historical research eligibility remains blocked until the policy is explicitly defined.

## 13. Crash-safe commit protocol

A successful acquisition is committed in this order:

1. receive the complete HTTP entity body;
2. compute `content_sha256` and byte size;
3. write the body to a temporary file on the **same filesystem** as the final object path;
4. flush and `fsync` the temporary file;
5. atomically rename/create it at the content-addressed object path;
6. `fsync` the containing directory where supported by the platform;
7. construct and canonicalize the AcquisitionRecord;
8. compute the acquisition-record SHA-256;
9. write the record to a same-filesystem temporary file;
10. flush and `fsync` the temporary record;
11. atomically rename/create it at the acquisition-record path;
12. `fsync` the containing directory where supported by the platform.

### 13.1 Commit point

The successful atomic creation of the final acquisition-record file is the acquisition **commit point**.

### 13.2 Crash invariant

A crash may leave an orphan raw content object, but it must not leave a committed acquisition record referencing absent or non-durable bytes under the supported durability protocol.

### 13.3 Platform durability boundary

If a platform cannot provide directory `fsync` semantics, the implementation must:

- document that limitation explicitly;
- preserve atomic same-filesystem rename semantics;
- provide recovery/integrity verification on restart; and
- avoid claiming a stronger power-loss durability guarantee than the platform can support.

The design does not fabricate filesystem guarantees.

## 14. Concurrency model

No shared append file is canonical, so ingestion workers do not need a global manifest sequence lock.

Independent workers may write different content objects and acquisition records concurrently.

For identical destinations:

- content-addressed writes are idempotent after verification;
- create-if-absent/atomic-rename behavior prevents destructive replacement; and
- an existing destination with unexpected bytes is a fatal integrity error.

## 15. HTTP and transport failure semantics

A successful AcquisitionRecord requires a complete successful response body under the configured success-status policy.

Examples that do **not** create a successful acquisition:

- timeout;
- DNS/connection failure;
- TLS failure;
- incomplete/aborted transfer;
- 404;
- 429; and
- 5xx responses.

A 200 response containing semantically wrong content may still be preserved as an acquisition observation; downstream parsing/validation must reject it as a filing if appropriate.

### 15.1 Coverage auditing

Corpus-building jobs must also produce a durable run-level operational report that enumerates attempted resources and failures. Research coverage must never be inferred solely from the successful acquisitions that happened to exist.

The run report is operational evidence rather than the canonical source-object store. Its exact implementation belongs in the acquisition implementation plan, but omission of failure accounting is not allowed.

## 16. Derived FilingRecord

Parsed filing metadata becomes an immutable derived record, conceptually containing:

```text
schema_version
parser_version
source_acquisition_sha256
source_content_sha256

cik
accession_no
form
filing_date
report_date
acceptance_datetime
conservative_public_datetime
amendment_flag
primary_document
items[]
sic_as_filed
```

The derived record receives its own deterministic record hash using a versioned canonical representation.

If parser v2 corrects parser v1, both records may coexist. The acquisition record is never rewritten.

The same lineage principle continues through Document, Section, XBRL, and feature records.

## 17. SourceSnapshot

A SourceSnapshot freezes the exact immutable source observations selected for a research generation.

Conceptual fields:

```text
schema_version
snapshot_builder_version
created_at_utc
selection_policy
selection_policy_version
eligibility_policy_version
requested_cutoff

selected_sources[]
dataset_digest
```

Each `selected_sources[]` entry records at least:

```text
acquisition_record_sha256
content_sha256
eligibility_basis
eligible_available_at
```

### 17.1 Eligibility basis

The snapshot must distinguish at least:

- `collector_observation` — eligibility begins no earlier than collector knowledge time; and
- `source_native_historical` — eligibility is justified by source-native historical evidence under an archival resource policy.

This prevents one universal `acquired_at <= cutoff` rule from incorrectly rejecting legitimate archived historical filings while also preventing mutable snapshots captured later from being backdated.

### 17.2 Dataset digest

`dataset_digest` hashes the canonical ordered set of selected source identities. Selection ordering must be deterministic.

The digest identifies the actual source corpus, independent of snapshot creation time.

The entire snapshot metadata document also receives its own record hash, so the system can distinguish:

- identical source corpus with different snapshot metadata; from
- genuinely different source data.

### 17.3 No implicit version selection

The snapshot builder must never silently choose "latest", "first", or "most recent" when multiple observations exist.

Version selection is governed by an explicit, versioned selection/eligibility rule. The chosen acquisition identity is recorded.

## 18. Scope of SourceSnapshot reproducibility

A SourceSnapshot freezes **source evidence only**.

It does not by itself reproduce a downstream feature dataset.

Experiment reproducibility must additionally pin downstream parser/extractor/transformation versions and, where applicable, derived-record hashes.

Therefore:

```text
SourceSnapshot + transformation lineage = reproducible derived dataset
```

This boundary is explicit so the project does not falsely treat raw-source freezing as complete model-data reproducibility.

## 19. Derived indexes

Indexes may later be generated as:

- SQLite;
- Parquet;
- JSONL; or
- other query accelerators.

They are disposable.

Deleting and rebuilding an index from the immutable canonical store must not alter provenance results.

No experiment may cite an index row as evidence without resolving it back to canonical acquisition/source identities.

## 20. Integrity verifier

Before a SourceSnapshot can be admitted to a research experiment, the verifier must check at minimum:

1. acquisition-record storage path matches the SHA-256 of canonical record bytes;
2. acquisition schema version is supported;
3. referenced raw object exists;
4. raw object hash equals `content_sha256`;
5. raw object size equals recorded size;
6. timestamps satisfy UTC/timezone rules;
7. URLs are syntactically valid;
8. resource policy/version is recognized;
9. snapshot record references existing acquisitions;
10. selected-source content hashes match their acquisitions;
11. dataset digest recomputes exactly;
12. eligibility basis is valid for the resource policy;
13. downstream lineage references resolve when downstream records are in scope; and
14. no required integrity/audit finding is unresolved.

If a required integrity check fails, the dataset is **not eligible** for research promotion.

## 21. Integrity versus authenticity threat model

SHA-256 content addressing and record verification provide strong integrity and corruption detection within the research environment.

They do **not** prove authenticity against an adversary with enough control to replace every raw object, provenance record, snapshot, and expected hash consistently.

Detached signatures, external hash anchoring, or trusted timestamping are intentionally out of scope for this implementation.

If the threat model later changes, those protections can be added without replacing the content-addressed architecture.

## 22. Recovery behavior

On startup or explicit repair/verify operations, the implementation may discover:

- orphan raw objects;
- orphan temporary files;
- corrupt records;
- records with missing objects; or
- unsupported schema versions.

Required behavior:

- orphan temporary files may be safely removed after proving they are not committed records;
- orphan raw objects may be retained or garbage-collected only under an explicit maintenance command/policy;
- corrupt committed records must not be silently repaired in place;
- missing referenced objects make the acquisition invalid; and
- unsupported schema versions fail closed for research eligibility.

Canonical committed evidence is never mutated as an automatic "repair" operation.

## 23. Mandatory implementation tests

The next implementation PR must add tests covering at least the following invariants.

| Area | Required test/proof |
|---|---|
| Raw CAS | Identical bytes map to one verified content object |
| Repeat observation | Same bytes acquired at different times produce distinct acquisition observations |
| Mutable endpoint | Changed payload is retained as a normal new version |
| Archived artifact | Changed payload is retained and flagged for unexpected drift |
| Content collision | Existing wrong bytes at an addressed path fail hard |
| Crash before record commit | At worst a harmless orphan payload remains |
| Crash after record commit | Acquisition and referenced payload verify |
| Same-filesystem atomicity | Temporary/final path strategy enforces same-filesystem rename |
| Directory durability | Supported-platform directory `fsync` is exercised; unsupported limitation is explicit |
| Concurrency | Parallel writers cannot corrupt or destructively replace canonical records |
| Canonicalization | Equivalent allowed records produce identical canonical bytes/hashes |
| Canonical type gate | Floats/unsupported types are rejected |
| UTC enforcement | Naive or non-UTC canonical acquisition timestamps are rejected |
| Raw corruption | Modified object bytes are detected |
| Record corruption | Modified acquisition JSON is detected |
| Bad remote filename | Cannot influence filesystem destination |
| Mutable PIT rule | Later-captured mutable snapshot cannot pass an earlier historical eligibility cutoff |
| Archived PIT rule | Source-native archival evidence can retain separate historical public timing |
| Snapshot determinism | Same selected source set under same policy yields same dataset digest |
| Snapshot change | Changed selected source set changes dataset digest |
| Snapshot missing ref | Verification fails closed |
| Explicit version choice | Multiple source observations cannot be selected without a defined rule |
| Parser upgrade | New derived parser record does not alter acquisition history |
| HTTP failure | Non-success/transport failure does not create a successful acquisition |
| Coverage accounting | Run-level failures are durably visible rather than silently disappearing |
| Regression | All pre-existing EDGAR tests remain passing |

The previously executed EDGAR suite remains a regression requirement; new tests supplement rather than replace existing coverage.

## 24. Implementation acceptance criteria

This design slice may be called **implementation-certified** only when:

1. all existing EDGAR tests still pass;
2. the mandatory provenance tests above pass;
3. implementation behavior matches the commit/durability semantics without overstating platform guarantees;
4. immutable acquisition facts remain separated from parsed filing facts;
5. source policy and PIT eligibility rules are explicit and fail closed;
6. corruption/missing-lineage verification prevents research eligibility;
7. run-level failures are auditable;
8. no canonical store depends on a mutable shared JSONL/SQLite index; and
9. code review finds no unresolved material deviation from this specification.

Passing this gate certifies only the acquisition/provenance implementation. It does not certify XBRL construction, alpha, backtests, prospective performance, or deployment.

## 25. Next engineering sequence after this gate

Once this design is implemented and its tests pass, proceed to the XBRL controls in this order:

1. XBRL context/duration integrity and safe quarter derivation;
2. specialized issuer accounting schemas/exclusions;
3. share-class/dimensional share-count handling; and
4. Item 4.02 non-reliance invalidation state.

Each downstream component must preserve the source and transformation lineage established by this acquisition/provenance layer.

## 26. Final design disposition

**EDGAR Acquisition & Provenance Design v2: APPROVED — 10/10 for currently known design-level risks.**

**Implementation status: NOT YET CERTIFIED.**

The design explicitly resolves the previously identified weaknesses:

- mixed raw/parsed state -> separated immutable layers;
- canonical JSONL concurrency -> eliminated by content-addressed records;
- false two-file atomicity -> explicit commit protocol and recovery invariant;
- incomplete crash durability -> directory durability semantics included;
- silent overwrites -> prohibited by content addressing and verification;
- mutable-resource ambiguity -> explicit source policy;
- historical snapshot backdating -> policy-aware PIT eligibility;
- path traversal -> remote names never control storage paths;
- parser revisions -> independent immutable derived records;
- snapshot nondeterminism -> deterministic source digest;
- raw snapshot overclaim -> source snapshot explicitly separated from transformation reproducibility;
- silent ingestion failure -> run-level coverage accounting required;
- provenance corruption -> integrity verifier gate; and
- integrity/authenticity confusion -> threat model explicitly bounded.
