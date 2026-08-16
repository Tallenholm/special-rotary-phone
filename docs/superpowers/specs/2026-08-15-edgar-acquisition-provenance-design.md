# EDGAR Acquisition & Provenance Design v2

**Date:** 2026-08-15  
**Status:** APPROVED DESIGN / IMPLEMENTATION NOT YET CERTIFIED  
**Repository:** `Tallenholm/special-rotary-phone`  
**Phase-0 framework:** v0.8 re-closed specification  
**Scope:** SEC EDGAR acquisition, provenance, source-version policy, immutable storage, source snapshots, run-level coverage evidence, and integrity verification.

## 1. Decision

Build the EDGAR acquisition/provenance layer before expanding into XBRL construction.

The canonical provenance store will use **content-addressed immutable raw objects plus content-addressed immutable acquisition, run, and snapshot records**. A shared append-only JSONL file or mutable database will **not** be the canonical source of truth. JSONL, SQLite, or Parquet may be built later as disposable derived indexes.

The design separates:

1. network observation facts;
2. parsed filing metadata;
3. downstream derived records;
4. run-level coverage/failure evidence; and
5. research source snapshots.

Acquisition history must never be rewritten when parser logic changes.

## 2. Goals

The implementation must make it possible to prove:

- exactly which SEC bytes were used;
- exactly when the collector observed those bytes;
- exactly which SEC resource produced them;
- whether that resource is archival, mutable, discovery-only, or unclassified;
- whether a historical backtest may treat the resource as point-in-time evidence;
- which parser/transformation version produced each downstream record;
- exactly which source observations were frozen into a research dataset;
- which planned resources failed to ingest rather than silently disappearing; and
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
    +--> immutable AcquisitionRecord
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
          experiment transformation lineage

Corpus ingestion run
    |
    +--> immutable RunRecord
           planned targets + attempts + successes + failures
```

The acquisition layer owns observation provenance. Parsed filing and document facts belong to downstream immutable records that reference the exact acquisition/content hashes that produced them.

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

  runs/
    sha256/
      45/
        456789....json

  snapshots/
    sha256/
      12/
        123456....json

  indexes/
    index.sqlite          # optional, derived, disposable
    acquisitions.parquet  # optional, derived, disposable
```

### 5.1 Raw object paths

Raw object paths are generated **only** from a validated SHA-256 digest. SEC filenames, URL basenames, descriptions, `Content-Disposition` filenames, accession text, and other remote strings never determine the filesystem destination.

This prevents path traversal and filename-normalization bugs by construction.

### 5.2 Existing-address behavior

If a content-addressed target already exists:

- recompute/verify its SHA-256 and size;
- if they match, treat the write as idempotent;
- if they do not match the address, fail hard with an integrity/collision error.

No canonical object or record may be overwritten with different bytes.

## 6. Exact raw-body definition

`content_sha256` hashes the complete HTTP entity body **after HTTP transfer/content decoding performed by the HTTP client and before any HTML, XBRL, text, Unicode, or parser transformation**.

The bytes hashed are exactly the bytes persisted in the raw object store and later supplied to parsers.

Transport metadata such as `Content-Encoding` is recorded separately.

## 7. Resource identity

Every acquisition contains a deterministic `resource_key` used to group observations of the same logical HTTP resource.

For `resource_key_v1`:

- begin from the final URL after redirects;
- remove any URL fragment;
- lowercase scheme and hostname;
- remove the default port for the scheme;
- preserve path and query string exactly as represented by the final resolved URL; and
- do not infer CIK, accession, form, or filing metadata into the key.

This key identifies an HTTP resource, not an issuer or filing entity. Parsed filing identity remains downstream.

## 8. AcquisitionRecord

An AcquisitionRecord represents **one successful network observation of a complete response body** and records observation facts only.

Required conceptual fields:

