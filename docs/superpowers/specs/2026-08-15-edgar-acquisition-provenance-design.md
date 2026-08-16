# EDGAR Acquisition & Provenance Design v2

**Date:** 2026-08-15  
**Status:** APPROVED DESIGN / IMPLEMENTATION NOT YET CERTIFIED  
**Repository:** `Tallenholm/special-rotary-phone`  
**Phase-0 framework:** v0.8 re-closed specification  
**Scope:** SEC EDGAR acquisition, provenance, source-version policy, immutable storage, source snapshots, run-level coverage evidence, and integrity verification.

## 1. Decision

Build the EDGAR acquisition/provenance layer before expanding into XBRL construction.

The canonical provenance store uses **content-addressed immutable raw objects plus content-addressed immutable acquisition, run, and snapshot records**. Shared JSONL files and mutable databases are not canonical evidence. JSONL, SQLite, or Parquet may later be generated as disposable indexes.

The design separates:

1. network observation facts;
2. parsed filing metadata;
3. downstream derived records;
4. run-level coverage/failure evidence; and
5. research source snapshots.

Acquisition history is never rewritten when parser logic changes.

## 2. Goals

The implementation must make it possible to prove:

- exactly which SEC bytes were used;
- exactly when the collector observed those bytes;
- exactly which HTTP resource produced them;
- whether the resource is archival, mutable, discovery-only, or unclassified;
- whether a historical backtest may treat it as point-in-time evidence;
- which parser/transformation version produced each downstream record;
- exactly which source observations were frozen into a research dataset;
- which planned resources failed or retried rather than silently disappearing; and
- whether any object, record, snapshot, or lineage link has been corrupted or lost.

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
HTTP GET -> final HTTP 200
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
           planned targets + ordered attempts + successes + failures
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

Raw object paths are generated only from a validated SHA-256 digest. SEC filenames, URL basenames, descriptions, `Content-Disposition` filenames, accession text, and other remote strings never determine filesystem destinations.

### 5.2 Existing-address behavior

If a content-addressed target already exists:

- recompute/verify its SHA-256 and size;
- if they match, treat the write as idempotent;
- if they do not match the address, fail hard with an integrity/collision error.

No canonical object or record may be overwritten with different bytes.

## 6. Exact raw-body definition

`content_sha256` hashes the complete HTTP entity body **after HTTP transfer/content decoding performed by the HTTP client and before any HTML, XBRL, text, Unicode, or parser transformation**.

The bytes hashed are exactly the bytes persisted in the raw object store and later supplied to parsers. Transport metadata such as `Content-Encoding` is recorded separately.

For acquisition schema v1, `body_representation` is the literal constant:

```text
decoded_http_entity_body_v1
```

A different representation requires a new schema/policy version; it cannot silently reuse this label.

## 7. Resource identity

Every acquisition contains a deterministic `resource_key` used to group observations of the same logical HTTP resource.

For `resource_key_v1`:

- begin from the final URL after redirects;
- remove any URL fragment;
- lowercase scheme and hostname;
- remove the default port for the scheme;
- preserve path and query string exactly as represented by the final resolved URL; and
- do not infer CIK, accession, form, or filing metadata into the key.

The key identifies an HTTP resource, not an issuer or filing entity.

## 8. AcquisitionRecord

An AcquisitionRecord represents **one successful network observation of a complete HTTP 200 response body** and records observation facts only.

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

`collector_version` identifies the acquisition implementation sufficiently to reproduce behavior, using the package/version identifier plus repository commit SHA when available.

### 8.2 Redirect chain

Each redirect hop is represented in observed order as:

```text
url
status_code
location_or_null
```

The final 200 response is represented by `final_url`/`status_code`, not duplicated as a redirect hop.

### 8.3 Relevant headers

Persist only safe representation/provenance headers.

Request headers:

- `user-agent`;
- `accept`; and
- `accept-encoding`.

Response headers when present:

- `content-type`;
- `content-encoding`;
- `content-length`;
- `etag`;
- `last-modified`; and
- `date`.

Selected header names are stored lowercase. Values are the HTTP client's normalized field values with leading/trailing optional whitespace removed; internal value content is otherwise preserved. Secret/authentication material is never persisted.