```text
schema_version
canonicalizer_version
collector_version
resource_key
resource_key_version
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

### 8.1 Collector version

`collector_version` must identify the executable acquisition implementation sufficiently to reproduce behavior, using the package/version identifier plus repository commit SHA when available.

### 8.2 Relevant request headers

Persist only headers that materially identify the representation request and are safe to retain:

- `User-Agent`;
- `Accept`; and
- `Accept-Encoding`.

Secret/authentication material must never be persisted.

### 8.3 Conditional GET rule

Canonical acquisition v1 does **not** use `If-None-Match` or `If-Modified-Since`.

A `304 Not Modified` contains no new response body and therefore cannot create a successful AcquisitionRecord under v1. If encountered, it is recorded as a run-level operational outcome and does not establish a new canonical source observation.

This avoids falsely treating a bodyless validator response as an independently captured payload. Conditional-validation provenance may be designed later if needed.

### 8.4 Relevant response headers

Capture when present:

- `Content-Type`;
- `Content-Encoding`;
- `Content-Length`;
- `ETag`;
- `Last-Modified`; and
- `Date`.

`Date` and `Last-Modified` are source metadata. They do **not** replace collector knowledge time.

### 8.5 Fields explicitly excluded from AcquisitionRecord

The following are parsed or interpreted facts and do **not** belong to the immutable acquisition record:

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

## 9. Acquisition identity

The canonical AcquisitionRecord JSON is hashed with SHA-256. The resulting digest is the record identity:

```text
acquisition_record_sha256
```

The serialized JSON does **not** include its own digest. The digest is computed externally and used as the storage address.

Two observations of the same response body at different times produce the same `content_sha256` but different acquisition-record hashes because their observation timestamps differ.

## 10. Canonical JSON v1

Canonical provenance records use one project-defined Python JSON encoding contract.

Before serialization, the value tree is validated to contain only:

- `dict[str, allowed_value]`;
- arrays/lists;
- strings;
- integers;
- booleans; and
- null/`None`.

Floating-point values and non-string object keys are rejected.

Canonical bytes are exactly:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Additional schema rules:

- timestamps are pre-normalized to UTC RFC3339 with exactly six fractional digits and trailing `Z`;
- null values are explicitly present when the schema requires nullable fields;
- list order is preserved where order is semantic;
- strings are not silently Unicode-normalized; and
- any optional filesystem newline is outside the canonical bytes and outside the digest.

`canonicalizer_version` is mandatory so any future encoding change cannot silently alter identity semantics.

## 11. Time semantics

Three timing concepts remain separate.

### 11.1 Collector knowledge time

`response_completed_at_utc` is the earliest time the collector can claim to have observed the complete stored payload.

It must:

- be timezone-aware UTC;
- come from an injectable/testable wall-clock source;
- never be backdated from filing metadata; and
- not be replaced by HTTP source headers.

### 11.2 Source-native historical availability

Downstream filing metadata may establish fields such as:

```text
acceptance_datetime
conservative_public_datetime
```

These describe the filing's source-native historical timing, not when this collector downloaded it.

### 11.3 Derived-feature availability

Later transformations produce their own availability such as `feature_as_of`. They must not inherit an earlier timestamp merely because the raw filing existed earlier.

## 12. No historical backdating

If the collector downloads a 2014 filing in 2026:

```text
response_completed_at_utc = 2026-...
```

remains true.

A downstream filing record may separately establish that the archived SEC filing was accepted and historically public in 2014.

A revisable API snapshot first captured in 2026 may **not** be projected backward into 2014 unless source-native historical version evidence independently proves the earlier state.

## 13. SEC resource policies

Every acquisition receives an explicit versioned policy determined from the resource resolver.

### 13.1 `SEC_ARCHIVED_HISTORICAL_ARTIFACT_V1`

For accession-level archived filing material intended to support historical reconstruction, including original filing HTML/iXBRL and complete submission artifacts.

Historical eligibility may rely on source-native filing/acceptance evidence under the applicable downstream verification rule.

If the same `resource_key` later yields different bytes, retain both observations and raise an `unexpected_content_drift` audit finding. Never overwrite or discard either observation.

### 13.2 `SEC_MUTABLE_SNAPSHOT_V1`

For revisable endpoints whose current representation changes over time.

Different payloads across observations are expected version history rather than an automatic conflict.

Absent source-native historical version evidence, a captured representation is eligible only from collector observation time forward.

### 13.3 `SEC_DISCOVERY_QA_ONLY_V1`

For sources used to locate, reconcile, or QA information but that are insufficient by themselves to establish historical backtest truth.

Old dates inside the payload do not make the resource historically eligible.

### 13.4 `SEC_UNCLASSIFIED_V1`

For an SEC resource not matched by a supported policy resolver.

The bytes may be preserved, but the record is **ineligible for research promotion** until a reviewed policy version explicitly classifies it.

### 13.5 Policy resolution

Policy assignment must be deterministic and versioned. Silent caller overrides are forbidden.

A resolver change requires a new policy/resolver version; existing acquisition records are never rewritten.

## 14. Crash-safe commit protocol

A successful acquisition commits in this order:

1. receive the complete HTTP entity body;
2. compute `content_sha256` and byte size;
3. write the body to a temporary file on the **same filesystem** as the final object path;
4. flush and `fsync` the temporary file;
5. atomically create/rename it at the content-addressed object path without destructive replacement;
6. `fsync` the containing directory where supported;
7. construct and canonicalize the AcquisitionRecord;
8. compute the acquisition-record SHA-256;
9. write the record to a same-filesystem temporary file;
10. flush and `fsync` the temporary record;
11. atomically create/rename it at the acquisition-record path without destructive replacement; and
12. `fsync` the containing directory where supported.

### 14.1 Commit point

The successful atomic creation of the final acquisition-record file is the acquisition **commit point**.

### 14.2 Crash invariant

A crash may leave an orphan raw content object, but it must not leave a committed acquisition record referencing absent bytes under the supported durability protocol.

### 14.3 Platform durability boundary

If a platform cannot provide directory `fsync` semantics, the implementation must:

- document that limitation;
- preserve same-filesystem atomic rename/create behavior;
- run recovery/integrity verification on restart; and
- avoid claiming a stronger power-loss durability guarantee than the platform supports.

## 15. Concurrency model

No shared append file is canonical, so ingestion workers need no global manifest sequence lock.

Independent workers may write different content objects and acquisition records concurrently.

For identical destinations:

- content-addressed writes are idempotent after verification;
- create-if-absent/atomic-rename semantics prevent destructive replacement; and
- an existing destination with unexpected bytes is a fatal integrity error.

## 16. HTTP and transport failure semantics

A successful AcquisitionRecord requires a complete response body with final HTTP status in the configured successful 2xx range.

These do **not** create a successful AcquisitionRecord:

- timeout;
- DNS/connection failure;
- TLS failure;
- incomplete/aborted transfer;
- 304;
- 404;
- 429; and
- 5xx responses.

A 2xx response containing semantically wrong content may still be preserved as an acquisition observation; downstream parsing/validation rejects it as a filing if appropriate.

## 17. RunRecord and coverage auditing

Every corpus-building run produces one immutable content-addressed RunRecord. Research coverage must never be inferred solely from successful acquisitions.

Required conceptual fields:

```text
schema_version
canonicalizer_version
collector_version
run_started_at_utc
run_completed_at_utc

planned_targets[]
attempts[]

planned_target_count
successful_target_count
failed_target_count
```

Each `planned_targets[]` entry contains:

```text
requested_url
resource_key_or_null
resource_policy
resource_policy_version
```

Each `attempts[]` entry contains:

```text
requested_url
attempt_started_at_utc
attempt_completed_at_utc
outcome
status_code_or_null
error_class_or_null
acquisition_record_sha256_or_null
```

Allowed `outcome` values are versioned and include at least:

```text
success
http_error
transport_error
incomplete_transfer
not_modified_304
```

The RunRecord's canonical JSON is hashed and stored under `runs/sha256/`. It does not mutate the acquisition store and does not convert a failed request into source evidence.

Retries are represented as multiple ordered attempt entries, so a terminal success cannot erase earlier failures.

## 18. Derived FilingRecord

Parsed filing metadata becomes an immutable derived record containing conceptually:

```text
schema_version
canonicalizer_version
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

The derived record receives its own deterministic hash.

If parser v2 corrects parser v1, both may coexist. The acquisition record is never rewritten.

The same lineage principle continues through Document, Section, XBRL, and feature records.

## 19. SourceSnapshot

A SourceSnapshot freezes the exact immutable source observations selected for a research generation.

Required conceptual fields:

```text
schema_version
canonicalizer_version
snapshot_builder_version
created_at_utc
selection_policy
selection_policy_version
eligibility_policy_version
requested_cutoff

selected_sources[]
dataset_digest
```