`date` and `last-modified` are source metadata and do not replace collector knowledge time.

### 8.4 Conditional GET rule

Canonical acquisition v1 does **not** send `If-None-Match` or `If-Modified-Since`.

A `304 Not Modified` contains no new response body and cannot create a successful AcquisitionRecord. If encountered, it is a run-level operational outcome only.

Conditional-validation provenance requires a future reviewed design rather than silently reusing prior bytes.

### 8.5 Fields excluded from AcquisitionRecord

Parsed/interpreted fields do not belong here, including CIK, accession number, form, filing/report dates, acceptance/public timestamps, amendment flag, primary document, filing items, SIC, ticker, and exchange.

They belong in downstream derived records referencing the acquisition source.

## 9. Acquisition identity

The canonical AcquisitionRecord JSON is hashed with SHA-256. The digest is the record identity:

```text
acquisition_record_sha256
```

The serialized JSON does not contain its own digest. Two observations of identical body bytes at different times share `content_sha256` but have different acquisition-record hashes because observation timestamps differ.

## 10. Canonical JSON v1

Before serialization, provenance data is validated to contain only:

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
- schema-required nullable fields are explicitly present as null;
- list order is preserved where order is semantic;
- strings are not silently Unicode-normalized; and
- an optional filesystem newline is outside canonical bytes and outside the digest.

`canonicalizer_version` is mandatory so future encoding changes cannot silently alter identity semantics.

## 11. Time semantics

### 11.1 Collector knowledge time

`response_completed_at_utc` is the earliest time the collector may claim to have observed the complete stored payload.

It must be timezone-aware UTC, come from an injectable/testable wall clock, never be backdated from filing metadata, and never be replaced by HTTP source headers.

### 11.2 Source-native historical availability

Downstream filing metadata may establish:

```text
acceptance_datetime
conservative_public_datetime
```

These describe historical SEC availability, not collector acquisition time.

### 11.3 Derived-feature availability

Later transformations produce their own `feature_as_of`/availability. A derived feature cannot inherit an earlier timestamp merely because the raw filing existed earlier.

## 12. No historical backdating

If the collector downloads a 2014 filing in 2026, its `response_completed_at_utc` remains in 2026.

A downstream verified FilingRecord may separately establish that an archived SEC filing was historically public in 2014.

A mutable API snapshot first captured in 2026 may not be projected backward into 2014.

## 13. SEC resource policies

Every acquisition receives an explicit versioned policy from a deterministic resolver.

### 13.1 `SEC_ARCHIVED_HISTORICAL_ARTIFACT_V1`

For accession-level archived filing material intended to support historical reconstruction, including original filing HTML/iXBRL and complete submission artifacts.

If the same `resource_key` later yields different bytes, retain both and raise `unexpected_content_drift`. Never overwrite or discard either observation.

### 13.2 `SEC_MUTABLE_SNAPSHOT_V1`

For revisable endpoints whose current representation may change. Different payloads across observations are expected version history.

Under v1, these resources are eligible only from collector observation time forward.

### 13.3 `SEC_DISCOVERY_QA_ONLY_V1`

For sources used to locate, reconcile, or QA information but insufficient by themselves to establish historical research truth.

They may be stored and used for diagnostics but cannot be selected as promotable research source evidence.

### 13.4 `SEC_UNCLASSIFIED_V1`

For a resource not matched by a supported resolver.

Bytes may be preserved, but the record is ineligible for research promotion until a reviewed future policy version classifies it.

### 13.5 Policy resolution

Policy assignment is deterministic and versioned. Silent caller overrides are forbidden. Resolver changes create new policy/resolver versions; existing acquisitions are never rewritten.

## 14. Crash-safe commit protocol

A successful acquisition commits in this order:

1. receive the complete HTTP 200 entity body;
2. compute `content_sha256` and byte size;
3. write the body to a temporary file on the same filesystem as the final object path;
4. flush and `fsync` the temporary file;
5. atomically create/rename it at the content-addressed path without destructive replacement;
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

A crash may leave an orphan raw object, but it must not leave a committed acquisition record referencing absent bytes under the supported durability protocol.

### 14.3 Platform durability boundary