Each selected source contains:

```text
acquisition_record_sha256
content_sha256
eligibility_basis
eligible_available_at
```

### 19.1 Eligibility basis

The snapshot supports at least:

- `collector_observation` — eligibility begins no earlier than collector knowledge time; and
- `source_native_historical` — eligibility is justified by source-native historical evidence under an archival policy.

This prevents one universal acquisition-time rule from rejecting legitimate archived filings while also preventing later mutable snapshots from being backdated.

### 19.2 Dataset digest

`dataset_digest_v1` is the SHA-256 of canonical JSON for the lexicographically sorted list of selected `acquisition_record_sha256` values.

Thus:

- the same exact source observations produce the same dataset digest;
- eligibility/selection metadata changes the snapshot-record hash but not the underlying source-corpus digest; and
- changing any selected acquisition identity changes the dataset digest.

The SourceSnapshot document itself receives its own content-addressed record hash.

### 19.3 No implicit version selection

The snapshot builder never silently chooses "latest", "first", or "most recent" when multiple observations exist.

Version selection is governed by an explicit versioned rule, and the chosen acquisition identity is recorded.

## 20. Scope of SourceSnapshot reproducibility

A SourceSnapshot freezes **source evidence only**. It does not by itself reproduce a downstream feature dataset.

Experiment reproducibility additionally pins parser/extractor/transformation versions and, where applicable, derived-record hashes.

```text
SourceSnapshot + transformation lineage = reproducible derived dataset
```

## 21. Derived indexes

SQLite, Parquet, JSONL, or other query indexes may be generated later for performance.

They are disposable. Deleting and rebuilding an index from the canonical immutable store must not alter provenance results.

No experiment may cite an index row as evidence without resolving it back to canonical acquisition/source identities.

## 22. Integrity verifier

Before a SourceSnapshot enters a research experiment, the verifier checks at minimum:

1. acquisition record parses under a supported schema/canonicalizer version;
2. re-canonicalized acquisition bytes hash to the storage address;
3. referenced raw object exists;
4. raw object hash equals `content_sha256`;
5. raw object size equals recorded size;
6. timestamps satisfy UTC/schema rules;
7. URLs and `resource_key` satisfy resolver rules;
8. resource policy/version is recognized;
9. unclassified resources are rejected for promotion;
10. snapshot references existing acquisitions;
11. selected-source content hashes match their acquisitions;
12. dataset digest recomputes exactly;
13. eligibility basis is valid for the selected resource policy;
14. required archived-resource drift findings are resolved or explicitly blocking;
15. run-level coverage evidence exists when the experiment depends on a planned corpus ingest; and
16. downstream lineage references resolve when downstream records are in scope.

Failure of a required check makes the source dataset **not eligible** for research promotion.

## 23. Integrity versus authenticity threat model

SHA-256 content addressing and record verification provide integrity and corruption detection within the research environment.

They do **not** prove authenticity against an adversary able to replace every raw object, provenance record, snapshot, and expected hash consistently.

Detached signatures, external hash anchoring, and trusted timestamping remain out of scope. They can be added later without replacing this architecture.

## 24. Recovery behavior

On startup or explicit verify/repair operations, the implementation may discover:

- orphan raw objects;
- orphan temporary files;
- corrupt records;
- records with missing objects; or
- unsupported schema versions.

Required behavior:

- orphan temporary files may be removed only after proving they are not committed records;
- orphan raw objects may be retained or garbage-collected only under an explicit maintenance policy;
- corrupt committed records are never silently repaired in place;
- missing referenced objects invalidate the acquisition; and
- unsupported schema/canonicalizer versions fail closed for research eligibility.

Canonical committed evidence is never mutated by automatic repair.

## 25. Mandatory implementation tests

The implementation PR must add tests covering at least these invariants:

| Area | Required test/proof |
|---|---|
| Raw CAS | Identical bytes map to one verified content object |
| Repeat observation | Same bytes at different times produce distinct acquisition observations |
| Resource key | Equivalent normalized final URLs yield the intended deterministic key |
| Mutable endpoint | Changed payload is retained as normal version history |
| Archived artifact | Changed payload is retained and flagged for unexpected drift |
| Unclassified resource | Preserved but rejected for research promotion |
| Content collision | Existing wrong bytes at addressed path fail hard |
| Crash before record commit | At worst a harmless orphan payload remains |
| Crash after record commit | Acquisition and referenced payload verify |
| Same-filesystem atomicity | Temp/final path strategy enforces same-filesystem operation |
| Directory durability | Supported-platform directory `fsync` is exercised; unsupported limit is explicit |
| Concurrency | Parallel writers cannot corrupt or destructively replace canonical records |
| Canonicalization | Equivalent allowed records produce identical canonical bytes/hashes |
| Canonical type gate | Floats/non-string keys/unsupported values are rejected |
| UTC enforcement | Naive or malformed canonical timestamps are rejected |
| Raw corruption | Modified object bytes are detected |
| Record corruption | Modified acquisition JSON is detected by recanonicalization/hash |
| Bad remote filename | Cannot influence filesystem destination |
| Conditional GET | 304 never creates a body-backed AcquisitionRecord |
| Mutable PIT rule | Later mutable snapshot cannot pass an earlier historical eligibility cutoff |
| Archived PIT rule | Source-native archival evidence can retain separate historical timing |
| Snapshot determinism | Same selected acquisitions yield same dataset digest |
| Snapshot change | Changed selected acquisition changes dataset digest |
| Snapshot missing ref | Verification fails closed |
| Explicit version choice | Multiple observations cannot be selected without a defined rule |
| Parser upgrade | New derived parser record does not alter acquisition history |
| HTTP failure | Non-success/transport failure does not create a successful acquisition |
| Run coverage | Failed/retried targets remain visible in immutable RunRecord |
| Regression | All pre-existing EDGAR tests remain passing |

The previously executed EDGAR suite remains a regression requirement; new tests supplement rather than replace existing coverage.

## 26. Implementation acceptance criteria

This slice may be called **implementation-certified** only when:

1. all existing EDGAR tests still pass;
2. every mandatory provenance test above passes;
3. implementation matches commit/durability semantics without overstating platform guarantees;
4. immutable observation facts remain separated from parsed filing facts;
5. resource key, policy, and PIT eligibility rules are deterministic and fail closed;
6. corruption or missing lineage blocks research eligibility;
7. run-level failures/retries are auditable;
8. no canonical store depends on mutable shared JSONL/SQLite state; and
9. code review finds no unresolved material deviation from this specification.

Passing this gate certifies only the acquisition/provenance implementation. It does not certify XBRL construction, alpha, backtests, prospective performance, or deployment.

## 27. Next engineering sequence

After this design is implemented and its tests pass, proceed to:

1. XBRL context/duration integrity and safe quarter derivation;
2. specialized issuer accounting schemas/exclusions;
3. share-class/dimensional share-count handling; and
4. Item 4.02 non-reliance invalidation state.

Each downstream component must preserve the source and transformation lineage established here.

## 28. Final design disposition

**EDGAR Acquisition & Provenance Design v2: APPROVED — 10/10 for currently known design-level risks.**

**Implementation status: NOT YET CERTIFIED.**

This specification explicitly resolves the known design weaknesses:

- mixed raw/parsed state -> separated immutable layers;
- canonical JSONL concurrency -> eliminated by content-addressed records;
- false two-file atomicity -> explicit commit protocol and recovery invariant;
- incomplete crash durability -> directory durability semantics included;
- ambiguous canonical hashing -> exact canonical JSON v1 contract;
- ambiguous logical-resource grouping -> deterministic `resource_key`;
- conditional 304 ambiguity -> bodyless validation responses cannot masquerade as acquisitions;
- silent overwrites -> prohibited by content addressing and verification;
- mutable-resource ambiguity -> explicit resource policies;
- unknown-resource ambiguity -> fail-closed unclassified policy;
- historical snapshot backdating -> policy-aware PIT eligibility;
- path traversal -> remote names never control storage paths;
- parser revisions -> independent immutable derived records;
- snapshot nondeterminism -> exact dataset-digest rule;
- raw snapshot overclaim -> source snapshot separated from transformation reproducibility;
- silent ingestion failure/retry -> immutable run-level coverage evidence;
- provenance corruption -> integrity verifier gate; and
- integrity/authenticity confusion -> threat model explicitly bounded.