If directory `fsync` is unavailable, the implementation documents the limitation, retains same-filesystem atomic rename/create behavior, verifies integrity on restart, and does not claim stronger power-loss durability than the platform supports.

## 15. Concurrency model

No shared append file is canonical, so workers need no global manifest sequence lock.

Independent workers may write concurrently. Identical destinations are idempotent after verification; destructive replacement is forbidden; unexpected existing bytes are a fatal integrity error.

## 16. HTTP and transport failure semantics

Canonical acquisition v1 supports **HTTP GET only** and requires a final **HTTP 200** with a complete body.

These do not create successful AcquisitionRecords:

- timeout;
- DNS/connection/TLS failure;
- incomplete/aborted transfer;
- 204;
- 206 unless a future range-acquisition design explicitly authorizes it;
- 304;
- 4xx; and
- 5xx responses.

Redirects may be followed; only the final HTTP 200 body is committed.

A 200 containing semantically wrong content may still be preserved as an observation. Downstream parsing/validation rejects it as a filing where appropriate.

## 17. RunRecord and coverage auditing

Every corpus-building run produces one immutable content-addressed RunRecord. Coverage is never inferred solely from successful acquisitions.

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

Each planned target contains only facts knowable before the request:

```text
target_index
requested_url
planned_policy
planned_policy_version
```

`target_index` is a zero-based integer unique within the RunRecord and stable for that planned target. It disambiguates retries and duplicate requested URLs.

A planned target does not contain final `resource_key`, because that key depends on the final URL after redirects.

Each ordered attempt contains:

```text
target_index
attempt_index_for_target
requested_url
attempt_started_at_utc
attempt_completed_at_utc
outcome
status_code_or_null
error_class_or_null
acquisition_record_sha256_or_null
```

`attempt_index_for_target` is zero-based and strictly increasing within each target.

Versioned outcomes include at least:

```text
success
http_error
transport_error
incomplete_transfer
not_modified_304
```

The RunRecord canonical JSON is hashed and stored under `runs/sha256/`. Retries appear as multiple ordered attempts so later success cannot erase earlier failure evidence.

Counts are derived by terminal target state, not raw attempt count:

- `planned_target_count = len(planned_targets)`;
- `successful_target_count` counts targets whose final attempt is `success`;
- `failed_target_count = planned_target_count - successful_target_count`.

`planned_policy` is a planning classification based on the requested URL. The committed AcquisitionRecord's actual policy is independently resolved from final resource identity and is authoritative for source eligibility.

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

The derived record receives its own deterministic hash. Parser v2 may coexist with parser v1; acquisition history is never rewritten.

The same lineage rule continues through Document, Section, XBRL, and feature records.

## 19. SourceSnapshot

A SourceSnapshot freezes exact immutable source observations for a research generation.

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

Every selected source must satisfy:

```text
eligible_available_at <= requested_cutoff
```

under the snapshot's versioned eligibility policy. Selection code must not use information with availability after `requested_cutoff` to choose among otherwise eligible versions.

### 19.1 Exact eligibility rules v1

`collector_observation`:

- allowed for `SEC_ARCHIVED_HISTORICAL_ARTIFACT_V1` and `SEC_MUTABLE_SNAPSHOT_V1`;
- `eligible_available_at = response_completed_at_utc`.

`source_native_historical`:

- allowed only for `SEC_ARCHIVED_HISTORICAL_ARTIFACT_V1` under v1;
- requires a derived FilingRecord sourced from the same acquisition/content;
- requires verified accession/form identity and a valid `conservative_public_datetime`;
- requires no unresolved `unexpected_content_drift` affecting the chosen logical artifact; and
- `eligible_available_at = conservative_public_datetime`.

`SEC_MUTABLE_SNAPSHOT_V1` may not use `source_native_historical` under v1. A future policy may add that capability only with explicit source-native version-history evidence.

`SEC_DISCOVERY_QA_ONLY_V1` and `SEC_UNCLASSIFIED_V1` cannot be selected into a promotable research SourceSnapshot.

### 19.2 Dataset digest

`dataset_digest_v1` is the SHA-256 of canonical JSON for the lexicographically sorted list of selected `acquisition_record_sha256` values.

Thus the same exact source observations produce the same corpus digest. Eligibility/selection metadata changes the SourceSnapshot record hash but not the underlying source-corpus digest. Changing any selected acquisition identity changes the digest.

### 19.3 No implicit version selection

The builder never silently chooses "latest", "first", or "most recent" when multiple observations exist. Selection uses an explicit versioned rule and records the chosen acquisition identity.

## 20. Scope of SourceSnapshot reproducibility

A SourceSnapshot freezes source evidence only. It does not reproduce a downstream feature dataset by itself.

Experiment reproducibility additionally pins parser/extractor/transformation versions and, where applicable, derived-record hashes.

```text
SourceSnapshot + transformation lineage = reproducible derived dataset
```

## 21. Derived indexes

SQLite, Parquet, JSONL, or other query indexes may be generated for performance. They are disposable.

Deleting and rebuilding an index from the immutable canonical store must not alter provenance results. Index rows must resolve back to canonical identities before they can support research evidence.

## 22. Integrity verifier

Before a SourceSnapshot enters a research experiment, the verifier checks at minimum:

1. acquisition record parses under supported schema/canonicalizer versions;
2. re-canonicalized acquisition bytes hash to the storage address;
3. referenced raw object exists;
4. raw object hash equals `content_sha256`;
5. raw object size equals recorded size;
6. `body_representation` is recognized and matches schema expectations;
7. timestamps satisfy UTC/schema rules;
8. final URL and `resource_key` satisfy resolver rules;
9. resource policy/version is recognized;
10. unclassified/discovery-only sources are rejected from promotable snapshots;
11. snapshot references existing acquisitions;
12. selected-source content hashes match acquisitions;
13. every selected source satisfies `eligible_available_at <= requested_cutoff`;
14. dataset digest recomputes exactly;
15. eligibility basis satisfies Section 19.1;
16. required archived-resource drift findings are resolved or blocking;
17. RunRecord coverage evidence exists when the experiment depends on a planned corpus ingest; and
18. downstream lineage references resolve when downstream records are in scope.

Failure of a required check makes the source dataset **not eligible** for research promotion.

## 23. Integrity versus authenticity threat model

SHA-256 content addressing and record verification provide integrity/corruption detection inside the research environment.

They do not prove authenticity against an adversary able to replace every raw object, provenance record, snapshot, and expected hash consistently.

Detached signatures, external anchoring, and trusted timestamping are out of scope and may be added later without replacing this architecture.

## 24. Recovery behavior

Startup or explicit verify/repair operations may discover orphan raw objects, orphan temp files, corrupt records, missing objects, or unsupported schemas.

Required behavior:

- orphan temp files may be removed only after proving they are uncommitted;
- orphan raw objects may be retained or garbage-collected only under explicit maintenance policy;
- corrupt committed records are never silently repaired in place;
- missing referenced objects invalidate the acquisition; and
- unsupported schema/canonicalizer versions fail closed for research eligibility.

Canonical committed evidence is never mutated by automatic repair.

## 25. Mandatory implementation tests

The implementation PR must add tests covering at least:

| Area | Required test/proof |
|---|---|
| Raw CAS | Identical bytes map to one verified object |
| Body representation | Stored bytes/hash match `decoded_http_entity_body_v1` definition |
| Repeat observation | Same bytes at different times produce distinct acquisitions |
| Resource key | Normalization is deterministic and final-URL based |
| Redirects | Hop order preserved; final 200 distinct from redirect chain |
| Mutable endpoint | Changed payload retained as normal version history |
| Archived artifact | Changed payload retained + unexpected-drift finding |
| Unclassified | Preserved but rejected for promotion |
| Discovery-only | Cannot enter promotable SourceSnapshot |
| Content collision | Wrong bytes at addressed path fail hard |
| Crash before commit | At worst a harmless orphan payload remains |
| Crash after commit | Acquisition and payload verify |
| Same-filesystem atomicity | Temp/final strategy enforces same-filesystem operation |
| Directory durability | `fsync` behavior/limitation correctly exercised/documented |
| Concurrency | Parallel writers cannot corrupt/replace canonical records |
| Canonical JSON | Exact v1 encoder produces stable bytes/hash |
| Canonical type gate | Floats/non-string keys/unsupported values rejected |
| UTC enforcement | Naive/malformed canonical timestamps rejected |
| Raw corruption | Modified object bytes detected |
| Record corruption | Modified acquisition JSON detected by recanonicalization/hash |
| Remote filename | Cannot influence filesystem destination |
| GET/200 rule | 204/206/304/4xx/5xx never create AcquisitionRecord |
| Conditional rule | `If-None-Match`/`If-Modified-Since` absent from canonical v1 |
| Mutable PIT | Mutable snapshot cannot backdate before collector observation |
| Archived PIT | Historical eligibility requires same-source FilingRecord + public timestamp + clean drift state |
| Snapshot cutoff | No selected source has `eligible_available_at > requested_cutoff` |
| Snapshot selection leakage | Selection cannot use post-cutoff version information |
| Snapshot determinism | Same selected acquisitions -> same dataset digest |
| Snapshot change | Changed selected acquisition -> changed digest |
| Snapshot missing ref | Verification fails closed |
| Explicit version choice | Multiple observations require defined selection rule |
| Parser upgrade | New derived record does not alter acquisition history |
| HTTP failure | Transport/error response does not create successful acquisition |
| Run target identity | `target_index` disambiguates duplicate requested URLs |
| Run planning | Planned target does not claim final resource key before fetch |
| Run retries | Attempt indices preserve earlier failures after later success |
| Run counts | Success/failure counts derive from terminal target state |
| Regression | All pre-existing EDGAR tests remain passing |

The previously executed EDGAR suite remains a regression requirement; these tests supplement rather than replace it.

## 26. Implementation acceptance criteria

This slice may be called **implementation-certified** only when:

1. all existing EDGAR tests still pass;
2. every mandatory provenance test above passes;
3. implementation matches commit/durability semantics without overstating platform guarantees;
4. immutable observation facts remain separated from parsed filing facts;
5. resource key, policy, and PIT eligibility are deterministic and fail closed;
6. corruption or missing lineage blocks research eligibility;
7. run-level failures/retries are auditable and target identity is unambiguous;
8. no canonical store depends on mutable shared JSONL/SQLite state; and
9. code review finds no unresolved material deviation from this specification.

Passing this gate certifies only acquisition/provenance implementation. It does not certify XBRL construction, alpha, backtests, prospective performance, or deployment.

## 27. Next engineering sequence

After this design is implemented and its tests pass:

1. XBRL context/duration integrity and safe quarter derivation;
2. specialized issuer accounting schemas/exclusions;
3. share-class/dimensional share-count handling; and
4. Item 4.02 non-reliance invalidation state.

Each downstream component preserves the source/transformation lineage established here.

## 28. Final design disposition

**EDGAR Acquisition & Provenance Design v2: APPROVED — 10/10 for currently known design-level risks.**

**Implementation status: NOT YET CERTIFIED.**

Resolved design weaknesses include:

- mixed raw/parsed state -> separated immutable layers;
- canonical JSONL concurrency -> eliminated by content-addressed records;
- false two-file atomicity -> explicit commit protocol/recovery invariant;
- incomplete crash durability -> directory durability boundary;
- ambiguous raw-body semantics -> fixed body representation constant;
- ambiguous canonical hashing -> exact canonical JSON v1;
- logical-resource ambiguity -> deterministic final-URL `resource_key`;
- pre-request/final-resource confusion -> RunRecord planning and acquisition identity separated;
- duplicate-target/retry ambiguity -> stable target and attempt indices;
- HTTP success ambiguity -> GET + final 200 only;
- conditional 304 ambiguity -> bodyless validation cannot masquerade as acquisition;
- silent overwrite -> prohibited by content addressing/verification;
- mutable-resource ambiguity -> explicit resource policies;
- unknown-resource ambiguity -> fail-closed unclassified policy;
- historical snapshot backdating -> exact policy-aware eligibility rules and cutoff invariant;
- path traversal -> remote names never control storage paths;
- parser revisions -> independent immutable derived records;
- snapshot nondeterminism -> exact dataset-digest rule;
- raw snapshot overclaim -> source snapshot separated from transformation reproducibility;
- silent ingestion failure/retry -> immutable run-level coverage evidence;
- provenance corruption -> integrity verifier gate; and
- integrity/authenticity confusion -> bounded threat model.
